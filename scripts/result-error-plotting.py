import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
plt.rcParams.update({
    'font.size': 22,            # default text size
    'axes.titlesize': 24,       # plot title
    'axes.labelsize': 22,       # x/y labels
    'xtick.labelsize': 16,      # x tick labels
    'ytick.labelsize': 18,      # y tick labels
    'legend.fontsize': 20,      # legend text
})
# -----------------------------
# 1. Load your CSV
# -----------------------------
csv_file = "results/top-down-combined.csv"  # Replace with your SQL export
outputfileName = csv_file.split('/')[0] + "/" + csv_file.split('/')[1].split(".")[0]


df = pd.read_csv(csv_file)
print(df.head())

# Ensure staircase_name is treated as categorical for plotting
df['staircase_name'] = df['staircase_name'].astype(str)

# Create output folder for plots
os.makedirs(f"{outputfileName}", exist_ok=True)

df['idx'] = range(len(df))
# -----------------------------
# 2. Bar Plot: Absolute Errors
# -----------------------------
dimensions = ['width', 'riser', 'tread']
for dim in dimensions:
    plt.figure(figsize=(12,6))
    ax = sns.histplot(data=df, x=f'{dim}_abs_error', kde=False)
    # plt.xticks(rotation=90)
    # ax.set_xticklabels([])     # ← remove tick labels
    ax.tick_params(axis='x', labelsize=24)
    ax.tick_params(axis='y', labelsize=24)
    ax.set_ylabel(f"freqency", fontsize=28)
    ax.set_xlabel("error range (mm)", fontsize=28)
    ax.set_title(f"Abs Error histogram - {dim.capitalize()}", fontsize=30)
    plt.tight_layout()
    plt.savefig(f"{outputfileName}/{dim}_abs_error.pdf")  # PDF for LaTeX
    plt.close()

# -----------------------------
# 3. Box Plot: Error Distribution
# -----------------------------
for dim in dimensions:
    plt.figure(figsize=(6,6))
    sns.boxplot(data=df, y=f'{dim}_abs_error', color='skyblue')
    plt.ylabel(f"{dim.capitalize()} Absolute Error (mm)")
    plt.title(f"{dim.capitalize()} Error Distribution")
    plt.tight_layout()
    plt.savefig(f"{outputfileName}/{dim}_boxplot.pdf")
    plt.close()

# -----------------------------
# 4. Scatter Plot: Measured vs GT
# -----------------------------
# Optional: if you have GT and measured columns in mm
for dim in dimensions:
    plt.figure(figsize=(6,6))
    plt.scatter(df[f'{dim}_gt_mm'], df[f'{dim}_alg_mm'], alpha=0.7)
    max_val = max(df[f'{dim}_gt_mm'].max(), df[f'{dim}_alg_mm'].max())
    plt.plot([0,max_val], [0,max_val], 'r--', label='Ideal')
    plt.xlabel("Ground Truth (mm)")
    plt.ylabel("Measured (mm)")
    plt.title(f"{dim.capitalize()}: Measured vs GT")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{outputfileName}/{dim}_scatter.pdf")
    plt.close()


# ------------------------------------
# 5. Step Count Error Calculations
# ------------------------------------
df['tread_count_abs_error'] = (df['treads_alg'] - df['gt_num_steps']).abs()
df['riser_count_abs_error'] = (df['risers_alg'] - df['gt_num_steps']).abs()

df['tread_count_pct_error'] = df['tread_count_abs_error'] / df['gt_num_steps'] * 100
df['riser_count_pct_error'] = df['riser_count_abs_error'] / df['gt_num_steps'] * 100
# ------------------------------------
# Bar Plots for Step Count Errors
# ------------------------------------
step_metrics = {
    'tread_count_abs_error': "Tread Count Abs(e)",
    'riser_count_abs_error': "Riser Count Abs(e)"
}

for col, title in step_metrics.items():
    plt.figure(figsize=(12,6))
    ax = sns.histplot(data=df, x=col, kde=False, palette='viridis')

    # ax.set_xticks([])          # ← remove tick marks
    # ax.set_xticklabels([])     # ← remove tick labels
    ax.tick_params(axis='x', labelsize=24)
    ax.tick_params(axis='y', labelsize=24)
    ax.set_ylabel(f"freqency", fontsize=28)
    ax.set_xlabel("error range (count)", fontsize=28)
    ax.set_title(f"{title} - Histogram", fontsize=30)
    plt.tight_layout()
    plt.savefig(f"{outputfileName}/{col}.pdf")
    plt.close()

# ------------------------------------
# Boxplots for Step Count Error
# ------------------------------------
for col, title in step_metrics.items():
    plt.figure(figsize=(6,6))
    ax = sns.boxplot(data=df, y=col, color='skyblue')
    ax.set_xticklabels([])     # ← remove tick labels
    plt.ylabel("Error (steps)")
    plt.title(f"{title}")
    plt.tight_layout()
    plt.savefig(f"{outputfileName}/{col}_boxplot.pdf")
    plt.close()

# ------------------------------------
# Boxplots for Step Count Error
# ------------------------------------
for col, title in step_metrics.items():
    plt.figure(figsize=(6,6))
    sns.boxplot(data=df, y=col, color='skyblue')
    plt.ylabel("Error (steps)")
    plt.title(f"{title}")
    plt.tight_layout()
    plt.savefig(f"{outputfileName}/{col}_boxplot.pdf")
    plt.close()
