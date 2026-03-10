# Contributing to Composite Laminate Analysis

Thank you for your interest in contributing! This document provides guidelines and instructions.

## Types of Contributions

We welcome contributions in the following areas:

### 1. Bug Reports
- Physics calculation issues
- Numerical instabilities or convergence failures
- Visualization errors
- Documentation inaccuracies

**To report a bug:**
1. Check existing issues first
2. Create a new issue with:
   - Clear title describing the bug
   - Steps to reproduce
   - Expected vs. actual behavior
   - Environment (Python version, package versions)
   - Error message / stack trace (if applicable)

### 2. Feature Requests
- New analysis modes (e.g., composite failure modes, matrix cracking)
- Additional sensitivity methods
- Performance improvements
- Visualization enhancements

**To request a feature:**
1. Describe the use case and motivation
2. Explain why it's valuable for the project
3. Suggest possible implementation approach (optional)

### 3. Code Improvements
- Optimization of physics calculations
- Refactoring for clarity
- Additional error handling
- Performance enhancements
- Code style improvements

### 4. Documentation
- Improved README clarity
- Additional examples
- Physics theory explanations
- Troubleshooting guides
- Tutorial notebooks

## Getting Started

### 1. Fork & Clone
```bash
git clone https://github.com/yourusername/composipy-surrogate.git
cd composipy-surrogate
```

### 2. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-name
```

Use descriptive branch names:
- `feature/frequency-damping` (new feature)
- `fix/bc-mapping-bug` (bug fix)
- `docs/usage-examples` (documentation)
- `perf/optimize-morris` (performance)

### 3. Install Development Dependencies
```bash
pip install -e .
pip install pytest pytest-cov black flake8
```

### 4. Make Changes
- Write clean, readable code
- Add comments for complex logic
- Follow PEP 8 style guide
- Test your changes thoroughly

### 5. Run Tests
```bash
pytest tests/
pytest --cov=composipy_surrogate tests/
```

### 6. Code Style
```bash
black Buckling_Load_Factor_Analysis.ipynb
flake8 *.py
```

### 7. Commit & Push
```bash
git add .
git commit -m "Clear description of changes"
git push origin feature/your-feature-name
```

### 8. Create a Pull Request
1. Go to GitHub and create a PR
2. Provide a clear title and description
3. Link related issues (if any)
4. Wait for review and feedback

## Development Guidelines

### Code Style
- Follow PEP 8
- Use descriptive variable names
- Add docstrings to functions
- Keep functions focused and modular
- Max line length: 88 characters (Black)

### Physics Code
- Document assumptions clearly
- Reference theory or papers
- Use SI units consistently
- Validate against known benchmarks
- Test edge cases (thin/thick plates, high modulus contrasts)

### Notebook Cells
- Keep cells focused on one task
- Add markdown headers (##, ###)
- Include progress checkpoints (print statements)
- Use Config variables (avoid magic numbers)
- Document any hardcoded parameters

### Testing
- Write tests for new physics implementations
- Test both typical and edge cases
- Document test expectations
- Use meaningful assertion messages

Example test structure:
```python
def test_bending_deflection_thin_plate():
    """Test bending deflection prediction on thin composite plate."""
    # Arrange
    design = {...}  # Known test case
    expected_deflection = ...  # From theory or reference

    # Act
    result = run_physics_analysis(design)

    # Assert
    assert abs(result - expected_deflection) < tolerance
```

## Physics Implementation Standards

### Validation Requirements
New analysis modes or physics calculations should include:
1. **Theory reference** — Cite textbook/paper with equations
2. **Benchmark comparison** — Compare against known analytical solution
3. **Numerical verification** — Test with multiple mesh resolutions
4. **Edge case testing** — Very thin/thick, high modulus contrasts
5. **Unit consistency** — Verify all inputs/outputs in SI units

### Documentation Requirements
All new physics functions must include:
```python
def new_analysis_function(plate, param1, param2):
    """
    Brief one-line description.

    Detailed description of physics and methodology.
    References: [Author, Year], equation X.Y.Z

    Parameters
    ----------
    plate : PlateStructure
        ComposiPy plate object with laminate and BCs
    param1 : float
        Description and units

    Returns
    -------
    float
        Description, units, and typical value range

    Notes
    -----
    - Assumption 1
    - Assumption 2
    - Limitation 1

    Examples
    --------
    >>> result = new_analysis_function(plate, 1000.0, 10)
    >>> print(result)
    """
```

## Review Process

### What Reviewers Look For
1. **Correctness** — Does the code do what it claims?
2. **Physics** — Are physics assumptions valid? Is theory cited?
3. **Tests** — Are there adequate tests? Do they pass?
4. **Style** — Is code readable and well-documented?
5. **Impact** — Could this break existing functionality?

### Feedback Guidelines
- Be respectful and constructive
- Ask clarifying questions rather than making assumptions
- Suggest improvements, don't demand changes
- Acknowledge good work and thoughtful approaches

## Common Scenarios

### "I want to add a new analysis mode (e.g., failure analysis)"
1. Design the new mode (e.g., `Config.ANALYSIS_MODE = "d"`)
2. Implement `_failure_analysis(plate, ...)`
3. Add to dispatcher in `run_physics_analysis()`
4. Update Cell 4 (MODE_META dict)
5. Add string replacements for dynamic labels in affected cells
6. Test all three existing modes still work
7. Document theory and validation in PR description

### "I found a numerical issue (e.g., singular matrix)"
1. Create a minimal reproducible example
2. Identify the cause (ill-conditioned matrix? invalid BC? zero load?)
3. Propose a fix with physical justification
4. Test on the failing case and several others
5. Document the edge case to prevent regression

### "I want to optimize Morris Screening (slow)"
1. Profile to identify bottleneck
2. Propose optimization (e.g., vectorize evaluations, cache, parallelize)
3. Benchmark before/after on representative case
4. Ensure results are numerically identical
5. Document any numerical precision trade-offs

## Reporting Security Issues

Do **not** open a public issue for security vulnerabilities. Email the maintainers privately instead.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- Check existing issues and discussions
- Review documentation and examples
- Open a discussion issue with your question

---

Thank you for contributing! 🎉
