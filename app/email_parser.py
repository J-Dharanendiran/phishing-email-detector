from datetime import timezone
from email import policy
from email.parser import BytesParser
from email.utils import getaddresses, parsedate_to_datetime


# --------------------------------------------------
# 1. EXTRACT EMAIL HEADERS
# --------------------------------------------------

def _normalize_date_to_utc(date_value):
    """
    Parse an RFC email Date header and normalize it to UTC.

    pandas.to_datetime(..., utc=True) treats timezone-naive values as UTC.
    This function follows the same convention.
    """
    if not date_value:
        return None

    try:
        parsed_date = parsedate_to_datetime(date_value)

        if parsed_date is None:
            return None

        if parsed_date.tzinfo is None:
            return parsed_date.replace(tzinfo=timezone.utc)

        return parsed_date.astimezone(timezone.utc)

    except (TypeError, ValueError, OverflowError):
        return None


def extract_headers(message):
    sender = message.get("From", "")

    receiver = []

    # Include To, Cc and Bcc when present in the supplied email file.
    for header in ("To", "Cc", "Bcc"):
        addresses = message.get_all(header, [])

        for _, address in getaddresses(addresses):
            if address:
                receiver.append(address)

    date = _normalize_date_to_utc(message.get("Date"))

    return {
        "sender": sender,
        "receiver": receiver,
        "date": date,
        "subject": message.get("Subject", "")
    }


# --------------------------------------------------
# 2. EXTRACT EMAIL BODY
# --------------------------------------------------

def extract_body(message):
    plain_text = []
    html_text = []
    content_types = set()

    for part in message.walk():
        if part.is_multipart():
            continue

        content_type = part.get_content_type()
        content_types.add(content_type)

        if part.get_content_disposition() == "attachment":
            continue

        if part.get_filename():
            continue

        if content_type not in ("text/plain", "text/html"):
            continue

        try:
            content = part.get_content()
        except (UnicodeDecodeError, LookupError, ValueError):
            payload = part.get_payload(decode=True)

            if payload is None:
                continue

            charset = part.get_content_charset() or "utf-8"

            try:
                content = payload.decode(charset, errors="replace")
            except LookupError:
                content = payload.decode("utf-8", errors="replace")

        if not isinstance(content, str):
            continue

        if content_type == "text/plain":
            plain_text.append(content)
        elif content_type == "text/html":
            html_text.append(content)

    return {
        "body": "\n".join(plain_text),
        "html_body": "\n".join(html_text),
        "content_types": sorted(content_types)
    }


# --------------------------------------------------
# 3. EXTRACT ATTACHMENTS
# --------------------------------------------------

def extract_attachments(message):
    attachments = []

    for part in message.walk():
        if part.is_multipart():
            continue

        filename = part.get_filename()
        disposition = part.get_content_disposition()

        if not filename and disposition != "attachment":
            continue

        payload = part.get_payload(decode=True)

        attachments.append({
            "filename": filename,
            "content_type": part.get_content_type(),
            "size": len(payload) if payload else 0
        })

    return attachments


# --------------------------------------------------
# 4. MAIN EMAIL PARSER
# --------------------------------------------------

def parse_email(email_bytes: bytes):
    if not isinstance(email_bytes, bytes):
        raise TypeError("Email input must be bytes.")

    if not email_bytes:
        raise ValueError("Email file is empty.")

    message = BytesParser(
        policy=policy.default
    ).parsebytes(email_bytes)

    headers = extract_headers(message)
    body_data = extract_body(message)
    attachments = extract_attachments(message)

    return {
        **headers,
        **body_data,
        "attachments": attachments,
        "attachment_count": len(attachments),
        "has_attachments": len(attachments) > 0
    }
