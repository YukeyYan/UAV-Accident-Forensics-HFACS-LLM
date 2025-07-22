# UAV Accident Forensics via HFACS-LLM Reasoning: Low-Altitude Safety Insights

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-green.svg)](https://openai.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Project Overview

An intelligent UAV accident analysis system based on ASRS (Aviation Safety Reporting System) data, integrating **HFACS 8.0 framework** with **Large Language Model reasoning** for comprehensive low-altitude flight safety insights. The system leverages OpenAI GPT-4o-mini to simulate expert analysis processes while introducing innovative features to enhance analysis efficiency and accuracy.

### 🚀 Key Features

- **📝 Intelligent Incident Reporting**: AI-powered narrative analysis with automatic field extraction
- **🤖 LLM-Enhanced Analysis**: GPT-4o-mini for root cause analysis, risk assessment, and recommendation generation
- **🧠 HFACS 8.0 Human Factors Analysis**: Professional human factors analysis based on the latest HFACS framework
- **📈 Multi-dimensional Trend Analysis**: Comprehensive data visualization including temporal trends, risk distribution, and keyword analysis
- **🔍 Similarity-based Case Retrieval**: Intelligent case matching and recommendation system
- **🌐 Advanced 3D Visualizations**: Interactive knowledge graphs and real-time dashboards
- **📊 Professional Reporting**: Automated generation of comprehensive analysis reports

### 💡 Innovation Highlights

- **Smart Form Assistant**: AI-driven narrative analysis with professional question generation
- **Real-time Risk Assessment**: Multi-factor intelligent risk level evaluation
- **Knowledge Graph Integration**: Complex relationship visualization between incident factors
- **HFACS-LLM Fusion**: Combining traditional human factors analysis with modern AI reasoning
- **3D Interactive Visualizations**: Advanced web-based 3D knowledge graphs and dashboards

## 🛠️ Technical Architecture

### Technology Stack
- **Frontend**: Streamlit + Plotly + HTML/CSS
- **Backend**: Python + Pandas + SQLite
- **AI Engine**: OpenAI GPT-4o-mini with Function Calling
- **Advanced Visualization**: Node.js + Three.js + D3.js + Socket.io
- **Data Processing**: Pandas + NumPy + SciPy
- **Database**: SQLite (lightweight, easy deployment)

### System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │ Smart Form      │    │  HFACS Analyzer │
│   Web Interface │◄──►│ Assistant       │◄──►│   (18 Classes)  │
└─────────────────┘    │ (GPT-4o-mini)   │    └─────────────────┘
         │              └─────────────────┘             │
         ▼                       │                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Knowledge Graph │    │   SQLite DB     │    │ 3D Visualization│
│ (Relationships) │◄──►│   (Storage)     │◄──►│ (Node.js Server)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                      │
         ▼                       ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ AI Analyzer     │    │ Data Processor  │    │ Enhanced        │
│ (Risk & Cause)  │◄──►│ (CSV Handler)   │◄──►│ Visualizations  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📦 Installation and Deployment

### Prerequisites
- Python 3.8+
- Node.js 16+ (for advanced visualizations)
- 8GB+ RAM (recommended)
- 2GB+ disk space

### Quick Start

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/UAV-accident-forensics-via-HFACS-LLM-reasoning.git
cd UAV-accident-forensics-via-HFACS-LLM-reasoning
```

2. **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Node.js Dependencies (Optional - for 3D visualizations)**
```bash
cd web_components
npm install
cd ..
```

4. **Configure Environment Variables**
```bash
# Copy environment template
cp .env.template .env

# Edit .env file with your OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here
```

5. **Prepare Data**
Ensure your ASRS CSV file is in the project root directory

6. **Launch the System**
```bash
# Method 1: Using launch script (recommended)
python run.py

# Method 2: Direct Streamlit execution
streamlit run streamlit_app.py

# Method 3: With advanced visualizations
# Terminal 1:
streamlit run streamlit_app.py --server.port 8501

# Terminal 2:
cd web_components && npm start
```

7. **Access the System**
- Main Interface: http://localhost:8501
- Advanced 3D Visualizations: http://localhost:3000

## 📖 Usage Guide

### 1. Data Management
- Load historical ASRS data in the "Data Management" section
- System automatically processes CSV files and stores in SQLite database
- Supports data cleaning, feature extraction, and risk classification

### 2. Intelligent Incident Reporting
- **Narrative-First Mode**: Input detailed incident description, AI extracts structured information
- **Professional Question Generation**: AI generates domain-specific questions based on narrative
- **Supplementary Information**: Add additional details and answer AI-generated questions
- **Smart Submission**: Choose between standard submission or direct analysis

### 3. AI-Enhanced Analysis
- **Multi-dimensional Risk Assessment**: 6-factor risk radar analysis
- **Root Cause Analysis**: LLM-powered causal factor identification
- **Incident Flow Visualization**: Complete incident sequence mapping
- **Knowledge Graph Integration**: Factor relationship visualization

### 4. HFACS 8.0 Analysis
- **18-Category Classification**: Complete HFACS 8.0 framework support
- **4-Level Hierarchy**: Unsafe Acts, Preconditions, Supervision, Organizational Influences
- **3D Visualization**: Interactive 3D HFACS hierarchy exploration
- **Professional Reporting**: Detailed HFACS analysis reports

### 5. Advanced Visualizations
- **3D Knowledge Graphs**: Interactive factor relationship networks
- **Real-time Dashboards**: Live data monitoring and updates
- **Causal Network Analysis**: Interactive cause-effect chain exploration
- **HFACS 3D Hierarchy**: Three-dimensional framework visualization

### 6. Trend Analysis and Case Retrieval
- **Temporal Trend Analysis**: Time-series incident patterns
- **Risk Distribution Analysis**: Multi-dimensional risk assessment
- **Similarity-based Retrieval**: AI-powered case matching
- **Predictive Analytics**: Trend forecasting and risk prediction

## ⚙️ Configuration

### Environment Variables
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_api_key          # Required
OPENAI_MODEL=gpt-4o-mini             # AI model
OPENAI_TEMPERATURE=0.1               # Generation temperature

# Database Configuration
DATABASE_PATH=asrs_data.db           # Database path
CSV_DATA_PATH=your_asrs_data.csv     # CSV file path

# Server Configuration
STREAMLIT_SERVER_PORT=8501           # Streamlit port
NODE_SERVER_PORT=3000                # Node.js visualization port

# Analysis Configuration
MAX_SIMILAR_CASES=5                  # Maximum similar cases
ANALYSIS_CONFIDENCE_THRESHOLD=0.6    # Analysis confidence threshold
ENABLE_3D_VISUALIZATIONS=true        # Enable advanced visualizations
```

## 🧪 Testing

### Run Tests
```bash
# System functionality test
python test_confidence_fix.py

# Button functionality test
python test_button_fix.py

# LLM integration test
python test_llm_integration.py

# Run all tests
pytest tests/ -v
```

## 📊 System Monitoring

### Performance Monitoring
- Enable monitoring: `ENABLE_PERFORMANCE_MONITORING=True`
- View logs: `tail -f asrs_system.log`
- Monitor memory and CPU usage

### Service Status
- Streamlit Service: http://localhost:8501/health
- Node.js Service: http://localhost:3000/api/health

## 🔧 Troubleshooting

### Common Issues

1. **OpenAI API Errors**
   - Verify API key correctness
   - Check account quota
   - Ensure network connectivity

2. **Data Loading Failures**
   - Confirm CSV file path and format
   - Check file encoding (UTF-8 recommended)
   - Review error logs

3. **3D Visualization Issues**
   - Ensure Node.js dependencies are installed
   - Check port 3000 availability
   - Verify WebGL support in browser

4. **Memory Issues**
   - Reduce batch size: `MAX_RECORDS_PER_BATCH`
   - Enable caching: `ENABLE_CACHE=True`
   - Increase system memory

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Code formatting
black .
flake8 .

# Type checking
mypy .
```

### Contribution Guidelines
- Follow PEP 8 coding standards
- Add appropriate test cases
- Update relevant documentation
- Ensure all tests pass

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support and Contact

- **Issues**: Please submit issues on GitHub Issues
- **Feature Requests**: Welcome to submit Pull Requests
- **Technical Discussions**: Join our GitHub Discussions

## 🙏 Acknowledgments

- ASRS data providers
- OpenAI GPT-4o-mini API
- Streamlit open-source framework
- Three.js and D3.js communities
- All contributors and users

## 📚 Citation

If you use this system in your research, please cite:

```bibtex
@software{uav_accident_forensics_2024,
  title={UAV Accident Forensics via HFACS-LLM Reasoning: Low-Altitude Safety Insights},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/UAV-accident-forensics-via-HFACS-LLM-reasoning}
}
```

---

**Note**: This system is intended for research and educational purposes. It should not be used as a formal accident investigation tool without proper validation and expert oversight.
