from app.email_parser import parse_email
from app.feature_extractor import extract_features

sample_email = b"""From: security@example.com
To: user@gmail.com, admin@yahoo.com
Subject: Account Verification Required
Date: Fri, 30 Oct 2026 10:30:00 +0000
MIME-Version: 1.0
Content-Type: text/plain; charset="utf-8"

Please verify your account immediately.
Visit https://example.com/verify
"""

parsed = parse_email(sample_email)

features = extract_features(parsed)

print("Extracted Features")
print("-" * 50)

for key, value in features.items():
    print(f"{key}: {value}")

print("\nTotal features:", len(features))