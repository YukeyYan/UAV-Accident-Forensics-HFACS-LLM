# Contributing to UAV Accident Forensics via HFACS-LLM Reasoning

Thank you for your interest in contributing to this project! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues
- Use the GitHub Issues tab to report bugs or request features
- Provide detailed information including:
  - System environment (OS, Python version, etc.)
  - Steps to reproduce the issue
  - Expected vs actual behavior
  - Error messages or logs

### Submitting Pull Requests
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 🛠️ Development Setup

### Prerequisites
- Python 3.8+
- Node.js 16+ (for visualization components)
- Git

### Local Development
```bash
# Clone your fork
git clone https://github.com/yourusername/UAV-accident-forensics-via-HFACS-LLM-reasoning.git
cd UAV-accident-forensics-via-HFACS-LLM-reasoning

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Install development dependencies
pip install pytest black flake8 mypy

# Install Node.js dependencies (optional)
cd web_components
npm install
cd ..
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest test_confidence_fix.py

# Run linting
flake8 .
black --check .
mypy .
```

## 📝 Code Style Guidelines

### Python Code Style
- Follow PEP 8 guidelines
- Use Black for code formatting: `black .`
- Use meaningful variable and function names
- Add docstrings for all functions and classes
- Maximum line length: 88 characters (Black default)

### Documentation
- Update README.md for significant changes
- Add docstrings for new functions/classes
- Include type hints where appropriate
- Comment complex logic

### Commit Messages
Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
- `feat(analysis): add new HFACS classification method`
- `fix(ui): resolve button click issue in report submission`
- `docs(readme): update installation instructions`

## 🧪 Testing Guidelines

### Test Structure
- Place tests in the same directory as the code being tested
- Use descriptive test names: `test_should_extract_fields_when_narrative_provided`
- Group related tests in classes
- Use fixtures for common test data

### Test Coverage
- Aim for >80% test coverage
- Test both happy path and error cases
- Include integration tests for critical workflows
- Mock external dependencies (OpenAI API, etc.)

### Example Test
```python
def test_smart_form_assistant_should_extract_fields():
    """Test that SmartFormAssistant extracts fields correctly"""
    assistant = SmartFormAssistant()
    narrative = "UAV lost communication at 1500 feet during training flight"
    
    result = assistant.analyze_narrative(narrative)
    
    assert len(result.extracted_fields) > 0
    assert result.completeness_score > 0
    assert 'altitude' in result.extracted_fields
```

## 🏗️ Architecture Guidelines

### Code Organization
```
├── streamlit_app.py          # Main Streamlit application
├── data_processor.py         # Data processing utilities
├── ai_analyzer.py           # AI analysis engine
├── hfacs_analyzer.py        # HFACS analysis implementation
├── smart_form_assistant.py  # Intelligent form assistance
├── knowledge_graph.py       # Knowledge graph functionality
├── enhanced_visualizations.py # Advanced visualizations
├── web_components/          # Node.js visualization server
├── data/                    # Data files
├── logs/                    # Log files
├── reports/                 # Generated reports
└── tests/                   # Test files
```

### Design Principles
- **Modularity**: Keep components loosely coupled
- **Testability**: Write testable code with clear interfaces
- **Performance**: Optimize for large datasets
- **Usability**: Prioritize user experience
- **Maintainability**: Write clean, documented code

### Adding New Features

#### 1. Analysis Components
For new analysis features:
- Extend base analyzer classes
- Implement proper error handling
- Add comprehensive tests
- Update documentation

#### 2. Visualization Components
For new visualizations:
- Use Plotly for consistency
- Ensure responsive design
- Add interactive features
- Test across browsers

#### 3. AI/LLM Features
For AI-related features:
- Handle API failures gracefully
- Implement fallback mechanisms
- Add confidence scoring
- Validate AI outputs

## 🔒 Security Guidelines

### API Keys and Secrets
- Never commit API keys or secrets
- Use environment variables
- Provide template files (.env.template)
- Document required environment variables

### Input Validation
- Validate all user inputs
- Sanitize data before processing
- Handle edge cases gracefully
- Prevent injection attacks

### Data Privacy
- Handle sensitive data appropriately
- Implement data anonymization where needed
- Follow data protection regulations
- Document data usage

## 📚 Documentation Guidelines

### Code Documentation
- Use clear, concise docstrings
- Include parameter and return type information
- Provide usage examples
- Document complex algorithms

### User Documentation
- Keep README.md up to date
- Provide clear installation instructions
- Include usage examples
- Document configuration options

### API Documentation
- Document all public functions
- Include parameter descriptions
- Provide example requests/responses
- Keep documentation in sync with code

## 🚀 Release Process

### Version Numbering
Follow Semantic Versioning (SemVer):
- MAJOR.MINOR.PATCH
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version number bumped
- [ ] CHANGELOG.md updated
- [ ] Release notes prepared
- [ ] Security review completed

## 🎯 Priority Areas for Contribution

### High Priority
- Performance optimization for large datasets
- Additional HFACS classification methods
- Enhanced error handling and recovery
- Mobile-responsive UI improvements

### Medium Priority
- Additional visualization types
- Export functionality improvements
- Integration with external systems
- Automated testing improvements

### Low Priority
- UI/UX enhancements
- Additional language support
- Advanced analytics features
- Documentation improvements

## 📞 Getting Help

### Communication Channels
- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: General questions and ideas
- Email: [your.email@example.com] for sensitive issues

### Resources
- Project Wiki: Detailed documentation
- Code Examples: See `examples/` directory
- API Reference: Generated from docstrings

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to UAV safety research! 🚁✨
