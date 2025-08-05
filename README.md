# Seismic Event Classification System

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Development Status](https://img.shields.io/badge/status-Phase%201%20Development-orange.svg)](STATUS.md)
[![Tests](https://github.com/seismic-classifier/seismic-classifier/workflows/tests/badge.svg)](https://github.com/seismic-classifier/seismic-classifier/actions)

A comprehensive Python-based machine learning platform for real-time seismic event detection, analysis, and classification. This system integrates with authoritative seismic data sources (USGS and IRIS) to provide intelligent earthquake monitoring and analysis capabilities.

## 🌍 Features

### 🔍 Real-Time Monitoring
- Continuous monitoring of global seismic activity
- Integration with USGS Earthquake Hazards Program API
- IRIS seismic waveform data processing using ObsPy
- Real-time event detection and classification

### 🤖 Machine Learning Capabilities
- Neural networks for deep pattern recognition
- Ensemble methods (Random Forest, XGBoost)
- Support Vector Machines with multiple kernels
- Automated hyperparameter optimization
- Model interpretability and explainability

### 📊 Advanced Signal Processing
- Multi-band frequency filtering and noise reduction
- Time-domain and frequency-domain feature extraction
- Wavelet transform analysis
- Spectrogram generation and analysis
- Signal quality assessment

### 📈 Interactive Visualization
- Real-time earthquake mapping with interactive controls
- Waveform and spectrogram visualization
- Model performance dashboards
- Geospatial analysis and 3D visualization
- Customizable alerts and notifications

### 🔧 Event Classification
- Tectonic vs. volcanic earthquakes
- Natural vs. artificial events (explosions, quarry blasts)
- Magnitude-based classification
- Depth-based analysis
- Regional seismic characteristics

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Git
- 4GB+ RAM recommended
- Internet connection for API access

### Installation

#### Option 1: Automated Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/seismic-classifier/seismic-classifier.git
   cd seismic-classifier
   ```

2. **Run automated setup**
   ```bash
   # Complete project setup with virtual environment
   make setup
   
   # Or use the setup script directly
   bash scripts/setup_venv.sh
   ```

3. **Activate virtual environment**
   ```bash
   source venv/bin/activate
   
   # Or use the helper script
   source scripts/activate_venv.sh
   ```

#### Option 2: Manual Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/seismic-classifier/seismic-classifier.git
   cd seismic-classifier
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   pip install -e .
   ```

4. **Setup pre-commit hooks** (optional but recommended)
   ```bash
   pre-commit install
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

> **⚠️ Important**: Always activate the virtual environment before working on the project.
> See [Virtual Environment Guide](docs/VIRTUAL_ENVIRONMENT.md) for detailed instructions.

### Basic Usage

#### 1. Download Earthquake Data
```bash
# Download recent earthquake data for training
python scripts/data_download.py --days 30 --min-magnitude 4.5
```

#### 2. Train a Classification Model
```bash
# Train machine learning models
python scripts/train_model.py --config config/config.yaml
```

#### 3. Start Real-Time Classification
```bash
# Begin real-time earthquake monitoring
python scripts/real_time_classifier.py
```

#### 4. Launch Interactive Dashboard
```bash
# Start the web dashboard
python dashboard/app.py
```

Visit `http://localhost:8050` to access the interactive dashboard.

## 📖 Documentation

- **[Project Status](STATUS.md)** - Current development progress and completed features
- **[Project Plan](docs/PROJECT_PLAN.md)** - Comprehensive development roadmap
- **[Virtual Environment Guide](docs/VIRTUAL_ENVIRONMENT.md)** - Virtual environment setup and usage
- **[Workflow Guidelines](docs/WORKFLOW.md)** - Development workflow and Git practices
- **[API Documentation](docs/api.md)** - Complete API reference (coming soon)
- **[Configuration Guide](docs/configuration.md)** - System configuration options (coming soon)
- **[Deployment Guide](docs/deployment.md)** - Production deployment instructions (coming soon)
- **[Contributing Guidelines](docs/CONTRIBUTING.md)** - How to contribute to the project (coming soon)

## 🏗️ Architecture

```
seismic-classifier/
├── src/                     # Source code
│   ├── data_pipeline/       # Data collection and processing
│   ├── feature_engineering/ # Signal processing and features
│   ├── models/             # Machine learning models
│   ├── visualization/      # Plotting and dashboard components
│   └── utils/              # Utility functions and helpers
├── dashboard/              # Web dashboard application
├── notebooks/              # Jupyter notebooks for analysis
├── tests/                  # Test suite
├── scripts/                # Automation and deployment scripts
├── config/                 # Configuration files
├── data/                   # Data storage
└── docs/                   # Documentation
```

## 🔧 Configuration

The system uses YAML configuration files for flexible setup:

```yaml
# config/config.yaml
api:
  usgs:
    base_url: "https://earthquake.usgs.gov/fdsnws/event/1/"
    rate_limit: 10
  iris:
    base_url: "IRIS"
    rate_limit: 5

data_collection:
  earthquake_filters:
    min_magnitude: 4.0
    max_magnitude: 9.0
  
machine_learning:
  neural_network:
    hidden_layers: [128, 64, 32]
    epochs: 100
```

## 🧪 Testing

Run the complete test suite:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test module
pytest tests/test_data_pipeline.py -v
```

## 📊 Example Usage

### Python API

```python
from src.data_pipeline import USGSClient, IRISClient
from src.models import NeuralNetworkClassifier
from src.feature_engineering import FeaturePipeline

# Initialize data clients
usgs = USGSClient()
iris = IRISClient()

# Fetch earthquake data
events = usgs.get_events(starttime="2024-01-01", min_magnitude=5.0)
waveforms = iris.get_waveforms(network="IU", station="ANMO")

# Extract features
feature_pipeline = FeaturePipeline()
features = feature_pipeline.extract_features(waveforms)

# Train classifier
classifier = NeuralNetworkClassifier()
classifier.fit(features, labels)

# Make predictions
predictions = classifier.predict(new_features)
```

### Command Line Interface

```bash
# Download and classify earthquakes from the last week
python scripts/real_time_classifier.py --days 7 --min-magnitude 4.0

# Train a new model with custom parameters
python scripts/train_model.py --model neural_network --epochs 200

# Export results to CSV
python scripts/export_results.py --format csv --output results.csv
```

## 🌐 Data Sources

### USGS Earthquake Hazards Program
- **Real-time earthquake catalogs**
- **Event metadata and parameters**
- **Geographic and temporal filtering**
- **Multiple output formats (GeoJSON, CSV, XML)**

### IRIS Data Management Center
- **High-quality seismic waveform data**
- **Global seismographic network access**
- **Multiple data formats (miniSEED, SAC)**
- **Station metadata and instrument responses**

## 🤝 Contributing

We welcome contributions from the seismology and machine learning communities! Please see our [Contributing Guidelines](docs/CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest tests/`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Standards

- **Python**: Follow PEP 8, use Black for formatting
- **Testing**: Maintain >90% code coverage
- **Documentation**: Include docstrings and type hints
- **Commits**: Use conventional commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **USGS Earthquake Hazards Program** for providing comprehensive earthquake data
- **IRIS Data Management Center** for seismic waveform data access
- **ObsPy Development Team** for the excellent seismological Python library
- **Seismology Research Community** for scientific guidance and feedback

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/seismic-classifier/seismic-classifier/issues)
- **Discussions**: [GitHub Discussions](https://github.com/seismic-classifier/seismic-classifier/discussions)
- **Email**: contact@seismic-classifier.org

## � Project Status

### ✅ Completed Features

#### 🏗️ Project Infrastructure
- [x] **Modern Project Structure**: Organized src/ layout with proper package hierarchy
- [x] **Virtual Environment Setup**: Automated venv creation and activation scripts
- [x] **Development Tools**: Pre-commit hooks, Black formatting, Flake8 linting, MyPy type checking
- [x] **Build System**: Modern pyproject.toml with setuptools, Makefile for common tasks
- [x] **Documentation**: Comprehensive README, project plan, workflow guidelines

#### 🔧 Development Environment
- [x] **VS Code Configuration**: Optimized settings, tasks, and launch configurations
- [x] **GitHub Integration**: CI/CD workflows for testing, documentation, and releases
- [x] **Code Quality**: Pre-commit hooks, automated formatting, security scanning
- [x] **Package Management**: Requirements files, development dependencies, optional extras
- [x] **Configuration System**: Flexible YAML-based configuration with environment overrides

#### 📦 Core Modules (Structure Created)
- [x] **Data Pipeline**: Module structure for USGS and IRIS API clients
- [x] **Feature Engineering**: Framework for signal processing and feature extraction
- [x] **Models**: ML model architecture and training pipeline structure
- [x] **Visualization**: Dashboard and plotting component organization
- [x] **Utils**: Logging, configuration, and helper utility modules

#### 🚀 Scripts and Automation
- [x] **Virtual Environment**: Automated setup, activation, and verification scripts
- [x] **Development Workflow**: Make targets for testing, building, and deployment
- [x] **GitHub Actions**: Automated testing, documentation building, and release management
- [x] **Pre-commit**: Code quality checks and automated formatting on commit

### 🚧 In Progress

#### 📊 Core Implementation (Phase 1)
- [ ] **USGS API Client**: Rate-limited client with error handling and caching
- [ ] **IRIS Data Client**: ObsPy integration for waveform data retrieval
- [ ] **Data Validation**: Quality control and data integrity checks
- [ ] **Database Layer**: Storage architecture for waveforms and metadata
- [ ] **Error Handling**: Comprehensive exception handling and resilience patterns

#### 🔬 Signal Processing (Phase 2)
- [ ] **Signal Preprocessing**: Multi-rate filtering, noise reduction, detrending
- [ ] **Feature Extraction**: Time-domain, frequency-domain, and wavelet features
- [ ] **Quality Assessment**: Signal-to-noise ratio and quality metrics
- [ ] **Feature Selection**: Automated importance ranking and dimensionality reduction

#### 🤖 Machine Learning (Phase 3)
- [ ] **Neural Networks**: CNN/RNN architectures for waveform classification
- [ ] **Ensemble Methods**: Random Forest, XGBoost, and SVM implementations
- [ ] **Model Training**: Cross-validation, hyperparameter tuning, performance evaluation
- [ ] **Model Serving**: REST API for real-time inference and batch processing

### 📅 Upcoming Milestones

#### Phase 1: Core Infrastructure (Current Focus)
**Target: End of Q1 2025**
- Complete data pipeline implementation
- Finalize configuration management system
- Implement comprehensive testing suite
- Deploy development environment documentation

#### Phase 2: Signal Processing & Feature Engineering
**Target: Q2 2025**
- Advanced signal processing algorithms
- Feature extraction and selection pipelines
- Signal quality assessment tools
- Performance optimization and benchmarking

#### Phase 3: Machine Learning Models
**Target: Q3 2025**
- Neural network architectures
- Traditional ML model implementations
- Model training and validation frameworks
- Real-time inference capabilities

#### Phase 4: Visualization & Dashboard
**Target: Q4 2025**
- Interactive web dashboard
- Real-time monitoring interface
- Geospatial analysis and mapping
- Model performance visualization

### 📈 Development Metrics

#### Code Quality Metrics
- **Test Coverage**: Target 90%+ (Infrastructure setup complete)
- **Code Style**: Black formatting enforced with pre-commit hooks
- **Type Coverage**: MyPy type checking configured and active
- **Security**: Bandit security scanning integrated into CI/CD

#### Project Health
- **Documentation**: Comprehensive README, project plan, and workflow docs ✅
- **CI/CD**: GitHub Actions for testing, docs, and releases ✅
- **Development Environment**: VS Code, virtual environment, and tools setup ✅
- **Code Organization**: Modern Python package structure with src/ layout ✅

### 🎯 Next Steps

1. **Implement USGS API Client** - Begin Phase 1 core infrastructure development
2. **Add ObsPy Integration** - Create IRIS data client for waveform retrieval
3. **Build Test Suite** - Add comprehensive unit and integration tests
4. **Create Sample Data Pipeline** - End-to-end data collection and processing demo
5. **Add Dashboard Prototype** - Basic web interface for system monitoring

## 🔮 Roadmap

- **Q1 2025**: Complete core infrastructure and data pipeline
- **Q2 2025**: Signal processing and feature engineering implementation
- **Q3 2025**: Machine learning models and real-time classification
- **Q4 2025**: Interactive dashboard and production deployment
- **2026**: Advanced features, mobile app, and community ecosystem

---

*Built with ❤️ for the global seismology community*
