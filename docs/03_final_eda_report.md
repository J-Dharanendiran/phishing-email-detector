# Exploratory Data Analysis (EDA) Report

## Spam & Phishing Email Detection

### 1. Introduction

Exploratory Data Analysis (EDA) was performed to understand the structure, distribution, and characteristics of the email dataset used to develop the Spam & Phishing Detector.

The analysis focuses on identifying patterns in email metadata, URL characteristics, attachment information, email content, and categorical features. Relationships between these features and the target label were investigated to identify potentially useful predictors and data quality concerns before feature selection and model development.

**Target variable:**

* `0`: Benign email
* `1`: Phishing email

The analysis was conducted using Python, Pandas, NumPy, Matplotlib, and Seaborn.

### 2. Dataset Overview

The dataset contains **108,684 email records and 21 columns**.

The features cover sender and receiver information, timestamps, subject lines, email bodies, URL statistics, attachment metadata, language, source, and the target label.

| Property                            | Value   |
| ----------------------------------- | ------- |
| Total records                       | 108,684 |
| Total columns                       | 21      |
| Benign emails (label 0)             | 60,650  |
| Phishing emails (label 1)           | 48,034  |
| Benign email percentage             | 55.8%   |
| Phishing email percentage           | 44.2%   |
| Numerical columns, including target | 7       |
| Boolean columns                     | 2       |
| Target variable                     | `label` |

The dataset contains more benign emails than phishing emails, but the difference is not extreme. Both classes have substantial representation.

Therefore, the target distribution does not indicate a severe class imbalance. Nevertheless, model evaluation should include precision, recall, F1-score, and a confusion matrix rather than relying solely on accuracy.

### 3. Data Types and Missing Values

The dataset contains:

* String-based features, including `sender`, `receiver`, `subject`, `body`, `content_types`, `language`, and `source`.
* Numerical features, including URL statistics and attachment counts.
* Boolean features, including `has_url` and `has_attachments`.
* A numerical target variable, `label`.

The missing-value summary produced by Pandas reported zero missing values across all 21 columns.

However, the dataset previously underwent missing-value handling, including replacing missing URL information with empty strings or placeholders.

Consequently, zero values from `isnull().sum()` establish only that Pandas did not detect actual null values in the loaded DataFrame. They do not establish that every field contains meaningful information.

Empty strings, placeholder values such as `unknown`, and sentinel values such as `[NO URL]` must be interpreted according to their meaning.

### 4. Numerical Feature Analysis

The following numerical features were examined:

* `url_count`
* `url_length_max`
* `url_length_avg`
* `url_subdom_max`
* `url_subdom_avg`
* `attachment_count`

#### 4.1 Descriptive Statistics

| Feature            |  Mean | Median | Maximum |
| ------------------ | ----: | -----: | ------: |
| `url_count`        |  3.31 |   1.00 |     553 |
| `url_length_max`   | 31.37 |   0.00 |  66,647 |
| `url_length_avg`   | 26.69 |   0.00 |  66,647 |
| `url_subdom_max`   |  0.66 |   0.00 |       5 |
| `url_subdom_avg`   |  0.59 |   0.00 |       5 |
| `attachment_count` | 0.021 |   0.00 |      61 |

The URL-related features exhibit substantial differences between their means and medians. This suggests skewed distributions and the presence of extreme observations.

The maximum URL length of 66,647 characters and maximum URL count of 553 warrant further investigation.

These observations should not automatically be removed as outliers. They must first be checked for data extraction errors, unusual but valid emails, and potential effects on model training.

The median attachment count is zero, indicating that at least half of the observations contain no recorded attachments.

#### 4.2 Numerical Features by Target Label

The class-wise summary revealed the following patterns:

| Feature            | Benign Mean (0) | Phishing Mean (1) |
| ------------------ | --------------: | ----------------: |
| `url_count`        |            2.73 |              4.04 |
| `url_length_max`   |           24.19 |             40.44 |
| `url_length_avg`   |           19.78 |             35.42 |
| `url_subdom_max`   |            0.51 |              0.85 |
| `url_subdom_avg`   |            0.46 |              0.75 |
| `attachment_count` |           0.035 |             0.003 |

On average, phishing emails have higher URL counts, URL lengths, and subdomain statistics in this dataset.

Attachment counts show the opposite pattern, with a higher mean among benign emails.

These are descriptive differences between the two classes. They do not establish that any individual feature can reliably distinguish phishing from benign emails.

### 5. Correlation Analysis

Pearson correlation was used to investigate the linear relationships between numerical features and the target label.

#### 5.1 Correlation with the Target

| Rank | Feature            | Pearson Correlation |
| ---: | ------------------ | ------------------: |
|    1 | `has_url`          |             +0.4145 |
|    2 | `url_subdom_max`   |             +0.2130 |
|    3 | `url_subdom_avg`   |             +0.1997 |
|    4 | `url_count`        |             +0.0623 |
|    5 | `attachment_count` |             -0.0582 |
|    6 | `url_length_max`   |             +0.0394 |
|    7 | `url_length_avg`   |             +0.0381 |

The strongest observed linear association is between `has_url` and the target label.

The positive correlation indicates that URL presence is associated with label 1, which represents phishing, in this dataset.

The subdomain features show weaker positive associations. URL count, URL lengths, and attachment count have relatively small Pearson correlation coefficients.

These results suggest that URL presence and subdomain characteristics deserve further investigation during feature selection.

However, low Pearson correlation does not necessarily mean that a feature lacks predictive value. Nonlinear relationships and interactions between features may still be useful to a machine learning model.

#### 5.2 Relationships Between Numerical Features

The numerical correlation heatmap identified potentially redundant features.

The observed correlations included:

* `url_length_max` and `url_length_avg`: approximately 1.00.
* `url_subdom_max` and `url_subdom_avg`: approximately 0.96.

The first pair appears to have an extremely strong linear relationship, while the second pair also shows a strong positive relationship.

The exact correlation between the URL length features should be checked before concluding that they contain identical information. Correlation values displayed to two decimal places may conceal small differences.

These relationships should be considered during feature selection, but correlated features should not automatically be removed without evaluating their contribution to model performance.

### 6. URL Presence Analysis

The relationship between URL presence and the target label was examined using cross-tabulation.

| Target Class |          No URL |    Contains URL |
| ------------ | --------------: | --------------: |
| Benign (0)   | 35,912 (59.21%) | 24,738 (40.79%) |
| Phishing (1) |  8,720 (18.15%) | 39,314 (81.85%) |

The percentages are calculated within each target class.

URL presence differs substantially between the two classes. Approximately 81.85% of phishing emails contain URLs, compared with 40.79% of benign emails.

This observation is consistent with the positive Pearson correlation of 0.4145 between `has_url` and the target label.

However, URL presence alone cannot determine whether an email is malicious because benign emails can also contain URLs.

The feature should therefore be evaluated as part of a broader detection system.

### 7. Attachment Analysis

The attachment-presence distribution was also compared across the target classes.

| Target Class | No Attachments | Has Attachments |
| ------------ | -------------: | --------------: |
| Benign (0)   |         97.37% |           2.63% |
| Phishing (1) |         99.85% |           0.15% |

In this dataset, recorded attachments are more prevalent among benign emails than phishing emails.

This finding is also consistent with the negative correlation between `attachment_count` and the target label.

However, the result should not be generalized to all phishing emails. The observed distribution may depend on the dataset's composition, collection process, and attachment extraction methodology.

### 8. Email Text-Length Analysis

Three additional features were examined:

* `subject_length`
* `body_length`
* `body_word_count`

These were derived from the subject and body text for exploratory analysis.

#### 8.1 Descriptive Statistics

| Feature           |     Mean | Median | Maximum |
| ----------------- | -------: | -----: | ------: |
| `subject_length`  |    42.20 |     32 |   3,701 |
| `body_length`     | 1,168.11 |    797 |  30,574 |
| `body_word_count` |   171.74 |    121 |   1,199 |

The distributions indicate substantial variation in email subject and body lengths.

Some observations have exceptionally long subjects or bodies. These records should be investigated before deciding whether any transformation or outlier treatment is appropriate.

#### 8.2 Text Length by Target Label

| Feature           | Benign Mean (0) | Phishing Mean (1) | Benign Median (0) | Phishing Median (1) |
| ----------------- | --------------: | ----------------: | ----------------: | ------------------: |
| `subject_length`  |           36.15 |             49.84 |                31 |                  32 |
| `body_length`     |        1,147.74 |          1,193.83 |               811 |                 783 |
| `body_word_count` |          170.94 |            172.76 |               123 |                 116 |

The mean subject length is higher for phishing emails, although the median subject lengths are relatively similar.

Mean body length and word count are also similar across the two classes.

These findings suggest that basic email length statistics alone may not provide a complete distinction between benign and phishing emails. Further evaluation is necessary to determine whether these features contribute to predictive performance.

### 9. Categorical Feature Analysis

The following categorical features were investigated:

* `sender_domain`
* `receiver_domain`
* `language`
* `source`
* `content_types`
* `attachment_types`

Frequency distributions, target cross-tabulations, and selected visualizations were used to investigate category patterns.

#### 9.1 Content Types

The most common content-type values were:

| Content Type            | Number of Records |
| ----------------------- | ----------------: |
| `text/plain`            |            70,992 |
| `text/plain;text/html`  |            21,173 |
| `text/html`             |            15,270 |
| `text/plain;text/plain` |               989 |

The target distribution within selected categories was:

| Content Type           | Benign (0) | Phishing (1) |
| ---------------------- | ---------: | -----------: |
| `text/html`            |     12.73% |       87.27% |
| `text/plain`           |     76.94% |       23.06% |
| `text/plain;text/html` |     13.95% |       86.05% |

These percentages represent the distribution of target labels within each content-type category.

The `text/html` and `text/plain;text/html` categories have a higher proportion of phishing emails in this dataset. In contrast, `text/plain` is predominantly associated with benign emails.

This pattern indicates that content type may contain useful information for distinguishing the target classes.

Nevertheless, categories with very few observations can produce extreme percentages. For example, a category containing one observation may show a 100% proportion for one class without providing sufficient evidence of a general pattern.

Rare categories should be handled carefully during feature engineering and model evaluation.

#### 9.2 Source

The dataset contains three source categories: `trec5`, `trec6`, and `trec7`.

| Source  | Total Records |      Benign (0) |    Phishing (1) |
| ------- | ------------: | --------------: | --------------: |
| `trec5` |        49,583 | 29,929 (60.36%) | 19,654 (39.64%) |
| `trec6` |        15,005 | 11,208 (74.70%) |  3,797 (25.30%) |
| `trec7` |        44,096 | 19,513 (44.25%) | 24,583 (55.75%) |

The label distribution differs across the three sources.

In particular, `trec6` has a higher proportion of benign emails, while `trec7` has a higher proportion of phishing emails.

This difference may reflect variation in the source datasets or collection processes.

The `source` feature requires special attention because a model might learn source-specific patterns instead of generalizable phishing characteristics.

If the source identifier will not be available for real-world predictions, it should not be included as an ordinary predictive feature without a clear justification.

#### 9.3 Sender Domains

The sender-domain analysis identified substantial differences in class counts among frequent domains.

Examples include:

| Sender Domain | Benign (0) | Phishing (1) |
| ------------- | ---------: | -----------: |
| `enron.com`   |     21,660 |           24 |
| `gmail.com`   |      2,784 |          125 |
| `hotmail.com` |        704 |          838 |
| `msn.com`     |        179 |          307 |
| `unknown`     |        143 |          351 |
| `yahoo.co.kr` |          0 |          565 |

These counts indicate that the target distribution varies considerably across the selected sender domains.

However, these observations do not establish the general safety or maliciousness of any domain.

Domain-based features may also encourage the model to memorize patterns specific to the training dataset. Their usefulness should therefore be evaluated using a validation strategy that accounts for repeated campaigns, related emails, and potential overlap between training and test data.

#### 9.4 Receiver Domains

The receiver-domain analysis also revealed substantial differences between target classes.

Examples include:

| Receiver Domain       | Benign (0) | Phishing (1) |
| --------------------- | ---------: | -----------: |
| `plg.uwaterloo.ca`    |          0 |        6,931 |
| `flax9.uwaterloo.ca`  |      2,139 |        7,729 |
| `speedy.uwaterloo.ca` |        841 |        5,224 |
| `samba.org`           |      2,368 |            0 |
| `enron.com`           |     15,723 |       15,122 |
| `unknown`             |        922 |        1,449 |

Some receiver domains are strongly associated with one target class in the observed data.

These differences may reflect dataset composition, communication patterns, or source-specific collection procedures. They should not be interpreted as evidence that a recipient domain is inherently malicious or trustworthy.

Receiver-domain features should be evaluated carefully for generalization and potential data leakage.

#### 9.5 Language and Attachment Types

English-related language values dominate the dataset. The most frequent language categories include `en` and `en;en`.

The `attachment_types` column is dominated by the `none` category, which appears in 107,018 records.

These distributions indicate that some categorical features are highly concentrated in a small number of categories.

Rare language and attachment categories should be examined before encoding. Depending on the modeling strategy, infrequent categories may require grouping or other preprocessing.

### 10. Categorical Association Using Cramér's V

Cramér's V was used to investigate associations between selected categorical features and the target label.

The reported results were:

| Feature         | Cramér's V |
| --------------- | ---------: |
| `content_types` |     0.6086 |
| `source`        |     0.2140 |

`content_types` exhibits a substantially stronger association with the target than `source` among the features evaluated.

Cramér's V measures the strength of association between categorical variables. It does not indicate which target class is more prevalent, nor does it represent the percentage of phishing emails.

The direction of the relationship must be examined using the category-wise target distributions.

The current analysis calculates Cramér's V only for categorical features with at most 50 unique values. Consequently, these results do not constitute a complete ranking of all categorical features. Sender and receiver domains may be excluded because of their high cardinality.

The reported values should be interpreted as exploratory findings rather than definitive measures of predictive importance.

### 11. Key Findings

The main findings from the EDA are summarized below.

**1. Target distribution**

The dataset contains 60,650 benign emails and 48,034 phishing emails. Both classes are sufficiently represented for further supervised learning experiments.

**2. URL presence**

URL presence has the strongest observed Pearson correlation with the target among the examined numerical and Boolean features, with a coefficient of +0.4145.

Phishing emails are more likely to contain URLs in this dataset than benign emails.

**3. URL subdomain characteristics**

The maximum and average subdomain features have positive associations with the target. Their contribution should be evaluated during model development.

**4. Numerical feature distributions**

URL statistics and attachment counts exhibit skewed distributions and extreme values. These observations warrant investigation before deciding on transformations or outlier treatment.

**5. Content types**

Content type has a relatively strong association with the target, with a reported Cramér's V of 0.6086. HTML-related categories contain higher proportions of phishing emails in the observed data.

**6. Source-related patterns**

The target distribution differs substantially across `trec5`, `trec6`, and `trec7`. This raises a potential concern about source-related shortcuts and generalization.

**7. Email domains**

Sender and receiver domains exhibit different class distributions. Their predictive usefulness must be evaluated carefully to avoid domain memorization and misleading validation performance.

**8. Text-length features**

Phishing emails have longer average subject lines in this dataset, but body-length and word-count statistics are relatively similar across classes. Their usefulness remains to be established experimentally.

**9. Attachment information**

Attachments are uncommon in both classes and are less frequent among phishing emails in this dataset. Attachment presence alone should not be treated as a reliable indicator of maliciousness.

**10. Potential feature redundancy**

The URL length and subdomain feature pairs show strong correlations with one another. Their redundancy should be investigated during feature selection.

### 12. Limitations and Risks

The following limitations should be considered before model development:

* Observed associations may reflect the dataset's composition rather than general phishing behavior.
* High-cardinality domain features may encourage memorization.
* Source-related patterns may create shortcuts that do not generalize to unseen data.
* Rare categories can produce misleadingly extreme target percentages.
* Extreme URL statistics may reflect valid observations, extraction artifacts, or data quality issues.
* Pearson correlation captures linear relationships and may miss nonlinear predictive patterns.
* Cramér's V measures categorical association rather than predictive performance.
* Zero actual missing values do not establish that every field contains meaningful data.
* The current EDA does not establish causal relationships between features and phishing.
* No final predictive performance conclusions can be drawn from EDA alone.

These limitations should inform the feature-selection strategy, data-splitting procedure, and evaluation methodology.

### 13. Recommendations for the Next Stage

The following steps are recommended before final model development.

**Step 1: Finalize data-quality checks**

Investigate extreme URL values, rare categories, and placeholder values. Confirm that derived features are consistent with their underlying data.

**Step 2: Review candidate features**

Consider URL presence, URL subdomain statistics, content types, and selected email text features as candidates for further evaluation.

Do not automatically remove features with weak correlations or retain features solely because they have strong associations.

**Step 3: Review potential leakage**

Investigate source identifiers, domains, duplicated messages, and related email campaigns. Ensure that the evaluation split reflects the intended real-world use case.

**Step 4: Prepare the feature-processing pipeline**

Handle text, categorical variables, numerical features, and Boolean indicators using suitable preprocessing steps.

For a combined model, ensure that the text and metadata transformations are fitted using training data only.

**Step 5: Establish a baseline model**

Train an appropriate baseline and evaluate it using a held-out validation or test set.

For a text-based baseline, a TF-IDF vectorizer combined with Multinomial Naive Bayes is a reasonable candidate. A metadata-based model and a combined model can subsequently be evaluated for comparison.

**Step 6: Evaluate generalization**

Use precision, recall, F1-score, a confusion matrix, and other appropriate metrics. Consider stratified splitting and, where necessary, grouping or time-based splitting to reduce leakage from related emails.

**Step 7: Compare feature sets**

Evaluate text-only, metadata-only, and combined approaches under comparable validation conditions. Use the results to make evidence-based feature-selection decisions.

### 14. Conclusion

The EDA identified meaningful differences between benign and phishing emails in URL presence, URL subdomain characteristics, email content types, source distributions, and domain frequencies.

Among the analyzed features, `has_url` has the strongest observed Pearson correlation with the target, while `content_types` has the strongest reported Cramér's V among the categorical features evaluated.

The analysis also identified potential feature redundancy, extreme numerical values, rare categories, and source-related patterns that warrant further investigation.

These findings provide a foundation for feature selection and baseline model development. However, the predictive value and generalizability of the identified features must be established through controlled model evaluation rather than inferred from EDA alone.
