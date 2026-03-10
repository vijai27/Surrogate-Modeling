# Quick Start Guide

## Installation (2 minutes)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/composipy-surrogate.git
cd composipy-surrogate
```

### 2. Install Dependencies
```bash
pip install numpy pandas scipy scikit-learn matplotlib seaborn composipy SALib jupyterlab
```

### 3. Launch Jupyter
```bash
jupyter lab Buckling_Load_Factor_Analysis.ipynb
```

## Run an Analysis (5-15 minutes)

### Mode A: Buckling Load Factor (Default)
This is the **default mode**. Just open the notebook and click:
```
Kernel → Restart & Run All
```
Expected output: BLF predictions with R² ≈ 0.95

### Mode B: Bending Deflection
1. Go to **Cell 4 (Configuration)**
2. Change line 9 from:
   ```python
   ANALYSIS_MODE = "a"
   ```
   to:
   ```python
   ANALYSIS_MODE = "b"
   ```
3. Run all cells (`Kernel → Restart & Run All`)

Expected output: Deflection predictions in meters

### Mode C: Natural Frequency
1. Go to **Cell 4 (Configuration)**
2. Change line 9 to:
   ```python
   ANALYSIS_MODE = "c"
   ```
3. Run all cells

Expected output: Natural frequency predictions in Hz

## What's Happening? (Under the Hood)

### Data Phase (Cells 1-7)
- Loads libraries and configuration
- Generates 3,500 Latin Hypercube samples
- Evaluates physics model on each sample

### Morris Screening (Cells 9-10)
- Identifies important design variables
- Shows which parameters most affect your chosen metric
- Runtime: ~2 minutes

### Surrogate Modeling (Cells 11-28)
- Trains polynomial regression model
- Splits data into train/validation/test
- Evaluates overfitting risk
- Generates learning curves
- Runtime: ~1 minute

### Sensitivity Analysis (Cells 29-30)
- Global sensitivity via Sobol indices
- Shows variable importance on trained model
- Runtime: ~30 seconds

### Output (Cell 32)
- Final summary with all metrics
- Plots saved to `buckling_analysis_outputs/`

## Key Files Generated

After running, you'll see these PNG plots in `buckling_analysis_outputs/`:

| Plot | Interpretation |
|------|-----------------|
| `morris_screening.png` | Which variables matter (OAT) |
| `morris_grouped.png` | Stacking sequence as combined effect |
| `rsm_predictions.png` | How well model predicts test data |
| `residuals.png` | Prediction errors distribution |
| `learning_curve.png` | Does model need more data? |
| `degree_comparison.png` | Is polynomial degree optimal? |
| `sobol_indices.png` | Global sensitivity (S1 and ST) |

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'composipy'`
**Solution:** Install ComposiPy:
```bash
pip install composipy
```

### Issue: Import errors (eigh, quad, ii_ff)
**Solution:** Update SciPy:
```bash
pip install --upgrade scipy composipy
```

### Issue: Notebook runs slow (takes > 30 minutes)
**Solution:** Reduce sample count in Cell 4:
```python
Config.LHS_SAMPLES = 500  # Instead of 3500
```
Trade-off: Faster runtime, lower model accuracy.

### Issue: ComposiPy simulation failures ("'simply supported'")
**Status:** ✅ **Already fixed** in this version
- Old code mapped Shear BC to `"SIMPLY SUPPORTED"` (space)
- Now correctly uses `"SIMPLY_SUPPORTED"` (underscore)
- Failure rate dropped from 16.5% → 0%

### Issue: High overfitting (R² drops significantly)
**Reason:** Limited samples for 136 polynomial features
**Solutions:**
- Increase `Config.LHS_SAMPLES` to 5000+
- Reduce `Config.POLYNOMIAL_DEGREE` to 1 (linear)
- Collect more data points

### Issue: Shear BC still gives errors
**Check:** Cell 4 line that maps BC:
```python
"Shear": {"x0": "SIMPLY_SUPPORTED",  # Should be UNDERSCORE, not space
          ...
```

## Running on Different Hardware

### Laptop (Fast Runtime)
```python
Config.LHS_SAMPLES = 1000
Config.PLATE_M = 8
Config.PLATE_N = 8
```
Runtime: ~5 minutes

### Workstation (Full Analysis)
```python
Config.LHS_SAMPLES = 5000  # More samples for better model
Config.PLATE_M = 12
Config.PLATE_N = 12
```
Runtime: ~45 minutes, better accuracy

### High-Performance Computing (Research)
```python
Config.LHS_SAMPLES = 10000
Config.PLATE_M = 15
Config.PLATE_N = 15
# Add parallelization in Cell 14
```

## Advanced: Custom Design Space

To analyze a different material or geometry:

1. **Edit Cell 4 (Configuration):**
   ```python
   DESIGN_SPACE = {
       "Plate Length (mm)": [100, 600],        # Change bounds
       "Plate Width (mm)": [150, 550],
       "Thickness (mm)": [0.05, 2.0],
       "Young's Modulus (Fiber) (MPa)": [50000, 150000],  # Different material
       ...
   }
   ```

2. **Update material model if needed (Cell 8)**

3. **Run all cells with new design space**

## Next Steps

### After Your First Run
1. **Review Morris results:** Which variables drive your metric?
2. **Check surrogate accuracy:** Is R² acceptable?
3. **Inspect sensitivity:** Do Sobol indices match physics intuition?

### For Publication
1. Cite ComposiPy and SALib (see README References)
2. Save generated plots
3. Document your design space and assumptions
4. Include final summary table from Cell 32

### For Deeper Analysis
- Modify design space for your application
- Switch modes to compare BLF vs. deflection vs. frequency trade-offs
- Extract the trained surrogate model for further optimization

## Getting Help

### Documentation
- **Physics details:** See README.md → Physics Implementation Details
- **Notebook structure:** See README.md → Notebook Sections
- **Design space:** See README.md → Design Space table

### Troubleshooting
- Check `.ipynb` markdown cells for detailed explanations
- Look at print outputs from each cell for diagnostics
- Review error messages carefully (they identify exact cause)

### Contributing
Found a bug or have an improvement?
- See CONTRIBUTING.md for guidelines
- Open an issue on GitHub

---

**Ready?** Open Jupyter and press `Kernel → Restart & Run All`. Your first results should appear in ~10 minutes!
