"""
Fix log1p -> log transform and reduce Morris samples.
log1p(x) ~ x for x << 1, which means it does nothing for bending deflection values.
log(x) properly compresses the full range.
"""
import json

with open('Buckling_Load_Factor_Analysis.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

def get_src(cell):
    s = cell['source']
    if isinstance(s, list):
        return ''.join(s)
    return s

def set_src(cell, text):
    cell['source'] = text.split('\n')
    # Add \n to all lines except the last
    for i in range(len(cell['source']) - 1):
        cell['source'][i] += '\n'
    cell['outputs'] = []

changes = []

# Cell 10 - Morris screening: fix log1p and reduce trajectories
src10 = get_src(nb['cells'][10])
old_lines = [
    "    # Use log1p transform for consistency; treat non-positive values as failure",
    "        y_morris[i] = np.log1p(max(result, 0.0))",
    "        y_morris[i] = 0.0  # log1p(0) = 0, plate fails immediately",
    "N_morris = 150  # Number of trajectories",
]
new_lines = [
    "    # Use log transform; treat non-positive values as failure",
    "        y_morris[i] = np.log(max(result, 1e-30))",
    "        y_morris[i] = np.log(1e-30)  # log floor for failed plates",
    "N_morris = 60  # Number of trajectories",
]
for old, new in zip(old_lines, new_lines):
    if old in src10:
        src10 = src10.replace(old, new)
        changes.append(f"Cell 10: '{old.strip()}' -> '{new.strip()}'")
    else:
        print(f"WARNING: Could not find in cell 10: '{old.strip()}'")

set_src(nb['cells'][10], src10)

# Cell 16 - Data prep: fix log1p
src16 = get_src(nb['cells'][16])
replacements_16 = {
    "y_log = np.log1p(y_valid)": "y_log = np.log(y_valid)",
    'print(f"\\nLog-transform applied (y_log = log(1 + {RSHORT})):")': 'print(f"\\nLog-transform applied (y_log = log({RSHORT})):")',
}
for old, new in replacements_16.items():
    if old in src16:
        src16 = src16.replace(old, new)
        changes.append(f"Cell 16: '{old.strip()}'")
    else:
        print(f"WARNING: Could not find in cell 16: '{old.strip()}'")
set_src(nb['cells'][16], src16)

# Cell 18 - RSM training: fix expm1 and log text
src18 = get_src(nb['cells'][18])
replacements_18 = {
    "np.expm1(y_test)": "np.exp(y_test)",
    "np.expm1(y_test_pred)": "np.exp(y_test_pred)",
    'log(1 + {RNAME})': 'log({RNAME})',
}
for old, new in replacements_18.items():
    if old in src18:
        src18 = src18.replace(old, new)
        changes.append(f"Cell 18: '{old}' -> '{new}'")
    else:
        print(f"WARNING: Could not find in cell 18: '{old}'")
set_src(nb['cells'][18], src18)

# Cell 32 - Summary: fix expm1 and log text
src32 = get_src(nb['cells'][32])
replacements_32 = {
    "np.expm1(y_test)": "np.exp(y_test)",
    "np.expm1(y_test_pred)": "np.exp(y_test_pred)",
    'log(1 + {RSHORT})': 'log({RSHORT})',
}
for old, new in replacements_32.items():
    if old in src32:
        src32 = src32.replace(old, new)
        changes.append(f"Cell 32: '{old}' -> '{new}'")
    else:
        print(f"WARNING: Could not find in cell 32: '{old}'")
set_src(nb['cells'][32], src32)

# Save
with open('Buckling_Load_Factor_Analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"\nApplied {len(changes)} changes:")
for c in changes:
    print(f"  {c}")
print("\nDone! Notebook saved.")
