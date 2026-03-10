"""
BUCKLING LOAD FACTOR - COMPLETE SURROGATE MODELING ANALYSIS
AEROSP 740 Project - Vijai Venkatesh Natarajan Ganesh Babu

Complete standalone Python script for VS Code execution.
Includes physics-based model, RSM training, and overfitting diagnostics.

Usage:
    python buckling_analysis.py

Output:
    - Console diagnostics and metrics
    - Plots saved to buckling_analysis_outputs/
    - CSV files with results
"""

# ============================================================================
# IMPORTS
# ============================================================================

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import time

# Sampling and DoE
from scipy.stats import qmc
from SALib.analyze import sobol

# ComposiPy for composite analysis
from composipy import OrthotropicMaterial, LaminateProperty, PlateStructure
from scipy.sparse.linalg import ArpackError

# Machine Learning
from sklearn.preprocessing import PolynomialFeatures, MinMaxScaler
from sklearn.model_selection import train_test_split, learning_curve, cross_val_score
from sklearn.linear_model import RidgeCV, Ridge, LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Statistics
from scipy.stats import shapiro

# Set random seed for reproducibility
np.random.seed(42)

# Configure plotting
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 10

print("="*70)
print("BUCKLING LOAD FACTOR ANALYSIS")
print("="*70)
print(f"✓ All libraries imported successfully")
print(f"NumPy version: {np.__version__}")
print(f"Pandas version: {pd.__version__}\n")


# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Central configuration for Buckling Load Factor analysis"""
    
    # Design Space
    DESIGN_SPACE = {
        "Plate Length (mm)": [200, 500],
        "Plate Width (mm)": [200, 500],
        "Thickness (mm)": [0.1, 1.5],
        "Young's Modulus (Fiber) (MPa)": [40000, 80000],
        "Young's Modulus (Transverse) (MPa)": [40000, 80000],
        "Material Density (kg/m³)": [1500, 2000],
        "Fiber Orientation": [0, 2],  # 0=0°, 1=45°, 2=90°
        "Boundary Condition": [0, 3]  # 0=Pinned, 1=Clamped, 2=Free, 3=Shear
    }
    
    # Categorical Mappings
    FIBER_MAP = {0: 0, 1: 45, 2: 90}
    BC_MAP = {0: "Pinned", 1: "Clamped", 2: "Free Edge", 3: "Shear"}
    
    COMPOSIPY_BC = {
        "Pinned": {"x0": "PINNED", "xa": "PINNED", "y0": "PINNED", "yb": "PINNED"},
        "Clamped": {"x0": "CLAMPED", "xa": "CLAMPED", "y0": "CLAMPED", "yb": "PINNED"},
        "Free Edge": {"x0": "FREE", "xa": "FREE", "y0": "FREE", "yb": "FREE"},
        "Shear": {"x0": "SIMPLY SUPPORTED", "xa": "SIMPLY SUPPORTED", 
                  "y0": "SIMPLY SUPPORTED", "yb": "SIMPLY SUPPORTED"}
    }
    
    # Continuous columns
    CONTINUOUS_COLS = [
        "Plate Length (mm)", "Plate Width (mm)", "Thickness (mm)",
        "Young's Modulus (Fiber) (MPa)", "Young's Modulus (Transverse) (MPa)",
        "Material Density (kg/m³)"
    ]
    
    # Sampling
    LHS_SAMPLES = 2000
    
    # Model Parameters
    POLYNOMIAL_DEGREE = 3
    TEST_SIZE = 0.15
    VALIDATION_SIZE = 0.15
    RANDOM_STATE = 42
    
    # Material Properties
    POISSON_RATIO = 0.33
    STACKING_LAYERS = 8
    
    # Analysis Parameters
    PLATE_M = 10
    PLATE_N = 10
    NXX_LOAD = -1.0
    
    # Output Directory
    OUTPUT_DIR = Path("buckling_analysis_outputs")

Config.OUTPUT_DIR.mkdir(exist_ok=True)
print(f"✓ Configuration loaded")
print(f"✓ Output directory: {Config.OUTPUT_DIR}")
print(f"✓ Target response: Buckling Load Factor\n")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def normalize_data(df, columns):
    """Min-Max normalize specified columns to [0, 1]"""
    df_scaled = df.copy()
    for col in columns:
        col_min, col_max = df[col].min(), df[col].max()
        if col_max - col_min > 0:
            df_scaled[col] = (df[col] - col_min) / (col_max - col_min)
    return df_scaled

def map_categorical(df):
    """Map categorical variables to string labels"""
    df_mapped = df.copy()
    if "Fiber Orientation" in df_mapped.columns:
        df_mapped["Fiber Orientation"] = df_mapped["Fiber Orientation"].round().astype(int).map(Config.FIBER_MAP)
    if "Boundary Condition" in df_mapped.columns:
        df_mapped["Boundary Condition"] = df_mapped["Boundary Condition"].round().astype(int).map(Config.BC_MAP)
    return df_mapped

print("✓ Utility functions defined\n")


# ============================================================================
# PHYSICS-BASED MODEL
# ============================================================================

def run_buckling_analysis(design_params):
    """
    Run physics-based buckling analysis using ComposiPy.
    
    Parameters:
    -----------
    design_params : dict
        Design parameters including geometry, material properties, BC
    
    Returns:
    --------
    float
        Buckling load factor (first eigenvalue)
    """
    # Convert to SI units
    a = float(design_params["Plate Length (mm)"]) / 1000  # m
    b = float(design_params["Plate Width (mm)"]) / 1000   # m
    t = float(design_params["Thickness (mm)"]) / 1000     # m
    E1 = float(design_params["Young's Modulus (Fiber) (MPa)"]) * 1e6      # Pa
    E2 = float(design_params["Young's Modulus (Transverse) (MPa)"]) * 1e6 # Pa
    rho = float(design_params["Material Density (kg/m³)"])
    bc_str = str(design_params["Boundary Condition"])
    theta = int(design_params["Fiber Orientation"])  # degrees
    
    # Material properties
    v12 = Config.POISSON_RATIO
    G12 = E1 / (2 * (1 + v12))
    
    # Stacking sequence: [θ]₈
    stacking_sequence = [theta] * Config.STACKING_LAYERS
    
    # Define material and laminate
    material = OrthotropicMaterial(E1, E2, v12, G12, t)
    laminate = LaminateProperty(stacking_sequence, material)
    
    # Boundary conditions
    if bc_str not in Config.COMPOSIPY_BC:
        raise ValueError(f"Unknown BC: {bc_str}")
    constraints = Config.COMPOSIPY_BC[bc_str]
    
    # Create plate and run buckling analysis
    plate = PlateStructure(
        laminate, a, b,
        m=Config.PLATE_M,
        n=Config.PLATE_N,
        Nxx=Config.NXX_LOAD,
        constraints=constraints
    )
    
    eigenvals, eigenvecs = plate.buckling_analysis()
    buckling_load_factor = eigenvals[0]
    
    return buckling_load_factor

print("✓ Physics-based buckling model defined\n")


# ============================================================================
# GENERATE LHS SAMPLES
# ============================================================================

print(f"Generating {Config.LHS_SAMPLES} LHS samples...")
start_time = time.time()

# Initialize LHS sampler
sampler = qmc.LatinHypercube(d=len(Config.DESIGN_SPACE), seed=Config.RANDOM_STATE)
lhs_samples = sampler.random(n=Config.LHS_SAMPLES)

# Scale to design space bounds
bounds = np.array(list(Config.DESIGN_SPACE.values()))
lower_bounds = bounds[:, 0]
upper_bounds = bounds[:, 1]
scaled_samples = qmc.scale(lhs_samples, lower_bounds, upper_bounds)

# Create DataFrame
lhs_df = pd.DataFrame(scaled_samples, columns=list(Config.DESIGN_SPACE.keys()))
lhs_df = map_categorical(lhs_df)

elapsed = time.time() - start_time
print(f"✓ Generated {len(lhs_df)} design points in {elapsed:.2f}s\n")


# ============================================================================
# EXECUTE PHYSICS MODEL
# ============================================================================

print(f"Running buckling analysis on {len(lhs_df)} samples...")
print("This may take 10-20 minutes...\n")
start_time = time.time()

buckling_results = []
successful_indices = []
failed_count = 0

# Progress tracking
total = len(lhs_df)
checkpoint = max(1, total // 10)

for idx, row in lhs_df.iterrows():
    if (idx + 1) % checkpoint == 0:
        elapsed = time.time() - start_time
        rate = (idx + 1) / elapsed if elapsed > 0 else 0
        eta = (total - idx - 1) / rate if rate > 0 else 0
        print(f"  Progress: {idx + 1}/{total} ({(idx+1)/total*100:.1f}%) | "
              f"Rate: {rate:.1f} samples/s | ETA: {eta/60:.1f} min")
    
    try:
        blf = run_buckling_analysis(row.to_dict())
        buckling_results.append(blf)
        successful_indices.append(idx)
    except ArpackError:
        failed_count += 1
        if failed_count <= 5:
            print(f"  ⚠ Index {idx}: ARPACK convergence failure")
    except Exception as e:
        failed_count += 1
        if failed_count <= 5:
            print(f"  ✗ Index {idx}: {str(e)[:60]}")

# Create results arrays
X = lhs_df.iloc[successful_indices].reset_index(drop=True)
y = np.array(buckling_results)

# Summary
elapsed = time.time() - start_time
success_rate = len(successful_indices) / total * 100
print(f"\n{'='*70}")
print(f"SIMULATION COMPLETE")
print(f"{'='*70}")
print(f"  Total time:     {elapsed/60:.1f} minutes")
print(f"  Successful:     {len(successful_indices)} ({success_rate:.1f}%)")
print(f"  Failed:         {failed_count} ({100-success_rate:.1f}%)")
print(f"\nBuckling Load Factor Statistics:")
print(f"  Mean:  {y.mean():.4f}")
print(f"  Std:   {y.std():.4f}")
print(f"  Min:   {y.min():.4f}")
print(f"  Max:   {y.max():.4f}")
print(f"  Range: {y.max() - y.min():.4f}")
print(f"{'='*70}\n")

# Save results
X.to_csv(Config.OUTPUT_DIR / 'lhs_input_points.csv', index=False)
results_df = X.copy()
results_df['Buckling Load Factor'] = y
results_df.to_csv(Config.OUTPUT_DIR / 'simulation_results.csv', index=False)
print(f"✓ Saved results to {Config.OUTPUT_DIR}/\n")


# ============================================================================
# PREPARE DATA FOR MODELING
# ============================================================================

print("Preparing data for modeling...")

# Encode categorical variables
X_encoded = X.copy()

# Map boundary conditions back to numeric
bc_reverse_map = {v: k for k, v in Config.BC_MAP.items()}
X_encoded["Boundary Condition"] = X_encoded["Boundary Condition"].map(bc_reverse_map)

# Map fiber orientation to 0, 1, 2
fiber_reverse_map = {v: k for k, v in Config.FIBER_MAP.items()}
X_encoded["Fiber Orientation"] = X_encoded["Fiber Orientation"].map(fiber_reverse_map)

# Normalize continuous variables
X_normalized = normalize_data(X_encoded, Config.CONTINUOUS_COLS)

print(f"✓ Data prepared")
print(f"  Input features: {X_normalized.shape[1]}")
print(f"  Samples: {len(X_normalized)}\n")


# ============================================================================
# TRAIN RESPONSE SURFACE MODEL
# ============================================================================

print(f"{'='*70}")
print(f"TRAINING RESPONSE SURFACE MODEL")
print(f"{'='*70}")
print(f"Target: Buckling Load Factor")
print(f"Polynomial degree: {Config.POLYNOMIAL_DEGREE}")

# Split data
X_train, X_temp, y_train, y_temp = train_test_split(
    X_normalized, y,
    test_size=Config.TEST_SIZE + Config.VALIDATION_SIZE,
    random_state=Config.RANDOM_STATE
)

val_ratio = Config.VALIDATION_SIZE / (Config.TEST_SIZE + Config.VALIDATION_SIZE)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp,
    test_size=val_ratio,
    random_state=Config.RANDOM_STATE
)

print(f"\nData Split:")
print(f"  Training:   {len(X_train)} samples ({len(X_train)/len(X_normalized)*100:.1f}%)")
print(f"  Validation: {len(X_val)} samples ({len(X_val)/len(X_normalized)*100:.1f}%)")
print(f"  Test:       {len(X_test)} samples ({len(X_test)/len(X_normalized)*100:.1f}%)")

# Generate polynomial features
poly = PolynomialFeatures(degree=Config.POLYNOMIAL_DEGREE, include_bias=True)
X_train_poly = poly.fit_transform(X_train)
X_val_poly = poly.transform(X_val)
X_test_poly = poly.transform(X_test)

print(f"\nPolynomial Features: {X_train_poly.shape[1]}")
print(f"Samples per feature: {len(X_train) / X_train_poly.shape[1]:.1f}")

# Train Ridge regression with CV
alphas = np.logspace(-6, 6, 50)
ridge_cv = RidgeCV(alphas=alphas, cv=5, scoring='neg_mean_squared_error')
ridge_cv.fit(X_train_poly, y_train)

print(f"\nOptimal Ridge α: {ridge_cv.alpha_:.4e}")

# Predictions
y_train_pred = ridge_cv.predict(X_train_poly)
y_val_pred = ridge_cv.predict(X_val_poly)
y_test_pred = ridge_cv.predict(X_test_poly)

# Metrics
def print_metrics(y_true, y_pred, name):
    r2 = r2_score(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = np.mean(np.abs(y_true - y_pred))
    print(f"\n{name}:")
    print(f"  R²:   {r2:.6f}")
    print(f"  RMSE: {rmse:.6f}")
    print(f"  MAE:  {mae:.6f}")

print_metrics(y_train, y_train_pred, "Training Metrics")
print_metrics(y_val, y_val_pred, "Validation Metrics")
print_metrics(y_test, y_test_pred, "Test Metrics")

# Cross-validation RMSE
cv_scores = cross_val_score(
    ridge_cv, X_train_poly, y_train,
    cv=5, scoring='neg_mean_squared_error'
)
cv_rmse = np.sqrt(-cv_scores.mean())
print(f"\n5-Fold CV RMSE: {cv_rmse:.6f}")
print(f"{'='*70}\n")


# ============================================================================
# VISUALIZE MODEL PERFORMANCE
# ============================================================================

print("Generating performance visualizations...")

# Actual vs Predicted
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

datasets = [
    (y_train, y_train_pred, "Training"),
    (y_val, y_val_pred, "Validation"),
    (y_test, y_test_pred, "Test")
]

for ax, (y_true, y_pred, name) in zip(axes, datasets):
    ax.scatter(y_pred, y_true, alpha=0.5, s=20)
    
    # Perfect prediction line
    min_val = min(y_true.min(), y_pred.min())
    max_val = max(y_true.max(), y_pred.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect')
    
    r2 = r2_score(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    
    ax.set_xlabel('Predicted BLF', fontsize=11)
    ax.set_ylabel('Actual BLF', fontsize=11)
    ax.set_title(f'{name}\nR² = {r2:.6f}, RMSE = {rmse:.6f}', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)

plt.suptitle('RSM Performance: Buckling Load Factor', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(Config.OUTPUT_DIR / 'rsm_predictions.png', dpi=300, bbox_inches='tight')
print(f"  ✓ Saved: rsm_predictions.png")
plt.close()

# Residuals
residuals = y_test - y_test_pred

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Residuals vs Predicted
axes[0].scatter(y_test_pred, residuals, alpha=0.5, s=20)
axes[0].axhline(y=0, color='r', linestyle='--', linewidth=2)
axes[0].set_xlabel('Predicted BLF', fontsize=11)
axes[0].set_ylabel('Residuals', fontsize=11)
axes[0].set_title('Residuals vs Predicted (Test Set)', fontsize=12)
axes[0].grid(True, alpha=0.3)

# Histogram
axes[1].hist(residuals, bins=30, edgecolor='black', alpha=0.7)
axes[1].set_xlabel('Residuals', fontsize=11)
axes[1].set_ylabel('Frequency', fontsize=11)
axes[1].set_title('Distribution of Residuals', fontsize=12)
axes[1].axvline(x=0, color='r', linestyle='--', linewidth=2)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(Config.OUTPUT_DIR / 'residuals.png', dpi=300, bbox_inches='tight')
print(f"  ✓ Saved: residuals.png\n")
plt.close()


# ============================================================================
# OVERFITTING DIAGNOSTICS
# ============================================================================

print(f"{'='*70}")
print(f"COMPREHENSIVE OVERFITTING DIAGNOSTICS")
print(f"{'='*70}")

# 1. R² Degradation
r2_train = r2_score(y_train, y_train_pred)
r2_val = r2_score(y_val, y_val_pred)
r2_test = r2_score(y_test, y_test_pred)

r2_drop_val = r2_train - r2_val
r2_drop_test = r2_train - r2_test

print(f"\n1. R² DEGRADATION CHECK:")
print(f"   Training R²:   {r2_train:.6f}")
print(f"   Validation R²: {r2_val:.6f}")
print(f"   Test R²:       {r2_test:.6f}")
print(f"   Train → Val drop:  {r2_drop_val:.6f}")
print(f"   Train → Test drop: {r2_drop_test:.6f}")

if r2_drop_val > 0.05 or r2_drop_test > 0.05:
    print(f"   ⚠️  WARNING: Significant R² drop → OVERFITTING!")
    risk = 'HIGH'
elif abs(r2_drop_val) < 0.001 and abs(r2_drop_test) < 0.001:
    print(f"   ⚠️  WARNING: Too little drop → DATA LEAKAGE!")
    risk = 'DATA_LEAKAGE'
elif r2_train > 0.999 and r2_test > 0.999:
    print(f"   ⚠️  WARNING: R² > 0.999 → DETERMINISTIC!")
    risk = 'DETERMINISTIC'
else:
    print(f"   ✓ Normal degradation pattern")
    risk = 'LOW'

# 2. Output Variance
y_var = np.var(y_train)
y_std = np.std(y_train)
y_range = y_train.max() - y_train.min()

print(f"\n2. OUTPUT VARIANCE CHECK:")
print(f"   Variance:  {y_var:.6f}")
print(f"   Std dev:   {y_std:.6f}")
print(f"   Range:     {y_range:.6f}")
print(f"   Min:       {y_train.min():.6f}")
print(f"   Max:       {y_train.max():.6f}")

if y_var < 0.001:
    print(f"   ⚠️  WARNING: Very low variance!")
else:
    print(f"   ✓ Sufficient variation")

# 3. Relative Error
rmse_test = np.sqrt(mean_squared_error(y_test, y_test_pred))
rel_rmse = (rmse_test / y_range * 100) if y_range > 0 else 0

print(f"\n3. RELATIVE ERROR CHECK:")
print(f"   Test RMSE: {rmse_test:.6f}")
print(f"   Relative:  {rel_rmse:.2f}% of range")

if rel_rmse < 0.1:
    print(f"   ⚠️  WARNING: < 0.1% → Suspiciously good!")
elif rel_rmse > 20:
    print(f"   ⚠️  WARNING: > 20% → Poor fit")
else:
    print(f"   ✓ Reasonable error level")

# 4. Model Complexity
n_samples = len(X_train)
n_features = X_train_poly.shape[1]
samples_per_feature = n_samples / n_features

print(f"\n4. MODEL COMPLEXITY CHECK:")
print(f"   Training samples:     {n_samples}")
print(f"   Polynomial features:  {n_features}")
print(f"   Samples per feature:  {samples_per_feature:.1f}")

if samples_per_feature < 5:
    print(f"   ⚠️  WARNING: Too many features!")
elif samples_per_feature < 10:
    print(f"   ⚠️  CAUTION: Borderline ratio")
else:
    print(f"   ✓ Adequate samples per feature")

# 5. Residual Normality
_, p_value = shapiro(residuals[:5000] if len(residuals) > 5000 else residuals)

print(f"\n5. RESIDUAL NORMALITY TEST:")
print(f"   Shapiro-Wilk p-value: {p_value:.4f}")
print(f"   Mean residual: {residuals.mean():.6f}")
print(f"   Std residual:  {residuals.std():.6f}")

if p_value < 0.05:
    print(f"   ⚠️  Residuals not normal (p < 0.05)")
else:
    print(f"   ✓ Residuals approximately normal")

# Overall Assessment
print(f"\n{'='*70}")
print(f"OVERALL RISK ASSESSMENT: {risk}")
print(f"{'='*70}\n")


# ============================================================================
# LEARNING CURVES
# ============================================================================

print("Generating learning curves...")

train_sizes = np.linspace(0.1, 1.0, 10)
train_sizes_abs, train_scores, val_scores = learning_curve(
    ridge_cv, X_train_poly, y_train,
    cv=5,
    scoring='neg_mean_squared_error',
    train_sizes=train_sizes,
    n_jobs=-1
)

train_rmse = np.sqrt(-train_scores)
val_rmse = np.sqrt(-val_scores)

fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(train_sizes_abs, train_rmse.mean(axis=1), 
        'o-', label='Training RMSE', linewidth=2, markersize=8)
ax.fill_between(train_sizes_abs, 
                 train_rmse.mean(axis=1) - train_rmse.std(axis=1),
                 train_rmse.mean(axis=1) + train_rmse.std(axis=1),
                 alpha=0.2)

ax.plot(train_sizes_abs, val_rmse.mean(axis=1), 
        's-', label='Validation RMSE', linewidth=2, markersize=8)
ax.fill_between(train_sizes_abs, 
                 val_rmse.mean(axis=1) - val_rmse.std(axis=1),
                 val_rmse.mean(axis=1) + val_rmse.std(axis=1),
                 alpha=0.2)

ax.set_xlabel('Training Set Size', fontsize=12)
ax.set_ylabel('RMSE', fontsize=12)
ax.set_title('Learning Curve: Buckling Load Factor', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

gap = val_rmse.mean(axis=1)[-1] - train_rmse.mean(axis=1)[-1]
gap_pct = gap / val_rmse.mean(axis=1)[-1] * 100

status = 'OVERFITTING!' if gap_pct > 10 else 'Good Fit'
color = 'red' if gap_pct > 10 else 'green'

ax.text(0.05, 0.95, 
        f'Final Gap: {gap:.6f} ({gap_pct:.1f}%)\n{status}',
        transform=ax.transAxes, 
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor=color, alpha=0.3),
        fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig(Config.OUTPUT_DIR / 'learning_curve.png', dpi=300, bbox_inches='tight')
print(f"  ✓ Saved: learning_curve.png")
plt.close()

print(f"  Final training RMSE:   {train_rmse.mean(axis=1)[-1]:.6f}")
print(f"  Final validation RMSE: {val_rmse.mean(axis=1)[-1]:.6f}")
print(f"  Gap: {gap:.6f} ({gap_pct:.1f}%)\n")


# ============================================================================
# COMPARE POLYNOMIAL DEGREES
# ============================================================================

print("Comparing polynomial degrees (1-5)...\n")

degree_results = []

for degree in range(1, 6):
    # Create features
    poly_temp = PolynomialFeatures(degree=degree)
    X_train_temp = poly_temp.fit_transform(X_train)
    X_test_temp = poly_temp.transform(X_test)
    
    # Train model
    model_temp = Ridge(alpha=1.0)
    model_temp.fit(X_train_temp, y_train)
    
    # Predictions
    y_train_pred_temp = model_temp.predict(X_train_temp)
    y_test_pred_temp = model_temp.predict(X_test_temp)
    
    # Metrics
    r2_train_temp = r2_score(y_train, y_train_pred_temp)
    r2_test_temp = r2_score(y_test, y_test_pred_temp)
    rmse_test_temp = np.sqrt(mean_squared_error(y_test, y_test_pred_temp))
    
    degree_results.append({
        'Degree': degree,
        'Features': X_train_temp.shape[1],
        'Train R²': r2_train_temp,
        'Test R²': r2_test_temp,
        'Test RMSE': rmse_test_temp,
        'R² Gap': r2_train_temp - r2_test_temp
    })

df_degrees = pd.DataFrame(degree_results)

# Plot comparison
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# R² plot
axes[0].plot(df_degrees['Degree'], df_degrees['Train R²'], 
             'o-', label='Train R²', linewidth=2, markersize=8)
axes[0].plot(df_degrees['Degree'], df_degrees['Test R²'], 
             's-', label='Test R²', linewidth=2, markersize=8)
axes[0].set_xlabel('Polynomial Degree', fontsize=11)
axes[0].set_ylabel('R²', fontsize=11)
axes[0].set_title('R² vs Polynomial Degree', fontsize=12, fontweight='bold')
axes[0].legend()
axes[0].grid(True, alpha=0.3)
axes[0].set_xticks(df_degrees['Degree'])

# RMSE plot
axes[1].plot(df_degrees['Degree'], df_degrees['Test RMSE'], 
             'o-', linewidth=2, markersize=8, color='green')
axes[1].set_xlabel('Polynomial Degree', fontsize=11)
axes[1].set_ylabel('Test RMSE', fontsize=11)
axes[1].set_title('Test RMSE vs Polynomial Degree', fontsize=12, fontweight='bold')
axes[1].grid(True, alpha=0.3)
axes[1].set_xticks(df_degrees['Degree'])

# Mark optimal
optimal_idx = df_degrees['Test RMSE'].idxmin()
axes[1].plot(df_degrees.loc[optimal_idx, 'Degree'], 
             df_degrees.loc[optimal_idx, 'Test RMSE'], 
             'r*', markersize=20, 
             label=f'Optimal (degree {df_degrees.loc[optimal_idx, "Degree"]:.0f})')
axes[1].legend()

plt.tight_layout()
plt.savefig(Config.OUTPUT_DIR / 'degree_comparison.png', dpi=300, bbox_inches='tight')
print(f"  ✓ Saved: degree_comparison.png")
plt.close()

print("\nPolynomial Degree Comparison:")
print("="*70)
print(df_degrees.to_string(index=False))
print("="*70)
print(f"\nOptimal degree: {df_degrees.loc[optimal_idx, 'Degree']:.0f} (lowest test RMSE)")
print(f"Current degree: {Config.POLYNOMIAL_DEGREE}")

if df_degrees.loc[optimal_idx, 'Degree'] != Config.POLYNOMIAL_DEGREE:
    print(f"\n⚠️  Consider changing to degree {df_degrees.loc[optimal_idx, 'Degree']:.0f}\n")


# ============================================================================
# BASELINE COMPARISON
# ============================================================================

print("\nBaseline Model Comparison:\n")

baseline_results = []

# 1. Current polynomial model
baseline_results.append({
    'Model': f'Polynomial (degree {Config.POLYNOMIAL_DEGREE})',
    'Features': X_train_poly.shape[1],
    'Test R²': r2_test,
    'Test RMSE': rmse_test
})

# 2. Linear regression
lr = LinearRegression()
lr.fit(X_train, y_train)
y_test_pred_lr = lr.predict(X_test)

baseline_results.append({
    'Model': 'Linear Regression',
    'Features': X_train.shape[1],
    'Test R²': r2_score(y_test, y_test_pred_lr),
    'Test RMSE': np.sqrt(mean_squared_error(y_test, y_test_pred_lr))
})

# 3. Mean baseline
y_mean = np.mean(y_train)
y_test_pred_mean = np.full_like(y_test, y_mean)

baseline_results.append({
    'Model': 'Mean Baseline',
    'Features': 0,
    'Test R²': r2_score(y_test, y_test_pred_mean),
    'Test RMSE': np.sqrt(mean_squared_error(y_test, y_test_pred_mean))
})

df_baseline = pd.DataFrame(baseline_results)

print("="*70)
print(df_baseline.to_string(index=False))
print("="*70)

if df_baseline.iloc[0]['Test R²'] - df_baseline.iloc[1]['Test R²'] < 0.05:
    print("\n⚠️  Polynomial barely better than linear!")
    print("   → Consider using simpler linear model\n")
else:
    print(f"\n✓ Polynomial provides {(df_baseline.iloc[0]['Test R²'] - df_baseline.iloc[1]['Test R²'])*100:.1f}% improvement over linear\n")


# ============================================================================
# SOBOL SENSITIVITY ANALYSIS
# ============================================================================

print(f"{'='*70}")
print(f"SOBOL GLOBAL SENSITIVITY ANALYSIS")
print(f"{'='*70}")

# Use normalized inputs and actual outputs
X_sobol = X_normalized.values
y_sobol = y

# Scale X to [0, 1]
scaler = MinMaxScaler()
X_sobol_scaled = scaler.fit_transform(X_sobol)

# Define problem
problem = {
    "num_vars": len(Config.DESIGN_SPACE),
    "names": list(Config.DESIGN_SPACE.keys()),
    "bounds": [[0.0, 1.0]] * len(Config.DESIGN_SPACE)
}

print(f"\nAnalyzing {len(y_sobol)} samples...")

# Perform Sobol analysis
Si = sobol.analyze(
    problem,
    y_sobol,
    calc_second_order=False,
    print_to_console=False
)

# Print results
print("\nSobol Indices:")
print("="*70)
print(f"{'Parameter':<40} {'S1 (First)':<12} {'ST (Total)':<12}")
print("-"*70)
for i, name in enumerate(problem['names']):
    print(f"{name:<40} {Si['S1'][i]:<12.4f} {Si['ST'][i]:<12.4f}")
print("="*70)

# Top 3 influential
top_indices = np.argsort(Si['S1'])[::-1][:3]
print("\nTop 3 Most Influential Parameters (First-Order):")
for i, idx in enumerate(top_indices, 1):
    print(f"  {i}. {problem['names'][idx]}: S1 = {Si['S1'][idx]:.4f}, ST = {Si['ST'][idx]:.4f}")

# Plot
fig, ax = plt.subplots(figsize=(12, 6))

bar_width = 0.35
indices = np.arange(len(problem['names']))

ax.bar(indices, Si['S1'], bar_width, label='First Order (S1)', color='cornflowerblue')
ax.bar(indices + bar_width, Si['ST'], bar_width, label='Total Order (ST)', 
       alpha=0.7, color='tomato')

ax.set_xticks(indices + bar_width / 2)
ax.set_xticklabels(problem['names'], rotation=45, ha='right')
ax.set_ylabel("Sobol Index", fontsize=12)
ax.set_title("Global Sensitivity Analysis: Buckling Load Factor", fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(Config.OUTPUT_DIR / 'sobol_indices.png', dpi=300, bbox_inches='tight')
print(f"\n  ✓ Saved: sobol_indices.png")
plt.close()

print(f"\n✓ Sobol analysis complete\n")


# ============================================================================
# FINAL SUMMARY
# ============================================================================

print(f"{'='*70}")
print(f"FINAL SUMMARY: BUCKLING LOAD FACTOR ANALYSIS")
print(f"{'='*70}")

print(f"\n1. DATA:")
print(f"   Total samples:      {len(lhs_df)}")
print(f"   Successful:         {len(X)} ({len(X)/len(lhs_df)*100:.1f}%)")
print(f"   Training set:       {len(X_train)}")
print(f"   Validation set:     {len(X_val)}")
print(f"   Test set:           {len(X_test)}")

print(f"\n2. MODEL:")
print(f"   Type:               Response Surface Model (Ridge)")
print(f"   Polynomial degree:  {Config.POLYNOMIAL_DEGREE}")
print(f"   Features:           {X_train_poly.shape[1]}")
print(f"   Optimal α:          {ridge_cv.alpha_:.4e}")

print(f"\n3. PERFORMANCE:")
print(f"   Test R²:            {r2_test:.6f}")
print(f"   Test RMSE:          {rmse_test:.6f}")
print(f"   Relative RMSE:      {rel_rmse:.2f}% of output range")
print(f"   CV RMSE:            {cv_rmse:.6f}")

print(f"\n4. OVERFITTING RISK:")
print(f"   Assessment:         {risk}")
print(f"   R² degradation:     {r2_drop_test:.6f}")
print(f"   Samples/feature:    {samples_per_feature:.1f}")

print(f"\n5. SENSITIVITY (Top 3):")
for i, idx in enumerate(top_indices, 1):
    print(f"   {i}. {problem['names'][idx]}: S1 = {Si['S1'][idx]:.4f}")

print(f"\n6. RECOMMENDATIONS:")

if risk == 'DETERMINISTIC':
    print(f"   ✓ Model correctly captures relationship")
    print(f"   → Near-perfect fit is expected for this physics")
elif risk == 'HIGH':
    print(f"   ⚠️  Reduce polynomial degree or increase regularization")
    print(f"   → Try degree 2 or α = 10-100")
elif risk == 'DATA_LEAKAGE':
    print(f"   🚨 Verify train/val/test splits are independent")
    print(f"   → Check for duplicate samples")
elif samples_per_feature < 10:
    print(f"   ⚠️  Consider reducing polynomial degree")
    print(f"   → Current ratio: {samples_per_feature:.1f} samples/feature")
else:
    print(f"   ✓ Model appears well-calibrated")
    print(f"   → Ready for optimization or further analysis")

print(f"\n7. OUTPUT FILES:")
print(f"   Directory: {Config.OUTPUT_DIR}/")
print(f"   - lhs_input_points.csv")
print(f"   - simulation_results.csv")
print(f"   - rsm_predictions.png")
print(f"   - residuals.png")
print(f"   - learning_curve.png")
print(f"   - degree_comparison.png")
print(f"   - sobol_indices.png")

print(f"\n{'='*70}")
print(f"ANALYSIS COMPLETE")
print(f"{'='*70}")
print(f"\nAll outputs saved to: {Config.OUTPUT_DIR}/")
print(f"\n✓ Script execution finished successfully!")
