from app.preprocessor import (
    load_artifacts,
    transform_features
)


# --------------------------------------------------
# LOAD ARTIFACTS
# --------------------------------------------------

preprocessor, classifier = load_artifacts()


# --------------------------------------------------
# SAMPLE EMAIL
# --------------------------------------------------

sample_email = {

    "sender_domain": "gmail.com",

    "receiver_domain": "company.com",

    "subject": "Urgent: Verify your account",

    "content_types": "text/plain; text/html",

    "body": """
    Your account requires immediate verification.
    Click the link below to verify your account.
    """,

    "urls": "https://example.com/verify",

    "url_count": 1,

    "attachment_types": "",

    "language": "en",

    "url_length_max_log": 3.0,

    "url_length_avg_log": 3.0,

    "url_subdom_max_log": 0.0,

    "url_subdom_avg_log": 0.0,

    "attachment_count_log": 0.0,

    "receiver_domain_count": 1,

    "receiver_unique_domain_count": 1,

    "date_year": 2026,

    "date_missing": 0
}


# --------------------------------------------------
# TRANSFORM FEATURES
# --------------------------------------------------

X_transformed = transform_features(
    sample_email,
    preprocessor
)


# --------------------------------------------------
# VERIFY OUTPUT
# --------------------------------------------------

print("\nTransformation Successful!")

print("Transformed shape:", X_transformed.shape)

print("Expected features:", classifier.n_features_in_)

print(
    "Feature dimensions match:",
    X_transformed.shape[1] == classifier.n_features_in_
)


# --------------------------------------------------
# PREDICTION TEST
# --------------------------------------------------

prediction = classifier.predict(X_transformed)

print("\nPrediction:", prediction[0])

print(
    "Classification:",
    "Phishing" if prediction[0] == 1 else "Legitimate"
)

