# Virtual Environment Setup

This guide explains how to set up and use the Python virtual environment for the Seismic Classifier project.

## Quick Setup

### Option 1: Automated Setup (Recommended)
```bash
# Run the setup script
bash scripts/setup_venv.sh

# Activate the environment
source venv/bin/activate
```

### Option 2: Using Make
```bash
# Complete setup including virtual environment
make setup

# Just create virtual environment
make venv

# Activate manually
source venv/bin/activate
```

### Option 3: Manual Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install package in development mode
pip install -e .

# Install pre-commit hooks
pre-commit install
```

## Using the Virtual Environment

### Activation
Always activate the virtual environment before working on the project:

```bash
# From project root
source venv/bin/activate

# Or use the helper script
source scripts/activate_venv.sh
```

### Verification
Verify the virtual environment is active:

```bash
# Check Python location
which python
# Should show: /path/to/seismic-classifier/venv/bin/python

# Check Python version
python --version
# Should show: Python 3.8+ 

# Check installed packages
pip list
```

### Deactivation
To deactivate the virtual environment:

```bash
deactivate
```

## IDE Configuration

### VS Code
The project is pre-configured to use the virtual environment:

- **Python Interpreter**: Automatically set to `./venv/bin/python`
- **Tasks**: All tasks use the virtual environment
- **Debug Configurations**: All launch configs use the virtual environment
- **Terminal**: Integrated terminal will activate the environment

### Other IDEs
For other IDEs, set the Python interpreter to:
```
/path/to/seismic-classifier/venv/bin/python
```

## Dependencies

### Core Dependencies
- **Scientific Computing**: NumPy, SciPy, Pandas
- **Seismology**: ObsPy
- **Machine Learning**: scikit-learn, TensorFlow, XGBoost
- **Visualization**: Matplotlib, Seaborn, Plotly
- **Web Framework**: Dash, Streamlit
- **Configuration**: PyYAML, python-dotenv

### Development Dependencies
- **Code Quality**: Black, Flake8, MyPy
- **Testing**: Pytest, pytest-cov
- **Security**: Bandit, Safety
- **Documentation**: Sphinx
- **Version Control**: Pre-commit

## Common Commands

All commands assume the virtual environment is activated:

```bash
# Install new package
pip install package-name
pip freeze > requirements.txt  # Update requirements if needed

# Run tests
make test
# or
pytest tests/ -v

# Format code
make format
# or
black src/ tests/ scripts/

# Lint code
make lint
# or
flake8 src/ tests/ scripts/

# Type checking
make type-check
# or
mypy src/

# Run all quality checks
make all
```

## Troubleshooting

### Virtual Environment Not Found
```bash
# Recreate virtual environment
rm -rf venv
make venv
# or
bash scripts/setup_venv.sh --force
```

### Permission Issues
```bash
# Make scripts executable
chmod +x scripts/*.sh
```

### Package Installation Issues
```bash
# Upgrade pip and setuptools
source venv/bin/activate
pip install --upgrade pip setuptools wheel

# Clear pip cache
pip cache purge

# Reinstall requirements
pip install --force-reinstall -r requirements.txt
```

### Python Version Issues
The project requires Python 3.8 or later. Check your Python version:

```bash
python3 --version
```

If you need to install a newer Python version:
- **Ubuntu/Debian**: `sudo apt install python3.9 python3.9-venv`
- **macOS**: `brew install python@3.9`
- **Windows**: Download from [python.org](https://python.org)

## Environment Variables

Create a `.env` file in the project root for environment-specific settings:

```bash
# Copy example environment file
cp .env.example .env

# Edit with your settings
nano .env
```

Common environment variables:
- `DEBUG=true`: Enable debug mode
- `PYTHONPATH=./src`: Ensure src directory is in Python path
- `USGS_API_URL`: Custom USGS API endpoint
- `IRIS_API_URL`: Custom IRIS API endpoint

## CI/CD Integration

The virtual environment setup is integrated with CI/CD:

- **GitHub Actions**: Uses `actions/setup-python` with cached dependencies
- **Pre-commit Hooks**: Automatically run code quality checks
- **Docker**: Virtual environment setup included in Dockerfile

## Best Practices

1. **Always activate**: Never run Python commands without activating the virtual environment
2. **Update requirements**: Keep `requirements.txt` and `requirements-dev.txt` up to date
3. **Use Make targets**: Prefer `make test`, `make format`, etc. over direct commands
4. **Pin versions**: Use specific versions in requirements files for reproducibility
5. **Clean installs**: Occasionally recreate the virtual environment for a clean state

## Additional Resources

- [Python Virtual Environments Guide](https://docs.python.org/3/tutorial/venv.html)
- [Pip User Guide](https://pip.pypa.io/en/stable/user_guide/)
- [Black Code Formatter](https://black.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Pre-commit Hooks](https://pre-commit.com/)
