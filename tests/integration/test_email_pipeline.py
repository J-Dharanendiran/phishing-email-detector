import math
from email.message import EmailMessage

import pytest

from app.email_parser import parse_email
from app.feature_extractor import EXPECTED_FEATURES, extract_features


def make_email(
    *,
    sender="sender@example.com",
    to="user@gmail.com",
    cc=None,
    bcc=None,
    subject="Test message",
    date="Fri, 30 Oct 2026 10:30:00 +0000",
    body="This is a test email body with enough text for language detection.",
    html=None,
    attachment=None,
):
    message = EmailMessage()
    message["From"] = sender

    if to is not None:
        message["To"] = to
    if cc is not None:
        message["Cc"] = cc
    if bcc is not None:
        message["Bcc"] = bcc
    if subject is not None:
        message["Subject"] = subject
    if date is not None:
        message["Date"] = date

    if html is None:
        message.set_content(body)
    else:
        message.set_content(body)
        message.add_alternative(html, subtype="html")

    if attachment is not None:
        filename, content, maintype, subtype = attachment
        message.add_attachment(
            content,
            maintype=maintype,
            subtype=subtype,
            filename=filename,
        )

    return message.as_bytes()


def parse_and_extract(email_bytes):
    parsed = parse_email(email_bytes)
    return parsed, extract_features(parsed)


def test_exactly_18_features_in_training_order():
    _, features = parse_and_extract(make_email())
    assert len(features) == 18
    assert list(features) == EXPECTED_FEATURES


def test_sender_and_receiver_domains():
    _, features = parse_and_extract(make_email(
        sender="Security Team <alerts@example.com>",
        to="User <user@gmail.com>",
        cc="Admin <admin@yahoo.com>",
    ))
    assert features["sender_domain"] == "example.com"
    assert features["receiver_domain"] == "gmail.com;yahoo.com"
    assert features["receiver_domain_count"] == 2
    assert features["receiver_unique_domain_count"] == 2


def test_duplicate_receiver_domains():
    _, features = parse_and_extract(make_email(
        to="first@gmail.com, second@gmail.com",
        cc="third@yahoo.com",
    ))
    assert features["receiver_domain"] == "gmail.com;gmail.com;yahoo.com"
    assert features["receiver_domain_count"] == 3
    assert features["receiver_unique_domain_count"] == 2


def test_email_without_urls():
    _, features = parse_and_extract(make_email(
        body="This email contains no web addresses."
    ))
    assert features["urls"] == "[NO URL]"
    assert features["url_count"] == 0
    assert features["url_length_max_log"] == 0.0
    assert features["url_length_avg_log"] == 0.0
    assert features["url_subdom_max_log"] == 0.0
    assert features["url_subdom_avg_log"] == 0.0


def test_plain_text_url_extraction():
    _, features = parse_and_extract(make_email(
        body="Please visit https://example.com/login."
    ))
    assert features["urls"] == "https://example.com/login"
    assert features["url_count"] == 1


def test_html_attribute_url_extraction():
    _, features = parse_and_extract(make_email(
        body="Please review this message.",
        html='<html><body><a href="https://example.org/account">Open</a></body></html>',
    ))
    assert "https://example.org/account" in features["urls"]
    assert features["url_count"] == 1


def test_no_attachments():
    _, features = parse_and_extract(make_email())
    assert features["attachment_types"] == "none"
    assert features["attachment_count_log"] == 0.0


def test_pdf_attachment():
    parsed, features = parse_and_extract(make_email(
        attachment=("report.pdf", b"%PDF-1.4 test", "application", "pdf")
    ))
    assert parsed["attachment_count"] == 1
    assert features["attachment_types"] == "application/pdf"
    assert features["attachment_count_log"] == pytest.approx(math.log1p(1))


def test_missing_subject_fallback():
    _, features = parse_and_extract(make_email(subject=None))
    assert features["subject"] == "[NO SUBJECT]"


def test_empty_body_fallback():
    _, features = parse_and_extract(make_email(body=""))
    assert features["body"] == "[NO BODY]"


def test_missing_date():
    _, features = parse_and_extract(make_email(date=None))
    assert features["date_year"] is None
    assert features["date_missing"] == 1


def test_date_normalized_to_utc_before_year_extraction():
    parsed, features = parse_and_extract(make_email(
        date="Thu, 31 Dec 2020 23:30:00 -0200"
    ))
    assert parsed["date"].utcoffset().total_seconds() == 0
    assert features["date_year"] == 2021
    assert features["date_missing"] == 0


def test_plain_text_content_type():
    _, features = parse_and_extract(make_email())
    assert features["content_types"] == "text/plain"


def test_parser_rejects_non_bytes():
    with pytest.raises(TypeError):
        parse_email("From: sender@example.com")


def test_parser_rejects_empty_bytes():
    with pytest.raises(ValueError):
        parse_email(b"")


def test_missing_receiver_information():
    _, features = parse_and_extract(make_email(to=None))
    assert features["receiver_domain"] == "unknown"
    assert features["receiver_domain_count"] == 0
    assert features["receiver_unique_domain_count"] == 0


def test_multiple_urls():
    _, features = parse_and_extract(make_email(
        body="Visit https://example.com/a and https://sub.example.org/b."
    ))
    assert features["url_count"] == 2
    assert features["urls"] == (
        "https://example.com/a;https://sub.example.org/b"
    )


def test_invalid_date_treated_as_missing():
    _, features = parse_and_extract(make_email(date="not a valid date"))
    assert features["date_year"] is None
    assert features["date_missing"] == 1
