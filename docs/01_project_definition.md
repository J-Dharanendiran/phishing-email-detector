# Spam & Phishing Detector

## 1. Project Overview

The Spam & Phishing Detector is a machine learning application designed to classify suspicious text messages and phishing emails.

The application will use labelled text datasets to train supervised machine learning models that distinguish between legitimate messages and unwanted or malicious messages.

The project will initially focus on spam SMS classification and phishing email detection as separate classification tasks. Their feasibility will be evaluated independently before considering a combined classification system.

The project will combine natural language processing (NLP), text preprocessing, feature extraction, supervised machine learning, model evaluation, API development, automated testing, Docker, and deployment.

## 2. Problem Statement

People receive unwanted messages and deceptive communications through SMS, email, and other digital channels.

Some messages contain unsolicited promotions, misleading offers, fraudulent claims, or attempts to steal sensitive information.

Manually identifying these messages can be difficult, particularly when malicious messages resemble legitimate communications.

The objective of this project is to develop machine learning models that analyse message text and predict whether a message belongs to a specified category.

The initial system will classify SMS messages as spam or legitimate. A separate phishing email classifier will be investigated using an appropriately labelled email dataset.

The trained models will be exposed through a FastAPI service so that users can submit text and receive predictions.

## 3. Business Objective

Provide an initial text-classification service that can help users identify potentially unwanted or deceptive messages.

The intended users are:

* Individual users who want to examine suspicious messages.
* Developers building messaging or email-processing applications.
* Organisations exploring automated message classification.
* Students and researchers studying NLP and classical machine learning.

The application will be positioned as a classification aid rather than a complete cybersecurity solution.

Predictions will not guarantee that a message is safe or malicious. Commercial usefulness will require further evaluation using representative data, appropriate security testing, and feedback from intended users.

## 4. Detection Scope

The project will initially investigate two related but distinct tasks.

### Task A: Spam SMS Classification

The first version will classify SMS messages into two categories:

* `ham`: Legitimate or non-spam messages.
* `spam`: Messages labelled as spam in the selected dataset.

The initial dataset candidate is the India Spam SMS dataset hosted on Hugging Face.

Dataset source: https://huggingface.co/datasets/CloveAI/india-spam-sms

The dataset's label definitions, collection dates, provenance, licence, and geographical representativeness must be verified before use.

### Task B: Phishing Email Classification

A separate model will be developed to distinguish phishing emails from legitimate emails.

The initial phishing dataset candidate is the MeAJOR phishing email dataset.

Dataset source: https://zenodo.org/records/18471483

The downloaded dataset's actual contents, label definitions, email-text availability, provenance, licence, and collection dates must be inspected before training.

The phishing classifier will only be implemented if the dataset provides suitable labelled examples for the intended task.

### Scope limitations

Spam and phishing are not interchangeable categories.

Spam may be unwanted without being malicious, while phishing involves deceptive attempts to obtain sensitive information or induce unsafe actions.

SMS phishing, commonly called smishing, also differs from email phishing in its communication format and typical characteristics.

The initial implementation will therefore treat SMS spam detection and email phishing detection as separate tasks.

A unified multiclass classifier may be considered later if the datasets and labels are sufficiently compatible.

## 5. Dataset and Prediction Targets

### Dataset A: SMS Spam

Selected candidate: India Spam SMS dataset hosted on Hugging Face.

Repository: https://huggingface.co/datasets/CloveAI/india-spam-sms

Intended prediction target: A label distinguishing spam messages from legitimate messages.

The actual text column, label column, class definitions, record count, data types, and class distribution must be verified during dataset inspection.

### Dataset B: Phishing Email

Selected candidate: MeAJOR phishing email dataset hosted on Zenodo.

Repository: https://zenodo.org/records/18471483

Intended prediction target: A label distinguishing phishing emails from legitimate emails.

The dataset's actual columns, target encoding, email-text representation, record count, and label distribution must be verified before use.

### Dataset preparation

Each dataset will be investigated and prepared independently before any decision to combine datasets.

The preparation process will include:

* Inspecting columns and data types.
* Investigating missing or unusable text.
* Checking exact and near-duplicate records.
* Examining class distributions.
* Verifying label meanings and consistency.
* Investigating data provenance and collection dates.
* Reviewing licensing and permitted use.
* Identifying potential data leakage.

Any combined dataset must use compatible label definitions and a documented, consistent schema.

The source of each record should be retained where possible to support source-specific evaluation.

## 6. Candidate Input Features

The principal input feature for both tasks will be message text.

For SMS spam classification, the input will contain the SMS message.

For phishing email classification, the input may contain the email subject and body, depending on the selected dataset and the information supported by the training data.

Candidate text features include:

* Message body.
* Email subject, when available.
* Word and term frequencies.
* TF-IDF representations of the text.

Additional features, such as URL characteristics or email-header information, may be investigated in later versions if reliable data is available.

Features unavailable during prediction will not be used during training.

The final feature schema will be determined after inspecting the datasets and defining the intended API inputs.

## 7. Machine Learning Approach

The project will compare the following classification algorithms:

1. **Dummy Classifier:** Establishes a simple baseline against which the trained models can be compared.
2. **Multinomial Naive Bayes:** A candidate for text classification using non-negative word-frequency or TF-IDF features.
3. **Logistic Regression:** Provides a linear classification baseline and can produce probability estimates.
4. **Linear Support Vector Machine:** Provides another candidate for classification using sparse text representations.

TF-IDF will be investigated as the primary text-vectorization technique.

The text vectorizer and classifier will be combined into a reproducible scikit-learn pipeline.

The vectorizer will be fitted only on the training data. Validation and test data will be transformed using the fitted vectorizer to avoid information leakage.

The algorithms will be evaluated separately for SMS spam classification and phishing email classification.

The final model for each task will be selected based on measured performance, error analysis, and the requirements of the intended application.

Probability estimates will only be exposed when supported by the selected model and its implementation. Any reported probabilities will be interpreted as model estimates, not guarantees of malicious intent.

## 8. Model Evaluation

The models will be evaluated using:

* Precision.
* Recall.
* F1-score.
* Confusion matrix.

Accuracy may also be reported, but it will not be used as the sole measure of model quality.

Evaluation will focus on the following error types:

* False positives: Legitimate messages incorrectly classified as spam or phishing.
* False negatives: Spam or phishing messages incorrectly classified as legitimate.

The importance of these errors will be considered when selecting decision thresholds.

A consistent evaluation procedure will be used to compare candidate algorithms within each task.

The project will investigate class imbalance, duplicate records, label quality, and potential overlap between training and test data.

Where multiple datasets are available for the same task, cross-dataset evaluation may be used to investigate generalisation across different data sources.

Results obtained on different test sets will not automatically be treated as directly comparable.

No performance threshold or detection accuracy will be claimed before the models have been trained and evaluated.

## 9. Application Architecture

The application will contain the following components:

* Dataset inspection and validation.
* Reproducible text-preprocessing and training pipelines.
* TF-IDF feature extraction.
* Baseline model development.
* Model training and comparison.
* Model evaluation and error analysis.
* Serialization and loading of selected pipelines.
* FastAPI prediction endpoints.
* Request validation using Pydantic.
* Automated API and preprocessing tests.
* Docker packaging.
* Deployment configuration.
* API documentation.

The initial implementation will support one classification task through its own prediction endpoint or service interface.

The architecture may be extended to support separate SMS spam and phishing email classifiers.

The deployed application must load the same preprocessing and vectorization pipeline used during model training.

## 10. Expected Input and Output

### SMS Spam Classification

The API will accept a text message.

Illustrative request:

```
{
    "message": "Congratulations! Claim your prize now."
}
```

Illustrative response:

```
{
    "prediction": "spam"
}
```

### Phishing Email Classification

The API may accept an email subject and body, depending on the final input schema.

Illustrative request:

```
{
    "subject": "Urgent account verification",
    "message": "Please verify your account immediately."
}
```

Illustrative response:

```
{
    "prediction": "phishing"
}
```

These examples illustrate the proposed API structure. They are not actual predictions or measured model results.

The final request and response schemas will be defined after inspecting the datasets and selecting the models.

The API will validate incoming requests and handle empty messages, malformed requests, unsupported input types, and other invalid inputs appropriately.

The application will not claim that a message is safe merely because it is classified as legitimate.

## 11. Success Criteria

The project will be considered technically successful when:

1. The selected datasets have been inspected and their sources documented.
2. Label meanings and prediction targets have been verified.
3. Data preparation is reproducible and documented.
4. The candidate models can be trained and compared.
5. Appropriate evaluation metrics and confusion matrices are reported.
6. Important false positives and false negatives are investigated.
7. The selected preprocessing and model pipeline can be saved and loaded successfully.
8. The API returns predictions for valid requests.
9. Automated tests cover valid inputs, invalid inputs, and important edge cases.
10. The application runs successfully in Docker.
11. The API documentation is accessible.
12. The README documents installation, usage, training, evaluation, and limitations.

For a combined classifier, additional success criteria will include verified label compatibility, duplicate handling, and evaluation across relevant data sources.

Real-world effectiveness will require further testing on representative messages that were not used to train or select the model.

## 12. Assumptions and Limitations

The performance of the models will depend on dataset quality, label reliability, collection dates, class balance, and representativeness.

A dataset's publication date does not necessarily indicate when its messages were collected.

The project will verify dataset provenance and licensing before making claims about recency or permitted use.

SMS spam detection and phishing email detection involve different message formats and potentially different feature distributions. Performance on one task will not establish performance on the other.

Models trained on historical messages may not recognise newly developed scam techniques or phishing tactics.

TF-IDF represents text through learned statistical features. It does not independently establish whether a message is malicious or understand the full context of a communication.

High precision, recall, or F1-score on a particular test set will not guarantee equivalent performance on real-world traffic.

Probability estimates may require calibration and threshold selection before they can be interpreted reliably.

The application will provide classification assistance rather than guaranteed threat detection. It must not be treated as a replacement for dedicated security controls or human investigation of high-risk communications.

## 13. Definition of Completion

The project will be considered technically complete when:

* The SMS spam classification pipeline has been trained and evaluated.
* The phishing email classification pipeline has been developed if the selected data supports the task.
* The selected models and their preprocessing steps can be loaded for inference.
* The FastAPI service accepts validated requests and returns predictions.
* Automated tests cover the principal API and model-inference behaviours.
* The application has been packaged and tested using Docker.
* The deployment has been completed if public hosting remains within the final project scope.
* The repository documents the datasets, their sources, preprocessing decisions, model results, evaluation methodology, limitations, API usage, and installation steps.

The final application will clearly distinguish between spam classification and phishing detection and will document the limitations of each model.
