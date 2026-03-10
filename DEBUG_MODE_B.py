"""
Debug script for Mode B (Bending Deflection)
Tests if the physics implementation is correct
"""

import numpy as np
from composipy import OrthotropicMaterial, LaminateProperty, PlateStructure
from scipy.integrate import quad
from composipy.pre_integrated_component.functions import fxi, sxieta

# Test case: Simple isotropic plate (known analytical solution)
print("="*70)
print("DEBUG: Mode B Bending Deflection")
print("="*70)

# Known case: Square plate, all 0 degrees (quasi-isotropic)
a = 0.3  # 300 mm
b = 0.3  # 300 mm
t_ply = 0.125e-3  # 0.125 mm per ply
E1 = 60e9  # Pa
E2 = 60e9  # Pa (isotropic)
v12 = 0.3
G12 = E1 / (2 * (1 + v12))
rho = 1600
h_total = t_ply * 8

p = 1000.0  # 1000 Pa pressure

print(f"\nTest parameters:")
print(f"  Plate: {a*1000:.0f} mm x {b*1000:.0f} mm")
print(f"  Thickness: {h_total*1e6:.0f} um")
print(f"  Material: E={E1/1e9:.0f} GPa (quasi-isotropic)")
print(f"  Pressure: {p} Pa")

# Build laminate
stacking_sequence = [0] * 8  # All zeros
material = OrthotropicMaterial(E1, E2, v12, G12, t_ply)
laminate = LaminateProperty(stacking_sequence, material)

# Create plate (all pinned)
constraints = {"x0": "PINNED", "xa": "PINNED", "y0": "PINNED", "yb": "PINNED"}
plate = PlateStructure(
    laminate, a, b,
    m=10, n=10,
    Nxx=0,  # No buckling load
    constraints=constraints
)

# Get K matrix and indices
K, _ = plate.calc_K_KG_D()
sw_idx = plate.sw_idx
n_dof = len(sw_idx)

print(f"\nSystem information:")
print(f"  Number of DOFs: {n_dof}")
print(f"  K matrix shape: {K.shape}")
print(f"  K matrix rank: {np.linalg.matrix_rank(K)}")
print(f"  K condition number: {np.linalg.cond(K):.2e}")

# Calculate shape function integrals
print(f"\nCalculating shape function integrals...")
unique_indices = set()
for (i, j) in sw_idx:
    unique_indices.add(i)
    unique_indices.add(j)

sf_integrals = {}
for idx in unique_indices:
    try:
        val, _ = quad(lambda xi, _i=idx: fxi(_i, xi), -1, 1)
        sf_integrals[idx] = val
    except:
        sf_integrals[idx] = 0.0
        print(f"  Warning: Failed to integrate f_{idx}")

print(f"  Unique indices: {len(unique_indices)}")
print(f"  All integrals:")
for idx in sorted(unique_indices):
    print(f"    Int f_{idx}(xi) dxi = {sf_integrals[idx]:.6f}")

# Build load vector
print(f"\nBuilding load vector...")
F = np.zeros(n_dof)
for r, (i, j) in enumerate(sw_idx):
    F[r] = p * (a * b / 4.0) * sf_integrals[i] * sf_integrals[j]

print(f"  Load vector shape: {F.shape}")
print(f"  Load vector min: {F.min():.6e}")
print(f"  Load vector max: {F.max():.6e}")
print(f"  Load vector mean: {F.mean():.6e}")
print(f"  Load vector std: {F.std():.6e}")
print(f"  Non-zero entries: {np.count_nonzero(F)} / {n_dof}")
print(f"  Total load: {F.sum():.6e} (should be ~{p*a*b:.2f})")

# Solve for deflection coefficients
print(f"\nSolving K*w = F...")
try:
    w_coeffs = np.linalg.solve(K, F)
    print(f"  Solution converged!")
    print(f"  w_coeffs min: {w_coeffs.min():.6e}")
    print(f"  w_coeffs max: {w_coeffs.max():.6e}")
    print(f"  w_coeffs mean: {w_coeffs.mean():.6e}")
except np.linalg.LinAlgError as e:
    print(f"  ERROR: {e}")
    w_coeffs = None

# Evaluate center-point deflection
if w_coeffs is not None:
    print(f"\nEvaluating center-point deflection...")
    sw_center = sxieta(sw_idx, 0.0, 0.0)  # xi=0, eta=0 = center
    center_deflection = float(sw_center @ w_coeffs)

    print(f"  Shape function at center (non-zero): {np.count_nonzero(sw_center)}")
    print(f"  Center deflection (m): {center_deflection:.6e}")
    print(f"  Center deflection (um): {center_deflection*1e6:.6f}")

    # Sanity checks
    print(f"\nSanity checks:")

    # Compare with Kirchhoff plate theory (isotropic, simply supported)
    # w_max = 0.00406 * p * a^4 / D for square plate
    # D = E * h^3 / (12 * (1-v^2))
    D_iso = E1 * h_total**3 / (12 * (1 - v12**2))
    w_analytical = 0.00406 * p * a**4 / D_iso

    print(f"  D_flexural = {D_iso:.6e}")
    print(f"  Analytical (Kirchhoff plate): {w_analytical:.6e} m ({w_analytical*1e6:.6f} um)")
    print(f"  Computed (Ritz): {center_deflection:.6e} m ({center_deflection*1e6:.6f} um)")
    print(f"  Ratio (Computed/Analytical): {abs(center_deflection)/w_analytical:.3f}")

    if abs(center_deflection) / w_analytical > 10 or abs(center_deflection) / w_analytical < 0.1:
        print(f"  PROBLEM: Deflection way off from analytical!")
    elif abs(center_deflection) / w_analytical > 1.5 or abs(center_deflection) / w_analytical < 0.5:
        print(f"  WARNING: Deflection differs by more than 50%")
    else:
        print(f"  OK: Deflection in reasonable range")

    # Also check: what if we evaluate at multiple points?
    print(f"\nDeflection field sample (xi, eta -> w):")
    for xi_val in [-0.5, 0.0, 0.5]:
        for eta_val in [-0.5, 0.0, 0.5]:
            sw_pt = sxieta(sw_idx, xi_val, eta_val)
            w_pt = float(sw_pt @ w_coeffs)
            print(f"  ({xi_val:+.1f}, {eta_val:+.1f}) -> w = {w_pt:.6e} m")

print("\n" + "="*70)
print("Check:")
print("  1. Is K matrix rank-deficient?")
print("  2. Is load vector near zero?")
print("  3. Is deflection too large or too small?")
print("  4. Does deflection ratio match analytical?")
print("="*70)
