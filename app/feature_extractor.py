import math
import re
from email.utils import parseaddr
from html.parser import HTMLParser
from urllib.parse import urlparse


# --------------------------------------------------
# 1. URL EXTRACTION
# --------------------------------------------------

class URLExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.urls = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()

        if tag == "a":
            wanted_attributes = {"href"}
        elif tag in {"img", "script", "iframe"}:
            wanted_attributes = {"src"}
        else:
            wanted_attributes = set()

        for key, value in attrs:
            if key and key.lower() in wanted_attributes and value:
                self.urls.append(value.strip())


def extract_urls(body, html_body):
    urls = []

    # URLs found in plain-text body.
    text_urls = re.findall(
        r'https?://[^\s<>"\']+|www\.[^\s<>"\']+',
        body or "",
        flags=re.IGNORECASE
    )
    urls.extend(text_urls)

    # URLs found in selected HTML attributes.
    parser = URLExtractor()
    if html_body:
        parser.feed(html_body)
        parser.close()

    urls.extend(parser.urls)

    # Remove common trailing punctuation and empty values.
    urls = [
        url.strip().rstrip(".,;:!?)]}")
        for url in urls
        if isinstance(url, str) and url.strip()
    ]

    # Preserve first-seen order and remove exact duplicates.
    return list(dict.fromkeys(urls))


# --------------------------------------------------
# 2. DOMAIN EXTRACTION
# --------------------------------------------------

def extract_domain(address):
    _, email_address = parseaddr(address or "")

    if "@" not in email_address:
        return ""

    return email_address.rsplit("@", 1)[1].lower().strip()


def extract_receiver_domains(receivers):
    """
    Return one domain for every valid receiver address.

    Do not deduplicate here: training's receiver_domain_count counts
    all non-empty entries. Unique-domain counting is done separately.
    """
    domains = []

    for receiver in receivers or []:
        domain = extract_domain(receiver)

        if domain:
            domains.append(domain)

    return domains


# --------------------------------------------------
# 3. URL STATISTICS
# --------------------------------------------------

def get_url_statistics(urls):
    lengths = []
    subdomain_counts = []

    for url in urls:
        parsed = urlparse(
            url if "://" in url else "https://" + url
        )

        hostname = (parsed.hostname or "").lower()

        if not hostname:
            continue

        lengths.append(len(url))

        # Retains the existing inference heuristic:
        # number of hostname labels before the final two labels.
        # This is not public-suffix-aware. Confirm against the original
        # dataset's feature-generation code before claiming exact parity.
        labels = hostname.split(".")
        subdomain_counts.append(max(0, len(labels) - 2))

    return {
        "url_count": len(urls),

        "url_length_max_log": math.log1p(
            max(lengths, default=0)
        ),

        "url_length_avg_log": math.log1p(
            sum(lengths) / len(lengths) if lengths else 0
        ),

        "url_subdom_max_log": math.log1p(
            max(subdomain_counts, default=0)
        ),

        "url_subdom_avg_log": math.log1p(
            sum(subdomain_counts) / len(subdomain_counts)
            if subdomain_counts else 0
        )
    }


# --------------------------------------------------
# 4. ATTACHMENT FEATURES
# --------------------------------------------------

def extract_attachment_features(attachments):
    attachments = attachments or []

    attachment_types = [
        attachment["content_type"]
        for attachment in attachments
        if attachment.get("content_type")
    ]

    return {
        "attachment_types": (
            ";".join(attachment_types)
            if attachment_types
            else "none"
        ),
        "attachment_count_log": math.log1p(len(attachments))
    }


# --------------------------------------------------
# 5. LANGUAGE FEATURE
# --------------------------------------------------

def detect_language(body):
    text = (body or "").strip()

    if len(text) < 20:
        return "unknown"

    try:
        from langdetect import DetectorFactory, detect

        # Make language detection repeatable between runs.
        DetectorFactory.seed = 0
        return detect(text)

    except ImportError:
        return "unknown"
    except Exception:
        return "unknown"


# --------------------------------------------------
# 6. MAIN FEATURE EXTRACTOR
# --------------------------------------------------

EXPECTED_FEATURES = [
    "sender_domain",
    "receiver_domain",
    "subject",
    "content_types",
    "body",
    "urls",
    "url_count",
    "attachment_types",
    "language",
    "url_length_max_log",
    "url_length_avg_log",
    "url_subdom_max_log",
    "url_subdom_avg_log",
    "attachment_count_log",
    "receiver_domain_count",
    "receiver_unique_domain_count",
    "date_year",
    "date_missing"
]


def extract_features(email_data):
    sender = email_data.get("sender", "")
    receivers = email_data.get("receiver", [])

    subject = email_data.get("subject") or "[NO SUBJECT]"
    raw_body = email_data.get("body") or ""
    body = raw_body if raw_body.strip() else "[NO BODY]"
    html_body = email_data.get("html_body") or ""

    content_types = email_data.get("content_types", [])
    attachments = email_data.get("attachments", [])
    date = email_data.get("date")

    # Domain features.
    sender_domain = extract_domain(sender)

    receiver_domains = extract_receiver_domains(receivers)

    # Preserve duplicate receiver domains in the multilabel string.
    receiver_domain = (
        ";".join(receiver_domains)
        if receiver_domains else "unknown"
    )

    receiver_domain_count = len(receiver_domains)

    receiver_unique_domain_count = len({
        domain.lower().strip()
        for domain in receiver_domains
        if domain.strip()
    })

    # URL features.
    urls = extract_urls(body, html_body)
    url_statistics = get_url_statistics(urls)

    urls_text = ";".join(urls) if urls else "[NO URL]"

    # Content types.
    content_types_text = (
        ";".join(content_types)
        if content_types else "unknown"
    )

    # Attachment features.
    attachment_features = extract_attachment_features(attachments)

    # Date features.
    # email_parser.py normalizes parsed dates to UTC. This also handles
    # externally supplied naive datetimes consistently with utc=True.
    date_missing = int(date is None)

    if date is None:
        date_year = None
    else:
        if getattr(date, "tzinfo", None) is not None:
            from datetime import timezone
            date = date.astimezone(timezone.utc)

        date_year = date.year

    # Language.
    language = detect_language(body)

    # Construct the exact 18 model input columns in training order.
    features = {
        "sender_domain": sender_domain or "unknown",
        "receiver_domain": receiver_domain,
        "subject": subject,
        "content_types": content_types_text,
        "body": body,
        "urls": urls_text,
        "url_count": url_statistics["url_count"],
        "attachment_types": attachment_features["attachment_types"],
        "language": language,
        "url_length_max_log": url_statistics["url_length_max_log"],
        "url_length_avg_log": url_statistics["url_length_avg_log"],
        "url_subdom_max_log": url_statistics["url_subdom_max_log"],
        "url_subdom_avg_log": url_statistics["url_subdom_avg_log"],
        "attachment_count_log": attachment_features["attachment_count_log"],
        "receiver_domain_count": receiver_domain_count,
        "receiver_unique_domain_count": receiver_unique_domain_count,
        "date_year": date_year,
        "date_missing": date_missing
    }

    # Fail immediately if the feature contract is accidentally changed.
    if list(features.keys()) != EXPECTED_FEATURES:
        raise RuntimeError(
            "Feature order or feature names do not match the "
            "expected 18-feature model input contract."
        )

    return features
