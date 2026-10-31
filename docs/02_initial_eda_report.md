# Exploratory Data Analysis (EDA) Report

## MeAJOR Email Spam and Phishing Detection

| Item | Details |
|---|---|
| Notebook reviewed | `02_initial_eda(10).ipynb` |
| Input dataset | `../data/raw/meajor_cleaned_preprocessed.csv` |
| Dataset shape | 108,685 rows × 20 columns |
| Target column | `label` |
| EDA scope | Structure, data types, missingness, duplicate rows, target/source distributions, date sanity checks, numerical distributions, text lengths, token frequencies, and placeholder patterns |
| Current status | Initial EDA findings documented; data cleaning and several target-comparison analyses remain to be completed |

> **Label interpretation:** The MeAJOR dataset documentation defines `0` as **benign** and `1` as **phishing**. See the [official MeAJOR dataset record on Zenodo](https://zenodo.org/records/18471483). Treat this mapping as the project’s working label definition and preserve it consistently in code, charts, and the API.

---

## 1. Executive Summary

The dataset contains **108,685 email records and 20 columns**. It combines message content (`subject`, `body`), email metadata (`sender`, `receiver`, domains, `date`, `source`, `language`, `content_types`), extracted URL information, attachment-related fields, and a binary target label.

Among the rows with a label, **60,650 are benign (55.80%)** and **48,034 are phishing (44.20%)**. One row has no target label. The class distribution is reasonably balanced for a first modelling pass; class balancing should not be applied automatically without evaluating model performance.

The most important issues discovered in the notebook are:

- `attachment_types` is missing in **98.47%** of rows, while `urls` is missing in **41.07%**.
- There are **13 exact duplicate rows**.
- The dataset has **one missing target label** and small amounts of missingness in several metadata and text fields.
- All date strings parse, but the parsed range is **1889-05-19 to 2102-03-16**, which is suspicious for email timestamps and requires investigation.
- URL-related numerical features are strongly right-skewed. For example, `url_length_max` reaches **66,647** and `url_count` reaches **553**. At least one extreme URL record appears to contain image/GIF-like data appended to a URL, so URL extraction and feature calculations should be audited before treating these values as valid.
- The text analysis reveals possible differences between classes, including more frequent `you`/`your` tokens and placeholder patterns in the phishing class. These are exploratory associations, not rules that prove a message is phishing.
- The tokenizer `r"\b[a-z]+\b"` extracts alphabetic tokens only. It converts special placeholders such as `<|SIMBOL|>` into ordinary-looking tokens such as `simbol`, while discarding punctuation, digits, and most URL structure. Token-frequency results must therefore be interpreted with that limitation in mind.

The next stage should preserve the raw source, validate suspicious records, handle missing values according to their meaning, create model-ready features, and select features using training data only.

## 2. Dataset Overview

### 2.1 Structure and columns

The notebook reports a shape of **108,685 rows × 20 columns**. The columns fall into these broad groups:

| Group | Columns | Initial interpretation |
|---|---|---|
| Sender/recipient metadata | `sender`, `sender_domain`, `receiver`, `receiver_domain` | Potential identity/domain context; sender and receiver IDs appear anonymized or hashed in the sample output |
| Time | `date` | Timestamp; parsed successfully but contains implausible years |
| Text content | `subject`, `body` | Primary inputs for a text-classification model |
| Message format | `content_types`, `language` | Categorical metadata; some values combine multiple types/languages using semicolons |
| URL information | `urls`, `url_count`, `url_length_max`, `url_length_avg`, `url_subdom_max`, `url_subdom_avg` | URL text and engineered URL features |
| Attachment information | `has_attachments`, `attachment_count`, `attachment_types` | Whether attachments exist and their observed counts/types |
| Dataset provenance | `source` | Source collection identifier (`trec5`, `trec6`, `trec7`) |
| Target | `label` | Binary classification target: benign (`0`) or phishing (`1`) |

The input columns `date`, `subject`, and `body` were initially loaded as strings. The six URL/attachment numeric columns are stored as floating-point values, `has_attachments` is Boolean, and `label` is a floating-point column because it contains a missing value. Convert types deliberately during preprocessing rather than assuming their current representation is ideal for modelling.

### 2.2 Target distribution

| Label | Meaning | Rows | Share of all rows (rounded) |
|---:|---|---:|---:|
| 0 | Benign | 60,650 | 55.80% |
| 1 | Phishing | 48,034 | 44.20% |
| Missing | Unknown/unlabelled | 1 | <0.01% |
| **Total** | | **108,685** | **100%** |

There is no severe class imbalance in the labelled portion. Remove or quarantine the one unlabelled row from supervised model fitting; do not silently assign it to either class.

## 3. Missing-Value Analysis

The missing-value summary below is taken from the notebook. Percentages use the full 108,685-row dataset.

| Column | Missing rows | Missing percentage |
|---|---:|---:|
| `attachment_types` | 107,019 | 98.47% |
| `urls` | 44,633 | 41.07% |
| `receiver` | 2,371 | 2.18% |
| `receiver_domain` | 2,371 | 2.18% |
| `subject` | 1,455 | 1.34% |
| `sender` | 494 | 0.45% |
| `sender_domain` | 494 | 0.45% |
| `body` | 1 | 0.00092% |
| `source` | 1 | 0.00092% |
| `language` | 1 | 0.00092% |
| `label` | 1 | 0.00092% |
| `content_types` | 1 | 0.00092% |
| All remaining columns | 0 | 0% |

### Interpretation

- **`attachment_types`:** The number of missing values (107,019) exactly matches the number of `False` values in `has_attachments`. This suggests the missingness may often mean “no attachment type applies,” but matching totals do not prove row-by-row alignment. Check whether missing `attachment_types` corresponds to `has_attachments == False` before converting missing values to an explicit category such as `"none"`.
- **`urls`:** A missing URL string may mean that no URL was extracted, but it might also indicate an extraction or source-data problem. Compare it row by row with `url_count` and inspect examples before deciding how to represent it.
- **`subject` and `body`:** The notebook finds that all 1,455 missing subjects and the single missing body are also empty or whitespace-only after filling nulls with an empty string. Missing and empty text should be treated consistently, while keeping a flag if the absence itself may be informative.
- **Sender/receiver fields:** These are relatively low-missingness fields. Avoid dropping thousands of rows solely because sender/receiver information is absent; evaluate whether these features are needed and how they will be used.
- **`label`:** The missing target cannot be imputed from ordinary feature-imputation rules. Exclude the unlabelled record from supervised training and document the decision.

Do not use a global `dropna()` or fill every missing value with zero. Missingness in text, URL, attachment, label, and metadata fields has different meanings.

## 4. Duplicate Rows

The notebook detects **13 exact duplicate rows** using `df.duplicated()`.

This is approximately **0.012%** of the dataset. Before removing duplicates, confirm that they are truly identical across all 20 source columns and check whether duplicate messages could represent repeated observations from the underlying collection. For the initial modelling dataset, a reasonable plan is to remove exact duplicates after logging their count and retaining the untouched raw dataset. Also inspect duplicates based on normalized `subject`/`body` separately; that is a different operation from removing exact duplicate rows and must not be done automatically, since repeated email text can be legitimate.

## 5. Categorical and Source-Level Findings

### 5.1 Source distribution

| Source | Rows | Share of all rows (rounded) |
|---|---:|---:|
| `trec5` | 49,583 | 45.62% |
| `trec7` | 44,096 | 40.57% |
| `trec6` | 15,005 | 13.81% |
| Missing | 1 | <0.01% |

The source distribution is uneven, with `trec5` contributing the largest share. The current notebook has not yet documented a full `source`-versus-`label` cross-tabulation. Add that analysis before concluding whether source composition is associated with the target. If source and label are strongly correlated, a model could learn dataset/source artifacts rather than general phishing signals.

### 5.2 Language

The most common recorded values are `en` (**82,175 rows; 75.61%**) and `en;en` (**21,250 rows; 19.55%**), followed by much smaller counts for values such as `ru`, `ja`, `de`, `es`, and `zh`. Since language values can contain semicolon-separated combinations, inspect the field’s construction before grouping or encoding values. Do not assume `en;en` is equivalent to `en` until this representation is understood.

### 5.3 Content type

The most common `content_types` values are:

| Value | Rows | Share (rounded) |
|---|---:|---:|
| `text/plain` | 70,992 | 65.32% |
| `text/plain;text/html` | 21,174 | 19.48% |
| `text/html` | 15,270 | 14.05% |

Other values are less common and often contain semicolon-separated repeated types. During feature engineering, consider parsing this into meaningful indicators such as “contains plain text” and “contains HTML,” rather than one-hot encoding every combination without review.

### 5.4 Attachment presence

- `has_attachments == False`: **107,019 rows (98.47%)**
- `has_attachments == True`: **1,666 rows (1.53%)**

Attachment presence is rare in the dataset. The related `attachment_count` field is also highly concentrated at zero, so check its relationship with `has_attachments` and avoid unintentionally using two redundant features without evaluating whether both help.

## 6. Date and Timestamp Validation

The notebook converts `date` using `pd.to_datetime(..., errors="coerce", utc=True)` and finds **zero parsing failures**. However, the resulting range is:

- Earliest: **1889-05-19 08:59:51 UTC**
- Latest: **2102-03-16 15:16:56 UTC**

The source-level ranges are also suspicious:

| Source | Earliest parsed timestamp | Latest parsed timestamp |
|---|---|---|
| `trec5` | 1898-06-16 | 2034-11-21 |
| `trec6` | 1889-05-19 | 2019-10-29 |
| `trec7` | 1900-06-27 | 2102-03-16 |

Valid parsing only means that the strings can be interpreted as timestamps. It does not mean the dates are semantically correct. Some implausible dates appear in rows with `<|SIMBOL|>`-heavy subjects, so investigate whether malformed text encoding, source conversion, or date parsing/serialization introduced the values. Inspect the original raw date string and, where available, the source record before correcting or removing anything. Keep the original value in a raw column and record any correction rule.

## 7. Numerical Feature Analysis

The notebook examines the following six numerical features.

| Feature | Mean | Median (50%) | 75th percentile | Maximum | Skewness |
|---|---:|---:|---:|---:|---:|
| `url_count` | 3.31 | 1.00 | 2.00 | 553 | 9.37 |
| `url_length_max` | 31.37 | 26.00 | 48.00 | 66,647 | 315.01 |
| `url_length_avg` | 26.69 | 24.50 | 43.50 | 66,647 | 320.65 |
| `url_subdom_max` | 0.66 | 1.00 | 1.00 | 5 | 1.47 |
| `url_subdom_avg` | 0.59 | 0.21 | 1.00 | 5 | 1.74 |
| `attachment_count` | 0.021 | 0.00 | 0.00 | 61 | 109.65 |

### Main observations

- `url_count`, URL-length features, and `attachment_count` are strongly right-skewed: their means are pulled above their medians by relatively few large values.
- The 75th percentile of `attachment_count` is zero, indicating that at least three quarters of records have no recorded attachment count above zero.
- The zero values in URL features may represent emails with no extracted URLs, not missing values. Preserve that semantic distinction.
- Outliers should not automatically be removed using a generic IQR rule. In phishing detection, an unusual URL count or URL structure could be meaningful. First distinguish legitimate high-volume messages from extraction errors.

### URL extraction concern

The maximum stored `urls` text length is **66,647 characters**. The corresponding record begins with a URL followed by content resembling an embedded image/GIF payload (`.jpgR0lGOD...`), while the engineered URL length features also take the extreme value 66,647. This is a strong reason to audit the extraction/feature-generation process. It is not yet proof of the exact source of the issue.

Recommended checks:

1. Compare `len(urls)`, the number of URLs actually parsed, and each engineered URL length for the extreme rows.
2. Verify whether multiple URLs are separated consistently (for example by newlines) and whether non-URL payloads are being included.
3. Recalculate URL features from cleaned URL candidates if the extraction logic and raw content permit it.
4. Keep original values and record which rows were corrected or flagged. Do not silently cap or delete these values before understanding them.

## 8. Text-Length Analysis

The notebook computes `subject_length` and `body_length` using string length, filling missing text with `""` for these exploratory calculations.

| Feature | Mean | Median | 75th percentile | Maximum |
|---|---:|---:|---:|---:|
| `subject_length` | 42.04 | 32 | 47 | 3,701 |
| `body_length` | 1,168.10 | 797 | 1,533 | 30,574 |

The distributions are right-skewed, especially at the upper ends. The notebook also compares the text lengths by label:

| Label | Subject mean length | Subject median | Body mean length | Body median |
|---|---:|---:|---:|---:|
| 0 — Benign | 35.96 | 31 | 1,147.74 | 811 |
| 1 — Phishing | 49.72 | 32 | 1,193.83 | 783 |

Phishing-labelled messages have a longer average subject in this dataset, but the medians are similar. The means may be affected by a small number of long subjects. Body means are also similar, while the phishing median is slightly lower. These are descriptive results only; they do not establish that length alone is a reliable classifier.

The notebook reports 68,486 distinct non-missing subjects and 103,518 distinct non-missing bodies. It finds 9,947 subject values and 1,103 body values that appear more than once. Repeated subjects/bodies can be legitimate and should be examined separately from exact row duplicates.

## 9. Word, Token, and Placeholder Analysis

The current tokenizer is:

```python
re.findall(r"\b[a-z]+\b", text.lower())
```

It extracts alphabetic sequences after lowercasing. It does not preserve numbers, punctuation, URL structure, or token boundaries represented by special delimiters. Therefore, the counts below describe output from this particular tokenizer, not a complete linguistic or URL analysis.

### 9.1 Most frequent tokens

The most frequent subject tokens include `simbol`, `re`, `organization`, `product`, `for`, `to`, `the`, `date`, `r`, and `in`. The most frequent body tokens include `the`, `to`, `and`, `of`, `a`, `product`, `organization`, `name`, `you`, and `i`.

Several of these are anonymization placeholders or artefacts from placeholders. For example, the regular expression turns `<|SIMBOL|>` into the token `simbol`. This token is not necessarily a normal word appearing in the original email.

### 9.2 Class-specific subject tokens

The most distinctive high-frequency subject tokens in the reported class counts include:

- **Class 0 (benign):** `re`, `organization`, `product`, `r`, `date`, `for`, `in`, `fw`, `to`, and `of`.
- **Class 1 (phishing):** `simbol`, `product`, `you`, `the`, `your`, `for`, `to`, `organization`, `re`, and `a`.

After normalizing frequencies per 1,000 tokens, `simbol`, `you`, `your`, and `emoji` are much more frequent in Class 1 in this notebook’s tokenization. For example, `simbol` is reported at approximately **0.171 per 1,000 tokens in Class 0** versus **208.13 per 1,000 tokens in Class 1**. Because this pattern is strongly associated with the placeholder/encoding representation, do not treat it as a generalizable phishing signal without validating its origin and checking for dataset-source leakage.

### 9.3 Placeholder checks

The notebook searches for the exact angle-bracket format `<|PLACEHOLDER|>`.

| Placeholder | Records in subject | Records in body | Notes |
|---|---:|---:|---|
| `<|SIMBOL|>` | 3,438 | 0 | 3,391 subject records have label 1, 46 have label 0, and one has no label |
| `<|EMOJI|>` | 684 | 4,498 | Body occurrence: 604 Class 0 records (1.00%) and 3,893 Class 1 records (8.10%) |
| `<|URL|>` | 351 | 27,224 | Body occurrence: 11,721 Class 0 records (19.33%) and 15,503 Class 1 records (32.28%) |
| `<|ORGANIZATION|>` | 0 | 0 | Not found in this angle-bracket form |
| `<|PRODUCT|>` | 0 | 0 | Not found in this angle-bracket form |
| `<|NAME|>` | 0 | 0 | Not found in this angle-bracket form |

Important: the data sample also contains square-bracket placeholders such as `[NAME]` and `[ORGANIZATION]`. The zero counts above mean only that the specific **angle-bracket** spelling was not found. They do not mean these concepts are absent from the dataset. Confirm the intended placeholder conventions before normalizing them.

The high occurrence of `<|SIMBOL|>` in phishing-labelled subject text appears to be associated with unusual character encoding or transformed text. The notebook does not establish the cause. Investigate it during cleaning and avoid allowing this artefact to dominate the model unnoticed. Conversely, do not simply delete every placeholder: some placeholders may contain useful information or may be part of the intended anonymization scheme.

## 10. EDA Items Still to Complete

The latest notebook contains substantial overall and text-focused analysis, but it does **not yet show the following comparisons in a complete, documented form**:

1. **Numerical features by target:** compare count, mean, median, and distribution of URL and attachment features across labels `0` and `1`.
2. **Source versus target:** produce both a count crosstab and row-normalized percentages for `source` by `label`.
3. **Attachment presence versus target:** compare `has_attachments` proportions across classes.
4. **Feature relationships:** check correlations among numeric URL/attachment variables and inspect highly redundant feature pairs.
5. **Potential leakage:** evaluate whether source identifiers, timestamps, placeholder/encoding artefacts, or repeated messages allow a model to infer collection origin instead of generalizable phishing behaviour.

These are important because a feature can look useful overall but behave differently across labels, or appear predictive mainly because the source dataset uses different collection practices.

---

# 11. Upcoming Workflow

The steps below turn the EDA observations into a reproducible modelling dataset. Keep the current preprocessed input and a read-only copy of the original file. Write outputs to new versioned files rather than overwriting the source.

## Step 3 — Data Cleaning and Validation

**Goal:** correct or flag demonstrable data-quality problems while preserving valid information.

### Actions

1. **Create a cleaning log.** Record row counts before/after each operation, columns modified, rules applied, and the reason for each change.
2. **Handle exact duplicates.** Inspect the 13 duplicated rows, then remove confirmed exact duplicates from the modelling copy. Do not automatically remove rows just because `subject` or `body` repeats.
3. **Validate `label`.** Confirm only `0`, `1`, and missing are present. Quarantine/exclude the single missing-label row from supervised training rather than imputing the target.
4. **Audit timestamps.** Inspect the records outside a defensible date range, especially the years before modern email and dates far in the future. Check source/raw values and document any correction or removal rule. Preserve the original timestamp string.
5. **Audit URL extraction.** Inspect extreme `urls` rows, including the 66,647-character record and unusually high URL counts. Parse URL candidates using a consistent rule and recalculate engineered URL features if the raw information supports it.
6. **Standardize string representation carefully.** Check leading/trailing whitespace, empty strings, inconsistent line breaks, HTML remnants, and the square-bracket versus angle-bracket placeholder formats. Do not remove meaningful punctuation or URLs before establishing the text preprocessing strategy.
7. **Check logical consistency.** Verify `has_attachments` against `attachment_count` and `attachment_types`; check `url_count` against the extracted URL list; check that numerical counts are non-negative and whether integer-valued counts are currently stored as floats.

### Outputs

- A cleaning notebook or clearly separated cleaning section.
- `meajor_cleaned.csv` (or Parquet if preferred), with the raw file retained unchanged.
- A short cleaning log listing changes and unresolved anomalies.

## Step 4 — Missing-Value Handling

**Goal:** represent missingness according to what it means, not apply one fill rule to every column.

| Field/type | Recommended investigation and treatment |
|---|---|
| `label` | Exclude the one missing-label row from supervised model fitting. Do not impute a target. |
| `subject`, `body` | Convert null/empty values to a consistent empty-text representation for modelling, and optionally add `subject_missing` / `body_missing` indicators if absence may carry signal. Compare this choice with dropping the very small number of affected records. |
| `urls` | Determine whether missing means no URLs or unavailable extraction. If `url_count == 0` consistently identifies no URL, represent that semantic state explicitly; otherwise keep a missingness indicator. |
| `attachment_types` | Check row-level correspondence with `has_attachments`. If missing means no attachment, use a documented category such as `none`; if type data is unknown, preserve that as a different state. Consider excluding the raw field if it is too sparse or unreliable. |
| `sender` / `sender_domain` / `receiver` / `receiver_domain` | Evaluate value for the intended model and risk of leakage/privacy/source memorization. If retained, use an explicit missing/unknown category or missingness indicator. |
| `language`, `source`, `content_types` | Handle their single missing value with an explicit `unknown`/`missing` category if the field is used, or drop that row only when justified by the broader cleaning decision. |
| Numerical features | Their null count is zero in the notebook. Do not convert zeros to NaN without evidence; for URL fields, zero may mean no URLs were found. |

Use `SimpleImputer` or equivalent transformations **inside a scikit-learn pipeline**, fitted only on the training data. Never calculate imputation values using the full dataset before splitting, because that leaks test-set information into training.

## Step 5 — Feature Engineering

**Goal:** turn email text, URL data, and metadata into features that can be used consistently in training and inference.

### Candidate features

**Text features**

- Use `subject` and `body` as separate text inputs initially; also test their concatenation as a controlled comparison.
- Build TF-IDF features with a fixed vectorizer configuration. Fit the vectorizer on training text only.
- Decide how to normalize anonymization placeholders. First investigate `<|SIMBOL|>`, `<|EMOJI|>`, `<|URL|>`, `[NAME]`, `[ORGANIZATION]`, and related tokens. Keep a stable normalization rule and apply it identically at training and prediction time.
- Consider text length, word count, uppercase ratio, digit ratio, punctuation count, and the presence of URLs as complementary features. Evaluate whether these add value beyond TF-IDF.

**URL features**

- Recalculate reliable URL count, maximum/average URL length, domain/subdomain depth, and possibly the number of distinct URL hosts.
- Consider flags such as `has_url`, HTTPS presence, IP-literal host, suspicious encoding, or excessive redirects only when they can be derived reliably and without visiting live URLs.
- Ensure `url_count == 0` and missing `urls` are handled consistently.
- Never use the entire raw `urls` field as a categorical value; represent URL content through suitable parsing or text vectorization.

**Attachment and metadata features**

- Reconcile `has_attachments` and `attachment_count`; retain both only if evaluation shows complementary value.
- Parse `content_types` into interpretable flags such as `contains_html` and `contains_plain_text` instead of blindly treating each semicolon-combination as a separate category.
- Decide whether `language` is retained and whether semicolon-separated combinations should be normalized.
- Evaluate `source` carefully. It is useful for dataset diagnostics but may act as a shortcut or leakage feature, so test models both with and without it.
- Treat sender/receiver IDs or domains cautiously. They may memorize collection-specific entities and may raise privacy or generalization concerns. Compare model performance with these fields excluded.

### Design requirements

- Keep raw columns separately from derived columns during development.
- Use deterministic transformations so the same input email produces the same feature representation in training and the API.
- Document each engineered feature, definition, units, expected range, and missing-value behaviour.
- Do not engineer features from `label` or from any information unavailable at prediction time.

## Step 6 — Train/Test Split and Feature Selection

**Goal:** choose a feature set that improves generalization rather than merely fitting the dataset.

1. **Split before fitting learned preprocessing.** Make a stratified train/test split using the labelled records. Keep the test set untouched until final evaluation. If duplicates or near-duplicates occur, investigate grouping/splitting so copies of the same message cannot appear in both train and test.
2. **Build a baseline first.** Start with a simple text-only baseline (for example, TF-IDF plus Logistic Regression or Multinomial Naive Bayes). Then compare with a model that combines text and engineered metadata/URL features.
3. **Use a `ColumnTransformer`/pipeline.** Put text vectorization, categorical encoding, numeric preprocessing, imputers, and any supervised feature selection inside the pipeline. Fit these steps on the training data only and use cross-validation for tuning.
4. **Select methods that match the feature type.** For sparse TF-IDF features, consider `min_df`/`max_df`, chi-squared selection (`SelectKBest(chi2)`) where its non-negative-input assumptions are met, or regularization. For numerical features, consider mutual information, permutation importance on validation data, or model-based importance. Compare methods rather than assuming one is best.
5. **Check redundancy.** Inspect numeric-feature correlations and the relationship between `has_attachments` and `attachment_count`. Redundancy is not automatically harmful, but it should be understood.
6. **Run leakage checks.** Compare results with and without `source`, sender/receiver identifiers, suspicious timestamps, and highly class-associated placeholder artefacts. Large performance drops can indicate that the removed feature was acting as a shortcut; investigate rather than automatically restoring it.
7. **Evaluate beyond accuracy.** Report precision, recall, F1, and confusion matrix; for phishing detection, pay particular attention to phishing recall and false positives. Use a validation set or cross-validation to choose the decision threshold. Report the final test results only after choices are locked.
8. **Check robustness.** Where possible, evaluate on a source-held-out split or another collection to see whether performance generalizes across `trec5`, `trec6`, and `trec7`. A random split alone can overstate performance if similar/source-specific messages occur in both partitions.

### Suggested experiment sequence

| Experiment | Input features | Purpose |
|---|---|---|
| Baseline A | TF-IDF of `subject` | Establish a simple subject-only baseline |
| Baseline B | TF-IDF of `body` | Measure body text contribution |
| Model C | TF-IDF of subject + body | Test combined text features |
| Model D | Text + validated URL/numeric features | Test whether structured features add value |
| Model E | Model D without `source` and sender/receiver identifiers | Check for source/entity shortcuts |
| Model F | Best robust feature set with cross-validation and tuning | Select final pipeline |

Do not decide final features from the full dataset before splitting. Feature selection is part of model training and belongs inside the validation process.

## 12. Recommended Priority Order

1. Finish the outstanding EDA comparisons: numeric features by label, attachment presence by label, and source by label.
2. Audit the strange timestamps, URL outliers, placeholder conventions, and duplicate records.
3. Create a cleaned modelling copy and document each change.
4. Handle missingness per field semantics and build a reproducible preprocessing pipeline.
5. Engineer validated text, URL, and metadata features.
6. Establish text-only baselines, then compare with combined features.
7. Select/tune features within cross-validation, check leakage/generalization, and lock the test set for final evaluation.

## 13. Conclusion

This initial EDA suggests that the dataset is large enough for meaningful experiments and has a manageable class distribution. The most important work before modelling is not aggressive outlier removal; it is understanding **what missing values mean, whether URL features are calculated correctly, why date values are implausible, and whether placeholder/source artefacts could create leakage**.

Once those issues are documented and the outstanding target comparisons are complete, the project can move into cleaning, missing-value handling, feature engineering, and model selection with a much more reliable foundation.
