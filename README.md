# Phishing Email Detector

An end-to-end machine learning application that analyzes uploaded email messages and classifies them as **Phishing** or **Legitimate**. The application combines email parsing, structural feature extraction, preprocessing, a trained SGD classifier, a FastAPI backend, and a Streamlit interface.

The current interface supports `.eml` email files and batch analysis. The frontend sends each uploaded email to the configured FastAPI backend and displays the classification results.

---

## Key Features

- **Email file parsing:** Reads email messages in `.eml` format (RFC 5322).
- **Feature extraction:** Extracts 18 structural features from an email, including information from its headers, body, URLs, and attachments.
- **Preprocessing:** Transforms extracted features into the representation expected by the trained model.
- **Machine learning classification:** Uses a trained `SGDClassifier` to classify emails as phishing or legitimate.
- **REST API:** Uses FastAPI to expose the prediction pipeline.
- **Interactive dashboard:** Uses Streamlit to provide an email-scanning interface and display batch results.
- **Batch analysis:** Supports selecting up to 10 `.eml` files in one batch. Files are submitted sequentially, one API request per email.
- **JSON report:** Allows users to download a JSON report for the most recently submitted batch.
- **Docker support:** Runs the application in a container.
- **Automated tests:** Includes tests for application components and integration behaviour.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn |
| Model Persistence | Joblib |
| Backend API | FastAPI |
| API Validation | Pydantic |
| Frontend | Streamlit |
| Email Parsing | Python email package |
| Testing | Pytest |
| Containerization | Docker |
| Development Tools | Jupyter Notebook, VS Code |

## Project Structure

The repository is organized by responsibility. The structure below reflects the main folders and files visible in the project workspace; individual notebook, report, and test files may be added as development continues.

```text
Phishing-Email-Detector/
│
├── app/
│   ├── __init__.py
│   ├── email_parser.py
│   ├── feature_extractor.py
│   ├── main.py
│   ├── preprocessor.py
│   └── tokenizers.py
│
├── data/
│   └── (dataset files and intermediate data)
│
├── docs/
│   └── working-proof/
│       ├── PhishGuard_Dashboard.pdf
│       └── PhishGuard_Email_Scanner.pdf
│
├── frontend/
│   ├── app.py
│   └── README.md
│
├── models/
│   ├── encoded_features.npz
│   ├── encoded_test_features.npz
│   ├── preprocessor.joblib
│   ├── sgd_classifier.joblib
│   ├── y_test.csv
│   └── y_train.csv
│
├── notebooks/
│   └── (project development notebooks)
│
├── reports/
│   └── (analysis and evaluation reports)
│
├── tests/
│   ├── integration/
│   └── (unit and integration test files)
│
├── .gitignore
├── Dockerfile
└── README.md
```

## Machine Learning Workflow

```text
Zenodo Email Dataset
        |
        v
Dataset Inspection and EDA
        |
        v
Data Cleaning and Preparation
        |
        v
Feature Engineering
        |
        v
Train / Test Data Preparation
        |
        v
Feature Encoding and Preprocessing
        |
        v
SGD Classifier Training
        |
        v
Model Evaluation
        |
        v
Save Preprocessor and Classifier
        |
        v
Email Parser (.eml)
        |
        v
18-Feature Extraction
        |
        v
Saved Preprocessor
        |
        v
SGD Classifier
        |
        v
Phishing / Legitimate Prediction
        |
        v
FastAPI + Streamlit Interface
```

### Inference pipeline

When a user uploads an `.eml` file:

1. The Streamlit frontend sends the file to the FastAPI backend.
2. The email parser reads the message, including its headers and body.
3. The feature extractor derives the 18 structural input features.
4. The saved preprocessor transforms those features into the model's expected input representation.
5. The saved SGD classifier produces the prediction.
6. The API returns the result, and the frontend displays whether the email was classified as **Phishing** or **Legitimate**.

The application loads the saved artifacts for inference. It does not need to retrain the classifier every time a user scans an email.

## Model Directory: What Each File Does

The `models/` folder contains the serialized model components and prepared feature/label data used by the training and inference workflow. These files have different purposes; they are not interchangeable.

| File | Purpose |
|---|---|
| `preprocessor.joblib` | The fitted preprocessing object. It applies the transformations learned during training to the extracted email features. The same fitted preprocessor must be used during inference so that incoming emails are represented consistently with the training data. |
| `sgd_classifier.joblib` | The trained `SGDClassifier`. It receives the preprocessed feature representation and predicts the class: legitimate or phishing. |
| `encoded_features.npz` | A NumPy compressed archive containing the encoded feature data used for model development/training. It stores prepared feature arrays rather than a human-readable CSV table. |
| `encoded_test_features.npz` | A NumPy compressed archive containing the encoded test feature data used to evaluate the trained classifier. |
| `y_train.csv` | The training target labels corresponding to the training feature data. These labels provide the expected class for each training sample. |
| `y_test.csv` | The test target labels corresponding to the test feature data. They are used to compare model predictions against the expected test classes during evaluation. |

### Why both the preprocessor and classifier are required

The classifier was trained on transformed feature data, not directly on the raw 18-feature input. At prediction time, the application must therefore apply the **same fitted preprocessor** before passing the transformed data to `sgd_classifier.joblib`.

Using a different preprocessing procedure, changing feature order, or skipping preprocessing can cause incorrect input dimensions or inconsistent predictions.

The `.npz` feature archives and label CSV files support the model development and evaluation workflow. The two `.joblib` files are the key saved artifacts required by the application at inference time.

> **Security note:** Only load Joblib files from trusted sources. Deserializing untrusted Python objects can execute code.

## Dataset

This project uses the **MeAJOR: Merged email Assets from Joint Open-source Repositories** dataset, hosted on Zenodo.

**Dataset record:** [Zenodo – MeAJOR dataset](https://zenodo.org/records/18471483)

The Zenodo record describes 108,685 anonymized, preprocessed email samples. Its binary labels are `0` for benign and `1` for phishing. The record provides the dataset in CSV and compressed Parquet formats. The CSV download is listed at approximately 191.1 MB, while the compressed Parquet download is approximately 86.3 MB.

### Why the dataset is not stored in this GitHub repository

The dataset file is large, so it is not included in this repository. Instead, download it directly from the Zenodo record above. This keeps the Git repository focused on source code, model artifacts, notebooks, and documentation rather than storing a large copy of the dataset.

After downloading, place the dataset in the appropriate location under `data/` according to the paths used by the project notebooks and scripts. Do not assume a filename or move the file without checking the path configured in the code.

**Dataset citation**

Cardoso, F., Vitorino, J., Mendes, P., Maia, E., & Praça, I. *MeAJOR: Merged email Assets from Joint Open-source Repositories* (Version 2.0). Zenodo. https://doi.org/10.5281/zenodo.18471483

Please consult the Zenodo record for the dataset's licence and reuse conditions, and retain the dataset attribution when using or redistributing it.

## Running the Application

### Prerequisites

- Python installed
- Git
- Docker Desktop (if using the containerized version)

### Run locally

Create and activate a virtual environment from the project root.

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Start the FastAPI backend in one terminal:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Start the Streamlit frontend in a second terminal:

```powershell
streamlit run frontend/app.py
```

Open the frontend at `http://localhost:8501`. The FastAPI interactive documentation is available at `http://localhost:8000/docs`.

The frontend's configured API base URL must point to the running backend. The screenshot evidence included with this repository shows the local configuration using `http://127.0.0.1:8000`.

### Run with Docker

Build the image from the project root:

```powershell
docker build -t phishguard:latest .
```

Run the container:

```powershell
docker run -d `
  --name phishguard `
  -p 8501:8501 `
  -p 8000:8000 `
  -v "${PWD}/models:/app/models:ro" `
  phishguard:latest
```

Then open:

- **PhishGuard Streamlit interface:** `http://localhost:8501`
- **FastAPI documentation:** `http://localhost:8000/docs`

The volume mount makes the local `models/` directory available inside the container as read-only model files. Keep the expected model artifacts in that directory before starting the container.

To view container logs:

```powershell
docker logs phishguard
```

To stop and remove the container:

```powershell
docker stop phishguard
docker rm phishguard
```

## Working Proof: Application PDFs

The following PDF files are included as working evidence of the running Streamlit application. They are screenshots captured from the local PhishGuard interface on **31 October 2026**.

### 1. PhishGuard Dashboard

The dashboard PDF shows the main security workspace, the FastAPI connection status, the readiness indicators for the preprocessor and SGD classifier, and the detection pipeline. It also shows the session summary with two analyzed emails: one classified as phishing and one as legitimate.

[View the PhishGuard Dashboard PDF](docs/working-proof/PhishGuard_Dashboard.pdf)

### 2. PhishGuard Email Scanner

The email scanner PDF shows the `.eml` upload interface and batch analysis report. The captured example contains two submitted email files, with one classified as phishing and one as legitimate. The interface also displays the JSON batch-report download option.

[View the PhishGuard Email Scanner PDF](docs/working-proof/PhishGuard_Email_Scanner.pdf)

These PDFs demonstrate the interface and a sample successful analysis flow. They are illustrative working evidence, not a guarantee that every email will be classified correctly.

## Testing

Run the test suite from the project root:

```powershell
python -m pytest -v
```

The repository includes a `tests/` directory with integration tests. Add or update tests when changing the parser, feature extraction, preprocessing, classifier integration, or API upload flow.

## Current Application Behaviour

Based on the captured application evidence:

- The Streamlit dashboard reports the FastAPI service as online.
- The preprocessor and SGD classifier are shown as ready.
- The scanner accepts `.eml` files.
- The scanner interface allows up to 10 files per batch and indicates a 200 MB per-file limit.
- Batch files are analyzed sequentially, with one API request per email.
- The displayed example batch contains one phishing result and one legitimate result.

These are observations from the included local screenshots, not general performance claims about the model.

## Limitations and Responsible Use

- The model's output is a prediction, not a definitive security verdict.
- A legitimate email may be flagged as phishing, and a phishing email may be classified as legitimate.
- The model's performance depends on the training data, feature extraction process, and the similarity between new emails and the data used during training.
- Do not upload confidential or sensitive emails to an API host unless you trust and control that host.
- Only inspect email messages that you are authorized to access.
- This project is intended for educational and demonstration purposes. It should not be treated as a replacement for a production email security system.

## Future Improvements

- Expand testing with diverse real-world email samples.
- Add stronger validation and error handling for malformed `.eml` files.
- Improve model monitoring and prediction logging.
- Add authentication and security controls before exposing the API publicly.
- Add reproducible model-training and evaluation scripts.
- Evaluate the model on data that is separate from the training dataset.

## Author

**J. Dharanendiran**  
B.Tech Artificial Intelligence and Data Science

GitHub: [J-Dharanendiran](https://github.com/J-Dharanendiran)

## License

No project licence has been specified in this README. Add a licence only after deciding the terms under which the project code may be reused. The dataset has its own separate source and licence terms; refer to the Zenodo record for those conditions.
