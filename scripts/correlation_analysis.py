import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# 1. Load Dataset

INPUT_FILE = "data/raw/delivery_profiling_dataset.xlsx"
OUTPUT_DIR = Path("output")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_excel(INPUT_FILE)

print("Dataset loaded successfully")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")


# 2. Select Numerical Columns

numeric_columns = [
    "delivery_time_min",
    "sla_limit_min",
    "refund_amount"
]

numeric_df = df[numeric_columns].apply(
    pd.to_numeric,
    errors="coerce"
)

print("\nNumerical columns used for correlation:")
print(numeric_columns)


# 3. Pearson Correlation


pearson_corr = numeric_df.corr(method="pearson")

print("\nPearson Correlation Matrix:")
print(pearson_corr)

pearson_corr.to_csv(
    OUTPUT_DIR / "pearson_correlation.csv"
)

# 4. Spearman Correlation


spearman_corr = numeric_df.corr(method="spearman")

print("\nSpearman Correlation Matrix:")
print(spearman_corr)

spearman_corr.to_csv(
    OUTPUT_DIR / "spearman_correlation.csv"
)

# 5. Pearson Heatmap


plt.figure(figsize=(10, 7))

sns.heatmap(
    pearson_corr,
    annot=True,
    fmt=".2f",
    center=0
)

plt.title("Pearson Correlation Matrix")
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "correlation_heatmap.png"
)

plt.close()

print("\nCorrelation heatmap saved.")

# 6. Find Strong Correlations

corr_flat = pearson_corr.unstack()

strong_correlations = []

for (var1, var2), correlation in corr_flat.items():

    # Ignore self-correlation
    if var1 == var2:
        continue

    # Avoid duplicate pairs
    if (var2, var1) in [
        (item["variable_1"], item["variable_2"])
        for item in strong_correlations
    ]:
        continue

    if abs(correlation) >= 0.7:

        strong_correlations.append({
            "variable_1": var1,
            "variable_2": var2,
            "correlation": correlation
        })


strong_df = pd.DataFrame(strong_correlations)

strong_df.to_csv(
    OUTPUT_DIR / "strong_correlations.csv",
    index=False
)

print("\nStrong correlations:")
print(strong_df)

# 7. Interpretation

print("\nCorrelation Interpretation:")

for _, row in strong_df.iterrows():

    correlation = row["correlation"]

    if correlation > 0:
        relationship = "strong positive relationship"
    else:
        relationship = "strong negative relationship"

    print(
        f"{row['variable_1']} <-> "
        f"{row['variable_2']}: "
        f"{correlation:.2f} "
        f"({relationship})"
    )

# 8. Correlation vs Causation Reminder


print("\nImportant:")
print(
    "Correlation indicates that variables move together. "
    "It does not prove that one variable causes the other."
)

print("\nCorrelation analysis completed successfully.")