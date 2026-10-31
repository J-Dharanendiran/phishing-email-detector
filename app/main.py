from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, Field

from app.email_parser import parse_email
from app.feature_extractor import extract_features
from app.preprocessor import load_artifacts, transform_features


# --------------------------------------------------
# GLOBAL MODEL REFERENCES
# --------------------------------------------------

preprocessor = None
classifier = None


# --------------------------------------------------
# APPLICATION LIFESPAN
# --------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):

    global preprocessor, classifier

    preprocessor, classifier = load_artifacts()

    yield

    preprocessor = None
    classifier = None


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="Phishing Email Detector API",
    description="Machine learning API for detecting phishing emails.",
    version="1.1.0",
    lifespan=lifespan
)


# --------------------------------------------------
# REQUEST SCHEMA FOR FEATURE-BASED PREDICTION
# --------------------------------------------------

class EmailRequest(BaseModel):

    sender_domain: str
    receiver_domain: str
    subject: str
    content_types: str
    body: str
    urls: str
    url_count: int = Field(ge=0)
    attachment_types: str
    language: str

    url_length_max_log: float
    url_length_avg_log: float
    url_subdom_max_log: float
    url_subdom_avg_log: float

    attachment_count_log: float
    receiver_domain_count: int = Field(ge=0)
    receiver_unique_domain_count: int = Field(ge=0)

    date_year: int | None = None
    date_missing: int = Field(ge=0, le=1)


# --------------------------------------------------
# PREDICTION HELPER
# --------------------------------------------------

def generate_prediction(features):

    if preprocessor is None or classifier is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded."
        )

    X_transformed = transform_features(
        features,
        preprocessor
    )

    prediction = int(
        classifier.predict(X_transformed)[0]
    )

    decision_score = float(
        classifier.decision_function(X_transformed)[0]
    )

    classification = (
        "Phishing" if prediction == 1
        else "Legitimate"
    )

    return {
        "prediction": prediction,
        "classification": classification,
        "decision_score": decision_score
    }


# --------------------------------------------------
# ROOT ENDPOINT
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "message": "Phishing Email Detector API",
        "status": "running",
        "docs": "/docs"
    }


# --------------------------------------------------
# HEALTH ENDPOINT
# --------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "preprocessor_loaded": preprocessor is not None,
        "classifier_loaded": classifier is not None
    }


# --------------------------------------------------
# EMAIL FILE UPLOAD PREDICTION
# --------------------------------------------------

@app.post("/predict")
async def predict_email_file(
    email_file: UploadFile = File(...)
):

    if not email_file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided."
        )

    if not email_file.filename.lower().endswith(".eml"):
        raise HTTPException(
            status_code=400,
            detail="Only .eml files are supported."
        )

    try:

        email_bytes = await email_file.read()

        if not email_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded email file is empty."
            )

        # 1. Parse raw email bytes.
        email_data = parse_email(email_bytes)

        # 2. Extract the 18 model features.
        features = extract_features(email_data)

        # 3. Transform features and predict.
        result = generate_prediction(features)

        return {
            "filename": email_file.filename,
            **result,
            "input_features": len(features),
            "encoded_features": int(
                preprocessor.transform(
                    __import__("pandas").DataFrame(
                        [features],
                        columns=preprocessor.feature_names_in_
                    )
                ).shape[1]
            )
        }

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Email processing failed: {str(error)}"
        )

    finally:
        await email_file.close()


# --------------------------------------------------
# FEATURE-BASED JSON PREDICTION
# --------------------------------------------------

@app.post("/predict/features")
def predict_from_features(email: EmailRequest):

    try:

        features = email.model_dump()

        return generate_prediction(features)

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

