PhishGuard  — Streamlit Frontend

A redesigned dark cybersecurity-style frontend for the existing Phishing Email Detector FastAPI service. The frontend does not modify the model, preprocessing pipeline, or backend endpoints.

Features

Dashboard with session-based scan counts and recent activity

.eml email scanner connected to POST /predict

API and model-artifact health indicators using GET /health

Phishing / legitimate result cards and technical response details

Downloadable JSON analysis response

Product overview and workflow page

Project layout

Keep this folder inside your existing project root:

project-root/
├── app/
├── models/
└── frontend/
    ├── app.py
    └── requirements.txt

Install

From the project root:

pip install -r frontend/requirements.txt

Run the backend

In terminal 1, from the project root:

uvicorn app.main:app --reload

Run the frontend

In terminal 2, from the same project root:

streamlit run frontend/app.py

Open the local Streamlit URL, usually http://localhost:8501.

The sidebar API URL defaults to http://127.0.0.1:8000. You can override it with the API_BASE_URL environment variable or edit it in the sidebar.

Backend contract

GET /health

POST /predict with multipart field name email_file

Only .eml files are supported by the current backend. Dashboard counts are stored in Streamlit session state and are not persistent database analytics. The SGD decision_score is not a probability or calibrated confidence percentage.

Replace the old frontend

Back up your current frontend directory if you want to retain the old UI.

Replace frontend/app.py, frontend/requirements.txt, and README.md with the files in this package.

Restart Streamlit. If it is already running, stop it with Ctrl+C and run the command above again.

The app/ backend and models/ artifacts remain untouched.