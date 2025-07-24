# Project Structure

This document describes the organization and structure of the UAV Accident Forensics via HFACS-LLM Reasoning project.

## 📁 Directory Structure

```
UAV-accident-forensics-via-HFACS-LLM-reasoning/
├── 📄 README.md                    # Main project documentation
├── 📄 LICENSE                      # MIT License
├── 📄 CHANGELOG.md                 # Version history and changes
├── 📄 CONTRIBUTING.md              # Contribution guidelines
├── 📄 PROJECT_STRUCTURE.md         # This file
├── 📄 requirements.txt             # Python dependencies
├── 📄 setup.py                     # Package setup configuration
├── 📄 Dockerfile                   # Docker container configuration
├── 📄 docker-compose.yml           # Docker Compose setup
├── 📄 .gitignore                   # Git ignore rules
├── 📄 .env.template                # Environment variables template
├── 📄 run.py                       # System launcher script
│
├── 🐍 Core Python Modules
│   ├── 📄 streamlit_app.py         # Main Streamlit application
│   ├── 📄 data_processor.py        # ASRS data processing utilities
│   ├── 📄 ai_analyzer.py           # AI-powered incident analysis
│   ├── 📄 hfacs_analyzer.py        # HFACS 8.0 framework implementation
│   ├── 📄 smart_form_assistant.py  # Intelligent form assistance
│   ├── 📄 knowledge_graph.py       # Knowledge graph functionality
│   └── 📄 enhanced_visualizations.py # Advanced visualization components
│
├── 🌐 Web Components (Node.js)
│   ├── 📄 package.json             # Node.js dependencies
│   ├── 📄 server.js                # Express server for 3D visualizations
│   └── 📁 public/
│       └── 📄 index.html           # 3D visualization interface
│
├── 🗂️ Data Directory
│   ├── 📄 sample_data.csv          # Sample ASRS data
│   └── 📄 .gitkeep                 # Keep directory in git
│
├── 📊 Reports Directory
│   ├── 📄 .gitkeep                 # Keep directory in git
│   └── 📝 Generated reports will be stored here
│
├── 📋 Logs Directory
│   ├── 📄 .gitkeep                 # Keep directory in git
│   └── 📝 System logs will be stored here
│
├── 🧪 Testing Files
│   ├── 📄 test_confidence_fix.py   # Confidence calculation tests
│   ├── 📄 test_button_fix.py       # UI functionality tests
│   └── 📄 test_llm_integration.py  # LLM integration tests
│
├── 📚 Documentation Files
│   ├── 📄 DEMO_GUIDE.md           # System demonstration guide
│   ├── 📄 SYSTEM_STATUS.md        # System status documentation
│   ├── 📄 FINAL_FIX_SUMMARY.md    # Final fixes summary
│   └── 📄 BUTTON_FIX_SUMMARY.md   # Button fixes documentation
│
├── ⚙️ GitHub Configuration
│   └── 📁 .github/
│       └── 📁 workflows/
│           └── 📄 ci.yml           # CI/CD pipeline configuration
│
└── 🗃️ Database Files (Generated)
    └── 📄 asrs_data.db             # SQLite database (created at runtime)
```

## 🔧 Core Components

### 1. Main Application (`streamlit_app.py`)
- **Purpose**: Primary Streamlit web interface
- **Features**: 
  - Multi-page navigation system
  - User interface for all system functions
  - Session state management
  - Page routing and redirects

### 2. Data Processing (`data_processor.py`)
- **Purpose**: ASRS data import and processing
- **Features**:
  - CSV file parsing and validation
  - Data cleaning and normalization
  - SQLite database operations
  - Feature extraction and classification

### 3. AI Analysis Engine (`ai_analyzer.py`)
- **Purpose**: LLM-powered incident analysis
- **Features**:
  - OpenAI GPT-4o-mini integration
  - Risk assessment and classification
  - Root cause analysis
  - Recommendation generation

### 4. HFACS Analyzer (`hfacs_analyzer.py`)
- **Purpose**: Human Factors Analysis and Classification System
- **Features**:
  - 18-category HFACS classification
  - 4-level hierarchy analysis
  - Professional reporting
  - Visualization generation

### 5. Smart Form Assistant (`smart_form_assistant.py`)
- **Purpose**: Intelligent form filling assistance
- **Features**:
  - Narrative analysis and field extraction
  - Professional question generation
  - Confidence scoring
  - Data completeness assessment

### 6. Knowledge Graph (`knowledge_graph.py`)
- **Purpose**: Factor relationship visualization
- **Features**:
  - Network graph construction
  - Relationship mapping
  - Interactive visualization
  - 3D graph rendering

### 7. Enhanced Visualizations (`enhanced_visualizations.py`)
- **Purpose**: Advanced visualization components
- **Features**:
  - Multi-dimensional charts
  - Interactive dashboards
  - Real-time updates
  - Export functionality

## 🌐 Web Components Architecture

### Node.js Server (`web_components/server.js`)
- **Purpose**: Advanced 3D visualization server
- **Technology**: Express.js + Socket.io
- **Features**:
  - RESTful API endpoints
  - WebSocket real-time communication
  - 3D rendering support
  - Cross-origin resource sharing

### Frontend Interface (`web_components/public/index.html`)
- **Purpose**: 3D visualization interface
- **Technology**: Three.js + D3.js
- **Features**:
  - Interactive 3D knowledge graphs
  - Real-time data updates
  - User interaction handling
  - WebGL acceleration

## 📊 Data Flow Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CSV Data      │───▶│ Data Processor  │───▶│ SQLite Database │
│   (ASRS)        │    │ (Cleaning)      │    │ (Storage)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ User Interface  │◄──▶│ Smart Form      │◄──▶│ AI Analyzer     │
│ (Streamlit)     │    │ Assistant       │    │ (OpenAI)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ HFACS Analyzer  │    │ Knowledge Graph │    │ Visualizations  │
│ (Classification)│    │ (Relationships) │    │ (Charts/3D)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Report          │    │ 3D Visualization│    │ Enhanced        │
│ Generation      │    │ Server (Node.js)│    │ Analytics       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔌 API Endpoints

### Streamlit Internal APIs
- `/health` - System health check
- `/_stcore/health` - Streamlit core health
- Session state management (internal)

### Node.js Visualization APIs
- `GET /api/health` - Service health check
- `POST /api/visualize/knowledge-graph-3d` - 3D knowledge graph
- `POST /api/visualize/hfacs-3d` - 3D HFACS hierarchy
- `POST /api/visualize/realtime-dashboard` - Real-time dashboard
- `POST /api/visualize/causal-network` - Causal relationship network

### WebSocket Events
- `connection` - Client connection
- `subscribe-updates` - Subscribe to real-time updates
- `data-update` - Real-time data push
- `disconnect` - Client disconnection

## 🗄️ Database Schema

### SQLite Tables
```sql
-- ASRS incident reports
CREATE TABLE asrs_reports (
    id INTEGER PRIMARY KEY,
    date TEXT,
    time_of_day TEXT,
    location TEXT,
    aircraft TEXT,           -- JSON field
    narrative TEXT,
    primary_problem TEXT,
    contributing_factors TEXT,
    human_factors TEXT,
    risk_level TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Analysis results
CREATE TABLE analysis_results (
    id INTEGER PRIMARY KEY,
    report_id INTEGER,
    analysis_type TEXT,
    result TEXT,             -- JSON field
    confidence_score REAL,
    created_at TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES asrs_reports (id)
);

-- HFACS classifications
CREATE TABLE hfacs_classifications (
    id INTEGER PRIMARY KEY,
    report_id INTEGER,
    layer TEXT,
    category TEXT,
    subcategory TEXT,
    confidence REAL,
    created_at TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES asrs_reports (id)
);
```

## 🔧 Configuration Management

### Environment Variables (`.env`)
```bash
# Core Configuration
OPENAI_API_KEY=your_api_key
DATABASE_PATH=asrs_data.db
CSV_DATA_PATH=your_data.csv

# Server Configuration
STREAMLIT_SERVER_PORT=8501
NODE_SERVER_PORT=3000

# Analysis Configuration
MAX_SIMILAR_CASES=5
ANALYSIS_CONFIDENCE_THRESHOLD=0.6

# Feature Flags
ENABLE_3D_VISUALIZATIONS=true
ENABLE_REAL_TIME_UPDATES=true
```

### Python Dependencies (`requirements.txt`)
- Core: `streamlit`, `pandas`, `numpy`
- AI: `openai`, `requests`
- Visualization: `plotly`, `networkx`
- Database: `sqlite3` (built-in)
- Utilities: `python-dotenv`, `logging`

### Node.js Dependencies (`package.json`)
- Server: `express`, `socket.io`
- Visualization: `three`, `d3`, `vis-network`
- Utilities: `cors`, `helmet`

## 🚀 Deployment Architecture

### Development Environment
```bash
# Python virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Node.js environment
cd web_components
npm install
npm start
```

### Docker Deployment
```bash
# Single container
docker build -t uav-forensics .
docker run -p 8501:8501 -p 3000:3000 uav-forensics

# Docker Compose
docker-compose up -d
```

### Production Considerations
- Reverse proxy (Nginx) for SSL termination
- Load balancing for high availability
- Database backup and recovery
- Log aggregation and monitoring
- Security hardening and updates

## 📈 Performance Characteristics

### System Requirements
- **Minimum**: 4GB RAM, 2 CPU cores, 2GB storage
- **Recommended**: 8GB RAM, 4 CPU cores, 5GB storage
- **Large datasets**: 16GB RAM, 8 CPU cores, 10GB storage

### Performance Metrics
- **Startup time**: 30-60 seconds
- **Analysis time**: 10-30 seconds per incident
- **Concurrent users**: 10-50 (depending on resources)
- **Data processing**: 1000-10000 records per batch

### Scalability Considerations
- Horizontal scaling with load balancers
- Database optimization for large datasets
- Caching strategies for frequent queries
- CDN for static assets and visualizations

This structure provides a comprehensive foundation for UAV accident analysis while maintaining modularity, scalability, and ease of maintenance.
