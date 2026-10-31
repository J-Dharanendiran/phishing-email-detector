from pathlib import Path
import pandas as pd

# Run this script from the project root.
candidate_paths = [
    Path("data/processed/email_cleaned.csv"),
    Path("../data/processed/email_cleaned.csv"),
]

data_path = next((path for path in candidate_paths if path.exists()), None)

if data_path is None:
    raise FileNotFoundError(
        "Could not find email_cleaned.csv. Checked:\n"
        + "\n".join(str(path.resolve()) for path in candidate_paths)
        + "\nUpdate candidate_paths in this script to your CSV location."
    )

print(f"Loading: {data_path.resolve()}")
df = pd.read_csv(data_path, low_memory=False)

print("\nDataset shape:", df.shape)
print("\nColumns and data types:")
for column, dtype in df.dtypes.items():
    print(f"{column}: {dtype}")

# Keep all columns so the verification can inspect both source fields
# and the values used during training.
if "label" in df.columns:
    pieces = []
    labels = sorted(df["label"].dropna().unique().tolist())

    for label in labels:
        group = df[df["label"] == label]
        pieces.append(group.sample(
            n=min(100, len(group)),
            random_state=42
        ))

    sample = pd.concat(pieces).sample(frac=1, random_state=42)
else:
    sample = df.sample(n=min(200, len(df)), random_state=42)

output_path = Path("data/processed/email_cleaned_verification_sample.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)
sample.to_csv(output_path, index=False)

print("\nSample shape:", sample.shape)
print("Saved sample to:", output_path.resolve())
print("\nUpload this sample CSV for the training/inference comparison.")
