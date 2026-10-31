from app.email_parser import parse_email
from app.feature_extractor import extract_features

from email.message import EmailMessage
from email import policy


# Create sample email
message = EmailMessage()

message["From"] = "security@gmail.com"
message["To"] = "user@company.com"
message["Subject"] = "Urgent: Verify your account"

message.set_content(
    """
    Dear user,

    Your account requires immediate verification.

    Visit https://example.com/verify

    Regards,
    Security Team
    """
)

message.add_alternative(
    """
    <html>
        <body>
            <h2>Account Verification</h2>
            <a href="https://example.com/verify">
                Verify Account
            </a>
        </body>
    </html>
    """,
    subtype="html"
)


# Convert to bytes
email_bytes = message.as_bytes(policy=policy.default)


# Parse email
email_data = parse_email(email_bytes)


# Extract features
features = extract_features(email_data)


# Display features
print("\nFEATURE EXTRACTION RESULTS")
print("=" * 60)

for name, value in features.items():
    print(f"{name}: {value}")


# Validate model input
expected_features = [
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

print("\nVALIDATION")
print("=" * 60)

print("Expected features:", len(expected_features))
print("Extracted features:", len(features))

print(
    "All features present:",
    set(expected_features) == set(features)
)

print(
    "Correct feature order:",
    list(features.keys()) == expected_features
)

