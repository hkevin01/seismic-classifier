# Seismic Event Classification System

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
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

1. **Clone the repository**
   ```bash
   git clone https://github.com/seismic-classifier/seismic-classifier.git
   cd seismic-classifier
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. **Initialize the system**
   ```bash
   python scripts/data_download.py --help
   ```

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

- **[Project Plan](docs/PROJECT_PLAN.md)** - Comprehensive development roadmap
- **[API Documentation](docs/api.md)** - Complete API reference
- **[Configuration Guide](docs/configuration.md)** - System configuration options
- **[Deployment Guide](docs/deployment.md)** - Production deployment instructions
- **[Contributing Guidelines](docs/CONTRIBUTING.md)** - How to contribute to the project

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

## 🔮 Roadmap

- **Q1 2025**: Enhanced deep learning models and transfer learning
- **Q2 2025**: Real-time early warning system integration
- **Q3 2025**: Mobile application and edge computing support
- **Q4 2025**: Federated learning and multi-institutional collaboration

---

*Built with ❤️ for the global seismology community*
