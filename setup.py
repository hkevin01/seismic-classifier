#!/usr/bin/env python3
"""Setup script for Seismic Classifier."""

import os

from setuptools import find_packages, setup

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(this_directory, "README.md")
with open(readme_path, encoding="utf-8") as readme_file:
    long_description = readme_file.read()


# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as req_file:
        return [
            line.strip()
            for line in req_file
            if line.strip() and not line.startswith("#")
        ]


setup(
    name="seismic-classifier",
    version="0.1.0",
    author="Seismic AI Team",
    author_email="team@seismic-ai.example.com",
    description="Real-time seismic event classification using ML",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/seismic-classifier",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "pre-commit>=3.3.0",
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "safety>=2.3.0",
            "bandit>=1.7.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
            "myst-parser>=2.0.0",
        ],
        "jupyter": [
            "jupyter>=1.0.0",
            "ipykernel>=6.25.0",
            "ipywidgets>=8.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "seismic-train=seismic_classifier.cli:train_command",
            "seismic-classify=seismic_classifier.cli:classify_command",
            "seismic-dashboard=seismic_classifier.cli:dashboard_command",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
