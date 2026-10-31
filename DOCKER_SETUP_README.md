# PhishGuard Docker setup

This setup runs the existing FastAPI backend and Streamlit multi-email frontend
as two separate containers. It does not rebuild or modify the trained model.

## Expected project structure

Place these Docker files in the project root. The existing application should
look broadly like this:

    Phishing Email Detector/
    ├── app/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── email_parser.py
    │   ├── feature_extractor.py
    │   ├── preprocessor.py
    │   └── tokenizers.py
    ├── models/
    │   ├── sgd_classifier.joblib
    │   └── feature_selection/
    │       └── preprocessor.joblib
    ├── frontend/
    │   ├── app.py
    │   ├── requirements.txt
    │   └── Dockerfile
    ├── requirements.txt
    ├── Dockerfile
    ├── docker-compose.yml
    └── .dockerignore

The backend Dockerfile expects the project's existing root `requirements.txt`.
It must include the packages used by the API and model, including FastAPI,
Uvicorn, python-multipart, pandas, NumPy, joblib and scikit-learn. Add
`langdetect` if you want language detection enabled.

IMPORTANT: joblib/scikit-learn artifacts can be version-sensitive. Before
building, compare the scikit-learn version used to train/save the model with
the version listed in the root requirements.txt. Use the same version that
created the saved artifacts; do not blindly upgrade scikit-learn.

## Build and start

Run these commands from the project root, where docker-compose.yml is located:

    docker compose config
    docker compose up --build

Open:

- Streamlit: http://localhost:8501
- FastAPI health: http://localhost:8000/health
- FastAPI docs: http://localhost:8000/docs

The frontend uses `API_BASE_URL=http://backend:8000`. This is intentional:
inside the frontend container, `localhost` refers to the frontend container,
not the backend container.

## Stop

    docker compose down

To rebuild after changing Python code or dependencies:

    docker compose up --build

## Model files

The `models/` directory is bind-mounted read-only into the backend container.
Keep these paths and filenames unchanged:

- `models/sgd_classifier.joblib`
- `models/feature_selection/preprocessor.joblib`

Do not commit or bake large/private model artifacts into the image unless you
intentionally want them distributed with the image.

## Notes

- Ports 8000 and 8501 must be available on the host.
- The current frontend's 10-file batch processing remains sequential.
- Uploaded `.eml` files are sent from Streamlit to FastAPI; the API processes
  each file using the existing `/predict` endpoint.
- Docker Compose waits for the API `/health` check before starting Streamlit.
- This is a local deployment baseline, not a hardened public production
  deployment. Do not expose it publicly without adding authentication, HTTPS,
  upload-size limits, and appropriate operational controls.
