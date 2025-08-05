# Contributing to Seismic Event Classification System

We welcome contributions from the seismology and machine learning communities! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

This project adheres to the Contributor Covenant [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to conduct@seismic-classifier.org.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic knowledge of seismology concepts (helpful but not required)
- Familiarity with machine learning (for ML contributions)

### Areas of Contribution

We welcome contributions in the following areas:

- **Data Pipeline**: USGS/IRIS API improvements, data validation
- **Signal Processing**: Feature extraction, filtering algorithms
- **Machine Learning**: New models, hyperparameter optimization
- **Visualization**: Dashboard improvements, plotting functions
- **Documentation**: User guides, API docs, tutorials
- **Testing**: Unit tests, integration tests, performance tests
- **Performance**: Optimization, caching, scaling

## Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/seismic-classifier.git
   cd seismic-classifier
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

5. **Run tests to verify setup**
   ```bash
   pytest tests/ -v
   ```

## Contributing Guidelines

### Issue Reporting

Before creating an issue, please:

1. **Search existing issues** to avoid duplicates
2. **Use the appropriate template** (bug report, feature request)
3. **Provide clear, detailed information**
4. **Include relevant system information**

### Feature Requests

When proposing new features:

1. **Describe the use case** and motivation
2. **Consider the scope** and complexity
3. **Discuss implementation approaches**
4. **Consider backwards compatibility**

### Bug Reports

When reporting bugs:

1. **Provide reproducible steps**
2. **Include error messages and stack traces**
3. **Specify environment details**
4. **Attach relevant configuration files**

## Pull Request Process

### Before Submitting

1. **Create a feature branch** from `develop`
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following coding standards

3. **Add or update tests** for your changes

4. **Update documentation** as needed

5. **Run the test suite**
   ```bash
   pytest tests/ -v
   flake8 src tests
   black src tests
   mypy src
   ```

### PR Requirements

- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] New functionality has tests
- [ ] Documentation is updated
- [ ] Commit messages are descriptive
- [ ] PR description explains changes

### Review Process

1. **Automated checks** must pass (CI/CD pipeline)
2. **Code review** by maintainers
3. **Testing** on different environments
4. **Documentation review** for user-facing changes
5. **Final approval** and merge

## Coding Standards

### Python Code Style

- **PEP 8** compliance with line length of 88 characters
- **Black** for code formatting
- **Type hints** for function signatures
- **Docstrings** for all public functions and classes

### Naming Conventions

- **Variables and functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Private members**: `_leading_underscore`
- **Modules**: `lowercase` or `snake_case`

### Code Organization

```python
"""Module docstring explaining purpose."""

import standard_library
import third_party_packages
import local_modules

from typing import List, Optional, Dict

# Constants
DEFAULT_TIMEOUT = 30

class ExampleClass:
    """Class docstring."""
    
    def __init__(self, param: str) -> None:
        """Initialize with parameter."""
        self.param = param
    
    def public_method(self, data: List[float]) -> Optional[Dict]:
        """Process data and return results."""
        pass
    
    def _private_method(self) -> None:
        """Internal helper method."""
        pass
```

### Error Handling

- Use specific exception types
- Provide meaningful error messages
- Log errors appropriately
- Include context in error messages

```python
try:
    result = process_seismic_data(waveform)
except InvalidWaveformError as e:
    logger.error(f"Failed to process waveform {waveform.id}: {e}")
    raise ProcessingError(f"Waveform processing failed: {e}") from e
```

## Testing Guidelines

### Test Structure

- **Unit tests**: Test individual functions/classes
- **Integration tests**: Test component interactions
- **End-to-end tests**: Test complete workflows
- **Performance tests**: Test for speed and memory usage

### Writing Tests

```python
import pytest
from unittest.mock import Mock, patch

from src.data_pipeline import USGSClient
from src.exceptions import APIError

class TestUSGSClient:
    """Test USGS API client functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = USGSClient()
    
    def test_successful_request(self):
        """Test successful API request."""
        # Test implementation
        pass
    
    @patch('requests.get')
    def test_api_error_handling(self, mock_get):
        """Test API error handling."""
        mock_get.side_effect = APIError("API unavailable")
        
        with pytest.raises(APIError):
            self.client.get_events(starttime="2024-01-01")
```

### Test Coverage

- Aim for >90% code coverage
- Focus on critical paths and edge cases
- Test both success and failure scenarios
- Include performance benchmarks for critical functions

## Documentation

### Code Documentation

- **Docstrings** for all public APIs
- **Type hints** for function parameters and returns
- **Inline comments** for complex logic
- **README updates** for significant changes

### API Documentation

```python
def extract_features(
    waveform: Stream,
    feature_types: List[str],
    window_length: float = 60.0
) -> Dict[str, float]:
    """Extract seismic features from waveform data.
    
    Args:
        waveform: ObsPy Stream object containing seismic data
        feature_types: List of feature types to extract
        window_length: Analysis window length in seconds
    
    Returns:
        Dictionary mapping feature names to values
    
    Raises:
        InvalidWaveformError: If waveform data is invalid
        FeatureExtractionError: If feature extraction fails
    
    Example:
        >>> from obspy import read
        >>> st = read("earthquake.mseed")
        >>> features = extract_features(st, ["peak_amplitude", "rms"])
        >>> print(features["peak_amplitude"])
        0.0025
    """
```

### User Documentation

- **Installation guides** with clear steps
- **Usage examples** with real data
- **Configuration documentation**
- **Troubleshooting guides**
- **API reference** with examples

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Email**: contact@seismic-classifier.org for private matters

### Getting Help

- **Documentation**: Check existing docs first
- **Search Issues**: Look for similar problems
- **Ask Questions**: Use GitHub Discussions
- **Join Community**: Participate in code reviews and discussions

### Recognition

We value all contributions and maintain a [Contributors](CONTRIBUTORS.md) file recognizing community members.

## Development Workflow

### Branch Strategy

- `main`: Production-ready code
- `develop`: Integration branch for new features
- `feature/*`: Individual feature branches
- `hotfix/*`: Critical bug fixes
- `release/*`: Release preparation

### Commit Messages

Use conventional commit format:

```
type(scope): description

body (optional)

footer (optional)
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
- `feat(models): add neural network classifier`
- `fix(data): handle missing earthquake metadata`
- `docs: update installation instructions`

### Release Process

1. **Feature freeze** on `develop`
2. **Create release branch** from `develop`
3. **Testing and bug fixes** on release branch
4. **Merge to main** and tag release
5. **Deploy to production**
6. **Merge back to develop**

## Security

### Reporting Vulnerabilities

Please report security vulnerabilities to security@seismic-classifier.org. Do not create public issues for security problems.

### Secure Coding Practices

- **Validate all inputs** from external sources
- **Use parameterized queries** for database access
- **Sanitize user data** before processing
- **Keep dependencies updated**
- **Follow principle of least privilege**

---

Thank you for contributing to the Seismic Event Classification System! Your efforts help advance earthquake science and early warning capabilities worldwide.

For questions about contributing, please contact: contribute@seismic-classifier.org
