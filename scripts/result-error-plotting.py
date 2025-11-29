import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# -----------------------------
# 1. Load your CSV
# -----------------------------
csv_file = "results/vesuvio-outdoor-above-night-2.csv"  # Replace with your SQL export
df = pd.read_csv(csv_file)
print(df.head())

# Ensure staircase_name is treated as categorical for plotting
df['staircase_name'] = df['staircase_name'].astype(str)

# Create output folder for plots
os.makedirs("results/plots", exist_ok=True)

# -----------------------------
# 2. Bar Plot: Absolute Errors
# -----------------------------
dimensions = ['width', 'riser', 'tread']
for dim in dimensions:
    plt.figure(figsize=(12,6))
    sns.barplot(data=df, x='staircase_name', y=f'{dim}_abs_error', palette='viridis')
    plt.xticks(rotation=90)
    plt.ylabel(f"{dim.capitalize()} Absolute Error (mm)")
    plt.xlabel("Staircase")
    plt.title(f"Absolute Error per Staircase - {dim.capitalize()}")
    plt.tight_layout()
    plt.savefig(f"results/plots/{dim}_abs_error.pdf")  # PDF for LaTeX
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
    plt.savefig(f"results/plots/{dim}_boxplot.pdf")
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
    plt.title(f"{dim.capitalize()}: Measured vs Ground Truth")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"results/plots/{dim}_scatter.pdf")
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
    'tread_count_abs_error': "Tread Count Absolute Error",
    'riser_count_abs_error': "Riser Count Absolute Error"
}

for col, title in step_metrics.items():
    plt.figure(figsize=(12,6))
    sns.barplot(data=df, x='staircase_name', y=col, palette='viridis')
    plt.xticks(rotation=90)
    plt.ylabel("Error (steps)")
    plt.xlabel("Staircase")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(f"results/plots/{col}.pdf")
    plt.close()

# ------------------------------------
# Boxplots for Step Count Error
# ------------------------------------
for col, title in step_metrics.items():
    plt.figure(figsize=(6,6))
    sns.boxplot(data=df, y=col, color='skyblue')
    plt.ylabel("Error (steps)")
    plt.title(f"{title} Distribution")
    plt.tight_layout()
    plt.savefig(f"results/plots/{col}_boxplot.pdf")
    plt.close()

# ------------------------------------
# Boxplots for Step Count Error
# ------------------------------------
for col, title in step_metrics.items():
    plt.figure(figsize=(6,6))
    sns.boxplot(data=df, y=col, color='skyblue')
    plt.ylabel("Error (steps)")
    plt.title(f"{title} Distribution")
    plt.tight_layout()
    plt.savefig(f"results/plots/{col}_boxplot.pdf")
    plt.close()
