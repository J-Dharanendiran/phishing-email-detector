# Feature Engineering Report

## Spam & Phishing Email Detection

## 1. Introduction

Feature engineering was performed to transform the existing email dataset into a more informative representation for machine learning.

The objective was to derive meaningful numerical and Boolean features from existing email metadata while preserving the original information wherever necessary.

The feature engineering process focused on:

* URL characteristics
* Attachment information
* Sender and receiver information
* Email content types
* Timestamp information
* Language information

The original `label` column was retained as the target variable.

| Label | Meaning        |
| ----- | -------------- |
| 0     | Benign email   |
| 1     | Phishing email |

---

## 2. URL Feature Engineering

URL-related features were examined because URLs can provide useful information about potentially suspicious email content.

### 2.1 URL Presence

An additional Boolean feature was created to represent whether an email contains at least one URL.

**Feature created:**

* `has_url_engineered`

The feature was derived from `url_count`.

```python
df['has_url_engineered'] = df['url_count'] > 0
```

This provides an explicit indicator of URL presence.

### 2.2 Log Transformation of URL Features

The URL-related numerical features exhibited highly skewed distributions and extreme values.

To reduce the influence of large values, logarithmic transformations using `np.log1p()` were applied.

**Features created:**

* `url_length_max_log`
* `url_length_avg_log`
* `url_subdom_max_log`
* `url_subdom_avg_log`

```python
df['url_length_max_log'] = np.log1p(df['url_length_max'])
df['url_length_avg_log'] = np.log1p(df['url_length_avg'])
df['url_subdom_max_log'] = np.log1p(df['url_subdom_max'])
df['url_subdom_avg_log'] = np.log1p(df['url_subdom_avg'])
```

The original numerical features were retained alongside their transformed versions.

---

## 3. Attachment Feature Engineering

Attachment information was examined to represent whether emails contain attachments and how many attachments are present.

The following features were used:

* `attachment_count`
* `has_attachments`
* `attachment_types`

### 3.1 Log Transformation

The attachment count contained a highly skewed distribution, with most emails having no recorded attachments.

A logarithmic transformation was applied.

**Feature created:**

* `attachment_count_log`

```python
df['attachment_count_log'] = np.log1p(df['attachment_count'])
```

### 3.2 Attachment Presence

An additional Boolean feature was derived from the attachment count.

**Feature created:**

* `has_attachments_engineered`

```python
df['has_attachments_engineered'] = (
    df['attachment_count'] > 0
)
```

The original attachment-related columns were retained.

---

## 4. Receiver Feature Engineering

The `receiver_domain` column can contain multiple domains separated by semicolons.

Instead of directly encoding the complete domain combinations, numerical features were derived to represent the receiver-domain structure.

### 4.1 Receiver Domain Count

Counts the number of receiver-domain entries associated with an email.

**Feature created:**

* `receiver_domain_count`

### 4.2 Unique Receiver Domain Count

Counts the number of distinct receiver domains after removing duplicates and normalizing case.

**Feature created:**

* `receiver_unique_domain_count`

### 4.3 Multiple Receiver Domains

Indicates whether an email contains more than one unique receiver domain.

**Feature created:**

* `has_multiple_receiver_domains`

```python
df['has_multiple_receiver_domains'] = (
    df['receiver_unique_domain_count'] > 1
)
```

These features provide a numerical representation of recipient-domain structure without directly encoding potentially high-cardinality combinations.

---

## 5. Email Content-Type Feature Engineering

The original `content_types` column contains information about the MIME content types present in an email.

Boolean features were derived to represent the presence of HTML and plain-text content.

### Features created

| Feature             | Description                                                     |
| ------------------- | --------------------------------------------------------------- |
| `has_html_content`  | Indicates whether HTML content is present.                      |
| `has_plain_text`    | Indicates whether plain-text content is present.                |
| `has_mixed_content` | Indicates whether both HTML and plain-text content are present. |

The features were derived using string matching.

```python
df['has_html_content'] = (
    df['content_types']
    .fillna('')
    .str.contains('text/html', case=False)
)

df['has_plain_text'] = (
    df['content_types']
    .fillna('')
    .str.contains('text/plain', case=False)
)

df['has_mixed_content'] = (
    df['has_html_content'] & df['has_plain_text']
)
```

The original `content_types` column was preserved.

---

## 6. Timestamp Feature Engineering

The original `date` column contained timestamp information represented as strings.

The column was converted into a datetime format using Pandas.

```python
df['date'] = pd.to_datetime(
    df['date'],
    errors='coerce',
    utc=True
)
```

### 6.1 Invalid Timestamp Handling

The timestamp investigation identified records with years outside the selected project-specific range of 1990–2026.

A total of 432 records were identified.

These records were not deleted. Instead, their invalid timestamps were replaced with `NaT`.

```python
invalid_date_mask = (
    (df['date'].dt.year < 1990) |
    (df['date'].dt.year > 2026)
)

df.loc[invalid_date_mask, 'date'] = pd.NaT
```

This preserved the email records while preventing the suspicious timestamps from being treated as valid dates.

### 6.2 Year Extraction

Only the year component was required for the current project.

**Feature created:**

* `date_year`

```python
df['date_year'] = df['date'].dt.year
```

The original `date` column was retained.

After handling invalid timestamps:

* Invalid timestamps remaining: 0
* Missing timestamps: 432
* Valid unique years: 28

---

## 7. Language Feature Engineering

The `language` column contains language identifiers, including records with multiple language entries separated by semicolons.

Instead of encoding every language combination directly, a numerical feature was created to represent the number of language entries.

**Feature created:**

* `language_count`

```python
df['language_count'] = (
    df['language']
    .fillna('')
    .str.split(';')
    .apply(
        lambda x: len([
            lang for lang in x
            if lang.strip()
        ])
    )
)
```

The original `language` column was retained.

The resulting distribution showed that most emails contain one or two language entries, while a small number contain several entries.

---

## 8. Summary of Engineered Features

The following table summarizes the additional features created during this stage.

| Category            | Engineered Features                                                                      |
| ------------------- | ---------------------------------------------------------------------------------------- |
| URL                 | `has_url_engineered`                                                                     |
| URL transformations | `url_length_max_log`, `url_length_avg_log`, `url_subdom_max_log`, `url_subdom_avg_log`   |
| Attachments         | `attachment_count_log`, `has_attachments_engineered`                                     |
| Receiver            | `receiver_domain_count`, `receiver_unique_domain_count`, `has_multiple_receiver_domains` |
| Content types       | `has_html_content`, `has_plain_text`, `has_mixed_content`                                |
| Timestamp           | `date_year`                                                                              |
| Language            | `language_count`                                                                         |

### Total Additional Features

**16 engineered features**

The original columns were retained wherever appropriate, allowing the original and transformed representations to be evaluated during feature selection.

---

## 9. Important Feature Engineering Decisions

Several decisions were made to preserve information and avoid unnecessary transformations.

1. **Original features were retained:** Log-transformed numerical features were added alongside their original versions.

2. **High-cardinality domains were not directly one-hot encoded:** Sender and receiver domain information requires careful encoding during model preprocessing.

3. **Timestamp records were preserved:** Invalid timestamps were converted to missing datetime values rather than deleting the corresponding email records.

4. **Multiple-value categorical columns were represented carefully:** Receiver domains and language combinations were converted into numerical structural features.

5. **Original email text was preserved:** Subject and body text remain important inputs for future text vectorization techniques such as TF-IDF.

6. **No feature was assumed to be predictive solely because it was engineered:** The usefulness of the new features will be evaluated during feature selection and model development.

---

## 10. Conclusion

Feature engineering transformed the original email metadata into additional numerical and Boolean representations.

The process covered URL characteristics, attachment information, receiver-domain structure, email content types, timestamps, and language information.

A total of 16 additional features were created while retaining the original information wherever appropriate.

The resulting dataset provides a richer feature representation for the next stages of the machine learning pipeline.

**Next Stage:** Feature Selection and Model Preparation.
