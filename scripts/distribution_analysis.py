import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

INPUT_FILE = "data/raw/delivery_profiling_dataset.xlsx"
OUTPUT_DIR = "output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_excel(INPUT_FILE)

print("Dataset loaded successfully")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")

numeric_columns = [
    "delivery_time_min",
    "sla_limit_min",
    "refund_amount"
]

for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

statistics = []

for column in numeric_columns:
    series = df[column].dropna()

    statistics.append({
        "column": column,
        "count": len(series),
        "mean": series.mean(),
        "median": series.median(),
        "std": series.std(),
        "min": series.min(),
        "max": series.max()
    })

stats_df = pd.DataFrame(statistics)

print("\nDescriptive Statistics:")
print(stats_df)

distribution_results = []

for column in numeric_columns:
    series = df[column].dropna()

    skewness = stats.skew(series)
    kurtosis = stats.kurtosis(series)

    distribution_results.append({
        "column": column,
        "skewness": skewness,
        "kurtosis": kurtosis
    })

distribution_df = pd.DataFrame(distribution_results)

print("\nDistribution Statistics:")
print(distribution_df)

final_statistics = stats_df.merge(
    distribution_df,
    on="column"
)

print("\nFinal Distribution Analysis:")
print(final_statistics)

final_statistics.to_csv(
    os.path.join(OUTPUT_DIR, "distribution_statistics.csv"),
    index=False
)

#Creating a histograms
plt.figure(figsize=(10, 5))

plt.hist(
    df["delivery_time_min"].dropna(),
    bins=10,
    edgecolor="black"
)

plt.xlabel("Delivery Time (minutes)")
plt.ylabel("Number of Deliveries")
plt.title("Delivery Time Distribution")

plt.tight_layout()

plt.savefig(
    os.path.join(OUTPUT_DIR, "delivery_time_distribution.png")
)

plt.close()

plt.figure(figsize=(10, 5))

plt.hist(
    df["refund_amount"].dropna(),
    bins=10,
    edgecolor="black"
)

plt.xlabel("Refund Amount")
plt.ylabel("Number of Deliveries")
plt.title("Refund Amount Distribution")

plt.tight_layout()

plt.savefig(
    os.path.join(OUTPUT_DIR, "refund_distribution.png")
)

plt.close()


plt.figure(figsize=(10, 5))

df["delivery_time_min"].dropna().plot(
    kind="density"
)

plt.xlabel("Delivery Time (minutes)")
plt.title("Delivery Time Distribution - KDE")

plt.tight_layout()

plt.savefig(
    os.path.join(OUTPUT_DIR, "delivery_time_kde.png")
)

plt.close()

plt.figure(figsize=(10, 5))

#Compare delivery time by city

cities = df["city"].dropna().unique()

for city in cities:
    city_data = df[df["city"] == city]["delivery_time_min"].dropna()

    plt.hist(
        city_data,
        bins=8,
        alpha=0.4,
        label=city
    )

plt.xlabel("Delivery Time (minutes)")
plt.ylabel("Number of Deliveries")
plt.title("Delivery Time Distribution by City")
plt.legend()

plt.tight_layout()

plt.savefig(
    os.path.join(OUTPUT_DIR, "delivery_time_by_city.png")
)

plt.close()

#Add business interpretation

print("\nBusiness Interpretation:")

for _, row in distribution_df.iterrows():

    column = row["column"]
    skewness = row["skewness"]

    print(f"\n{column}:")

    if abs(skewness) < 0.5:
        print("Distribution is approximately symmetric.")

    elif skewness >= 0.5:
        print("Distribution is positively skewed; a small number of high values may affect the mean.")

    else:
        print("Distribution is negatively skewed; a small number of low values may affect the mean.")


# Adding a mean vs median comparison
for column in numeric_columns:

    mean_value = df[column].mean()
    median_value = df[column].median()

    print(
        f"{column}: "
        f"Mean = {mean_value:.2f}, "
        f"Median = {median_value:.2f}"
    )

#success message
print("\nDistribution analysis completed successfully.")

print("\nGenerated files:")
print("output/distribution_statistics.csv")
print("output/delivery_time_distribution.png")
print("output/refund_distribution.png")
print("output/delivery_time_kde.png")
print("output/delivery_time_by_city.png")