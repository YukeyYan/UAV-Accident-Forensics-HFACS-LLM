"""
Setup script for UAV Accident Forensics via HFACS-LLM Reasoning
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    with open("README_GITHUB.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="uav-accident-forensics-hfacs-llm",
    version="1.0.0",
    author="UAV Safety Research Team",
    author_email="your.email@example.com",
    description="UAV Accident Forensics via HFACS-LLM Reasoning: Low-Altitude Safety Insights",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/UAV-accident-forensics-via-HFACS-LLM-reasoning",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "viz": [
            "plotly>=5.0",
            "networkx>=2.5",
            "seaborn>=0.11",
        ],
    },
    entry_points={
        "console_scripts": [
            "uav-forensics=run:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json", "*.yaml", "*.yml"],
    },
    keywords=[
        "UAV", "drone", "accident analysis", "HFACS", "LLM", "safety",
        "aviation", "forensics", "AI", "machine learning", "ASRS"
    ],
    project_urls={
        "Bug Reports": "https://github.com/yourusername/UAV-accident-forensics-via-HFACS-LLM-reasoning/issues",
        "Source": "https://github.com/yourusername/UAV-accident-forensics-via-HFACS-LLM-reasoning",
        "Documentation": "https://github.com/yourusername/UAV-accident-forensics-via-HFACS-LLM-reasoning/wiki",
    },
)
