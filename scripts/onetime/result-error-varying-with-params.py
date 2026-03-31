import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# -----------------------------
# Load your CSV
# -----------------------------
csv_file = "results/simulation-errors.csv"  # Replace with your CSV path
df = pd.read_csv(csv_file)
df['staircase_name'] = df['staircase_name'].astype(str)

# Create folder for plots
os.makedirs("results/plots", exist_ok=True)

# -----------------------------
# Parameters (independent variables)
# -----------------------------
gt_params = {
    'width': 'width_gt_mm',        # Make sure your CSV has this column in mm
    'riser': 'riser_gt_mm',
    'tread': 'tread_gt_mm'
}

# -----------------------------
# Error types (dependent variables)
# -----------------------------
error_types = ['abs_error', 'pct_error', 'mae', 'rmse']

# -----------------------------
# Scatter plots: Error vs GT parameter
# -----------------------------
for dim, gt_col in gt_params.items():
    for err in error_types:
        col_name = f"{dim}_{err}"
        if col_name not in df.columns:
            continue  # Skip if column doesn't exist in CSV
        
        plt.figure(figsize=(6,6))
        sns.scatterplot(data=df, x=gt_col, y=col_name, alpha=0.7)
        sns.regplot(data=df, x=gt_col, y=col_name, scatter=False, color='red', ci=None)
        plt.xlabel(f"Ground Truth {dim.capitalize()} (mm)")
        plt.ylabel(f"{dim.capitalize()} {err.replace('_',' ').capitalize()}")
        plt.title(f"{dim.capitalize()} {err.replace('_',' ').capitalize()} vs GT {dim.capitalize()}")
        plt.tight_layout()
        plt.savefig(f"results/plots/{dim}_{err}_vs_gt.pdf")
        plt.close()

print("GT vs error plots saved in 'results/plots/'")
