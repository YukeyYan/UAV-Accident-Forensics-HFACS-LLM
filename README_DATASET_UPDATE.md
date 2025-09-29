# 📊 Dataset Release Information

## 🎯 Ground Truth Dataset Now Available

We are excited to announce the availability of our **expert-annotated UAV accident dataset** used in the research "UAV Accident Forensics via HFACS-LLM Reasoning: Low-Altitude Safety Insights".

### 📈 Dataset Highlights

- **📋 200 UAV Accident Reports**: Carefully curated from aviation safety databases (2010-2025)
- **🎯 3,600 Coded Data Points**: Complete HFACS 8.0 classifications
- **👨‍💼 Expert Annotated**: Validated by certified aviation safety experts
- **🔬 Research Grade**: Inter-rater reliability κ = 0.823
- **📊 Comprehensive Coverage**: 18 HFACS categories across 4 hierarchical levels

### 🗂️ Dataset Structure

```
01_Data/Ground_Truth/
└── ground_truth_standard_coded.csv    # Main dataset (200 records, 3,600 data points)
```

### 🔍 What's Included

#### Core Data Fields
- **Incident Identification**: ASRS accession numbers, timestamps
- **Narrative Content**: Complete incident descriptions and expert summaries  
- **HFACS Classifications**: 18-category expert annotations with confidence scores
- **Analysis Metadata**: Processing information and quality metrics

#### HFACS 8.0 Framework Coverage
- **Level 1 - Unsafe Acts** (3 categories): Skill errors, decision errors, violations
- **Level 2 - Preconditions** (7 categories): Environmental, technological, and personnel factors
- **Level 3 - Unsafe Supervision** (4 categories): Supervisory and planning issues
- **Level 4 - Organizational Influences** (4 categories): Culture, policy, resources, training

### 📊 Dataset Statistics

| Metric | Value |
|--------|-------|
| **Total Incidents** | 200 |
| **Time Span** | 2010-2025 (May) |
| **Data Points** | 3,600 |
| **Average Confidence** | 84.7% |
| **High Confidence Classifications** | 68% |
| **Most Common Category** | Decision-Making Errors (76%) |
| **Least Common Category** | Adverse Physiological (10%) |

### 🎓 Research Applications

This dataset enables research in:

- **Aviation Safety Analysis**: Quantitative human factors research
- **AI Model Development**: Training and validation of safety analysis models
- **Human Factors Studies**: Large-scale analysis of cognitive and organizational factors
- **Risk Management**: Development of predictive safety models
- **Regulatory Science**: Evidence-based policy development

### 📚 Quick Start

```python
import pandas as pd

# Load the dataset
df = pd.read_csv('01_Data/Ground_Truth/ground_truth_standard_coded.csv')

# Basic statistics
print(f"Dataset shape: {df.shape}")
print(f"Number of incidents: {len(df)}")

# HFACS category analysis
hfacs_categories = [col for col in df.columns if col.endswith('_Present')]
category_freq = df[hfacs_categories].sum().sort_values(ascending=False)
print("Top 5 HFACS Categories:")
print(category_freq.head())
```

### 🔒 Data Quality Assurance

- **✅ Expert Validation**: 3 certified aviation safety experts
- **✅ Quality Control**: Inter-rater reliability κ > 0.80
- **✅ Consistency Checks**: Systematic validation procedures
- **✅ Privacy Compliance**: All PII removed, ASRS guidelines followed
- **✅ Ethical Approval**: Institutional review board approved

### 📄 Citation

If you use this dataset, please cite:

```bibtex
@dataset{uav_hfacs_dataset_2024,
  title={UAV Accident Forensics Ground Truth Dataset},
  author={[Your Name] and [Co-authors]},
  year={2024},
  publisher={GitHub},
  url={https://github.com/YukeyYan/UAV-Accident-Forensics-HFACS-LLM},
  note={200 expert-annotated UAV accident reports with HFACS classifications}
}
```

### 📋 License and Usage

- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Permitted Uses**: Academic research, commercial use with attribution
- **Requirements**: Proper citation, ethical use guidelines
- **Restrictions**: No use without attribution

### 🔄 Release Timeline

- **Current Status**: Dataset prepared and validated
- **Public Release**: Upon paper acceptance
- **Preview Access**: Available for reviewers and collaborators
- **Full Release**: Complete dataset with documentation

### 📞 Access and Support

- **Dataset Documentation**: See [DATASET_README.md](DATASET_README.md)
- **Metadata**: Complete specifications in [dataset_metadata.json](dataset_metadata.json)
- **Technical Support**: GitHub Issues
- **Research Collaboration**: [Your Email]

### 🚀 Future Enhancements

- **v1.1.0**: Extended annotations with causal relationships
- **v2.0.0**: Expanded dataset with 500+ incidents
- **Multi-language**: International incident reports
- **Real-time Updates**: Continuous dataset expansion

---

**Note**: This dataset represents a significant contribution to UAV safety research, providing the first comprehensive, expert-annotated collection of UAV accidents with standardized HFACS classifications. The complete dataset will be publicly released upon acceptance of the associated research paper.

For early access or collaboration opportunities, please contact the research team.
