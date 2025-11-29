import pandas as pd
import requests
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import os
import time
import numpy as np

# -----------------------------
# CONFIG
# -----------------------------
API_URL = "http://localhost:8000/check"
csv_file = "results/vesuvio-outdoor-above-night-2.csv"  # Replace with your SQL export

# Create folders
os.makedirs("results/plots", exist_ok=True)

# -----------------------------
# Load CSV
# -----------------------------
df = pd.read_csv(csv_file)

# -----------------------------
# Helper: Call API with timing
# -----------------------------
def call_api(width_m, riser_m, tread_m):
    payload = {
        "step_height": riser_m,   # riser
        "step_depth": tread_m,    # tread
        "step_width": width_m,     # width
        "stair_parts": 0,
        "risers": 0,
        "treads": 0
    }
    start_time = time.time()
    r = requests.post(API_URL, json=payload)
    r.raise_for_status()
    elapsed = time.time() - start_time
    return r.json()["compliance"], elapsed

# -----------------------------
# Compute compliance and API timing
# -----------------------------
gt_width_ok, gt_tread_ok, gt_riser_tread_ok = [], [], []
alg_width_ok, alg_tread_ok, alg_riser_tread_ok = [], [], []

gt_time_s, alg_time_s = [], []

for _, row in df.iterrows():

    # --- Ground truth values (mm → m) ---
    w_gt = row["width_gt_mm"] / 1000
    r_gt = row["riser_gt_mm"] / 1000
    t_gt = row["tread_gt_mm"] / 1000

    gt_res, gt_elapsed = call_api(w_gt, r_gt, t_gt)
    gt_time_s.append(gt_elapsed)

    gt_width_ok.append(gt_res["width_ok"])
    gt_tread_ok.append(gt_res["tread_ok"])
    gt_riser_tread_ok.append(gt_res["riser_tread_relation_ok"])

    # --- Algorithm-predicted values (mm → m) ---
    w_alg = row["width_alg_mm"] / 1000
    r_alg = row["riser_alg_mm"] / 1000
    t_alg = row["tread_alg_mm"] / 1000

    alg_res, alg_elapsed = call_api(w_alg, r_alg, t_alg)
    alg_time_s.append(alg_elapsed)

    alg_width_ok.append(alg_res["width_ok"])
    alg_tread_ok.append(alg_res["tread_ok"])
    alg_riser_tread_ok.append(alg_res["riser_tread_relation_ok"])

# Add compliance to dataframe
df["gt_width_ok"] = gt_width_ok
df["gt_tread_ok"] = gt_tread_ok
df["gt_riser_tread_relation_ok"] = gt_riser_tread_ok
df["alg_width_ok"] = alg_width_ok
df["alg_tread_ok"] = alg_tread_ok
df["alg_riser_tread_relation_ok"] = alg_riser_tread_ok

# Add timing info
df["gt_api_time_s"] = gt_time_s
df["alg_api_time_s"] = alg_time_s

# -----------------------------
# Helper to save confusion matrices
# -----------------------------
def save_confusion_matrix(gt, pred, title, filename):
    cm = confusion_matrix(gt, pred, labels=[True, False])
    cm_percent = np.where(cm.sum(axis=1, keepdims=True) == 0, 0, cm / cm.sum(axis=1, keepdims=True) * 100)


    disp = ConfusionMatrixDisplay(confusion_matrix=cm_percent)
    plt.figure(figsize=(6, 6))
    disp.plot(colorbar=True)
    disp.plot(values_format=".1f")  # shows percentages with 1 decimal
    plt.title(title)
    plt.tight_layout()
    plt.savefig(f"results/plots/{filename}.pdf")
    plt.close()

# -----------------------------
# Save confusion matrices
# -----------------------------
save_confusion_matrix(df["gt_width_ok"], df["alg_width_ok"],
                      "Width Compliance (GT vs ALG)", "confusion_width_ok")

save_confusion_matrix(df["gt_tread_ok"], df["alg_tread_ok"],
                      "Tread Compliance (GT vs ALG)", "confusion_tread_ok")

save_confusion_matrix(df["gt_riser_tread_relation_ok"], df["alg_riser_tread_relation_ok"],
                      "Riser–Tread Relation Compliance (GT vs ALG)", "confusion_riser_tread_relation_ok")

# -----------------------------
# Plot API response times
# -----------------------------
plt.figure(figsize=(8,6))
plt.bar(range(len(df)), df["gt_api_time_s"], label="GT API time", alpha=0.7)
plt.bar(range(len(df)), df["alg_api_time_s"], label="ALG API time", alpha=0.7)
plt.xlabel("Staircase Index")
plt.ylabel("API Response Time (s)")
plt.title("API Response Time per Staircase")
plt.legend()
plt.tight_layout()
plt.savefig("results/plots/api_response_times.pdf")
plt.close()

print("All confusion matrices and API response time plots saved in results/plots/")



from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# -----------------------------
# Helper to calculate metrics
# -----------------------------
def classification_metrics(gt, pred):
    accuracy = accuracy_score(gt, pred)
    precision = precision_score(gt, pred)
    recall = recall_score(gt, pred)
    f1 = f1_score(gt, pred)
    return accuracy, precision, recall, f1

# -----------------------------
# Compute metrics for all compliance types
# -----------------------------
metrics_results = {}

for name, gt_col, alg_col in [
    ("Width compliance", "gt_width_ok", "alg_width_ok"),
    ("Tread compliance", "gt_tread_ok", "alg_tread_ok"),
    ("Riser–Tread relation", "gt_riser_tread_relation_ok", "alg_riser_tread_relation_ok")
]:
    acc, prec, rec, f1 = classification_metrics(df[gt_col], df[alg_col])
    metrics_results[name] = {
        "Accuracy": acc,
        "Precision": prec,
        "Recall": rec,
        "F1-score": f1
    }

# -----------------------------
# Print metrics
# -----------------------------
for name, vals in metrics_results.items():
    print(f"{name}:")
    for metric_name, value in vals.items():
        print(f"  {metric_name}: {value:.3f}")


# quantify deviation of compliant examples from blondel rule
import seaborn as sns
import matplotlib.pyplot as plt

# Compute riser-tread sum
df['blondel_sum_gt'] = 2*df['riser_gt_mm']/100 + df['tread_gt_mm']/100  # cm
df['blondel_sum_alg'] = 2*df['riser_alg_mm']/100 + df['tread_alg_mm']/100  # cm

# Keep only rows where GT is compliant
df_compliant = df[(df['blondel_sum_gt'] >= 62) & (df['blondel_sum_gt'] <= 64)].copy()

# Compute deviation for ALG
df_compliant['blondel_dev_alg'] = df_compliant['blondel_sum_alg'].apply(
    lambda x: 0 if 62 <= x <= 64 else min(abs(x-62), abs(x-64))
)

# Keep only rows where ALG is actually violating Blondel
df_negative = df[(df['blondel_sum_gt'] >= 62) & (df['blondel_sum_gt'] <= 64) & 
                 ((df['blondel_sum_alg'] < 62) | (df['blondel_sum_alg'] > 64))]
df_negative['blondel_dev_alg'] = df_negative['blondel_sum_alg'].apply(lambda x: min(abs(x-62), abs(x-64)))

# print(df_negative.head())
# Plot
plt.figure(figsize=(12,6))
sns.barplot(data=df_negative, x='staircase_name', y='blondel_dev_alg', color='salmon')
plt.xticks(rotation=90)
plt.ylabel("Deviation from Blondel range (cm)")
plt.xlabel("Staircase")
plt.title("Blondel Deviation per Staircase (GT Compliant, ALG Non-Compliant Only)")
plt.tight_layout()
plt.savefig("results/plots/blondel_deviation_negative_only.pdf")
plt.close()
