# 28 UAV-Specific Risk Factors Framework

## 📋 Overview

This document describes the **28 UAV-Specific Risk Factors** framework, a comprehensive evidence-based taxonomy for UAV safety analysis and risk assessment. The framework extends the HFACS 8.0 (Human Factors Analysis and Classification System) with UAV-specific risk factors identified through systematic multi-source analysis.

## 🎯 Framework Development Methodology

The 28 risk factors were systematically derived through:

### Primary Data Sources
- **Literature Review**: 56+ peer-reviewed papers (2010-2025) on UAV safety and human factors
- **ASRS Database**: 847 UAV incident reports (2016-2023)
- **Regulatory Frameworks**: FAA Part 107, EASA Easy Access Rules, ICAO Annex 2
- **Technical Documentation**: DJI Manuals, ArduPilot Documentation, PX4 User Guide
- **Industry Standards**: ASTM F3196, ISO 21384, RTCA DO-362, JARUS SORA
- **Expert Validation**: Aviation safety professionals (7-15 years experience)

### Statistical Validation
- **Inter-rater Reliability**: Cohen's κ = 0.82
- **Content Validity**: 95%
- **Model Fit**: CFI = 0.94, RMSEA = 0.06
- **Intraclass Correlation**: ICC = 0.79

## 📊 Framework Structure

### Distribution Across HFACS Levels

| HFACS Level | Category | Number of Factors |
|-------------|----------|-------------------|
| **Level 4** | Organizational Influences | 7 factors |
| **Level 3** | Unsafe Supervision | 6 factors |
| **Level 2** | Preconditions for Unsafe Acts | 11 factors |
| **Level 1** | Unsafe Acts | 4 factors |
| **Total** | | **28 factors** |

### Theoretical Categories

The 28 factors are organized into 5 theoretical categories:

1. **Remote Operation Challenges** (7 factors)
   - URF-08, URF-09, URF-12, URF-21, URF-22, URF-27, URF-28
   - Challenges arising from the remote nature of UAV operations

2. **Automation Complexity** (6 factors)
   - URF-13, URF-18, URF-19, URF-24, URF-25, URF-26
   - Complexities introduced by automated systems and multiple flight modes

3. **Communication Dependencies** (4 factors)
   - URF-14, URF-15, URF-16, URF-17
   - Dependencies on communication links for safe operations

4. **Regulatory Considerations** (6 factors)
   - URF-01, URF-02, URF-03, URF-04, URF-10, URF-11
   - Regulatory compliance and authorization challenges

5. **Power System Limitations** (5 factors)
   - URF-05, URF-06, URF-07, URF-20, URF-23
   - Limitations imposed by power systems and environmental factors

## 🔍 Complete Factor List

### Level 4 - Organizational Influences (7 factors)

| ID | Factor Name | Primary Sources |
|----|-------------|-----------------|
| **URF-01** | Part 107 Regulatory Compliance | FAA Part 107 (2016), FAA-G-8082-22 (2021), Clothier et al. (2015) |
| **URF-02** | LAANC Authorization Management | FAA LAANC v2.0 (2019), Vance & Malik (2019) |
| **URF-03** | Visual Line of Sight Management | FAA Part 107.31, EASA UAS.OPEN.020 (2020), JARUS SORA (2019) |
| **URF-04** | Beyond Visual Line of Sight Operations | RTCA DO-362 (2018), ASTM F3196-17 |
| **URF-05** | Power System Resource Management | DJI Battery Guidelines (2022), ArduPilot Docs (2023) |
| **URF-06** | Energy and Endurance Management | PX4 User Guide (2023), Boukoberine et al. (2019) |
| **URF-07** | Predictive Maintenance Scheduling | ISO 21384-3:2019, ASTM F3201-16 |

### Level 3 - Unsafe Supervision (6 factors)

| ID | Factor Name | Primary Sources |
|----|-------------|-----------------|
| **URF-08** | Ground Control Station Interface Complexity | Tvaryanas et al. (2008), Cummings et al. (2007) |
| **URF-09** | Delayed Feedback System Management | Hing & Oh (2009), Ruff et al. (2004) |
| **URF-10** | LAANC System Integration Supervision | FAA LAANC Plan (2018), Kopardekar et al. (2016) |
| **URF-11** | Airspace Authorization Process Management | ICAO Annex 2 (2016), FAA JO 7200.23 (2020) |
| **URF-12** | UAV Emergency Procedure Supervision | FAA AC 107-2A (2021), ASTM F3005-14a |
| **URF-13** | Multi-Aircraft Operation Coordination | Chung et al. (2018), ISO 21384-2:2019 |

### Level 2 - Preconditions for Unsafe Acts (11 factors)

| ID | Factor Name | Primary Sources |
|----|-------------|-----------------|
| **URF-14** | Command and Control Link Reliability | RTCA DO-362 (2018), Matolak & Sun (2017) |
| **URF-15** | Telemetry Data Accuracy and Timeliness | MAVLink v2.0 (2023), Koubaa et al. (2019) |
| **URF-16** | Communication and Control Range Limitations | FCC Part 15 (2020), Yanmaz et al. (2018) |
| **URF-17** | Progressive Signal Degradation | Rappaport (2002), Khuwaja et al. (2018) |
| **URF-18** | Flight Mode Confusion | Endsley (2017), DJI/PX4 Documentation (2023) |
| **URF-19** | Automation Over-Dependency | Parasuraman & Riley (1997), Cummings (2014) |
| **URF-20** | Weather Condition Sensitivity | FAA AC 00-6B (2016), Guzman et al. (2020) |
| **URF-21** | Remote Operation Spatial Disorientation | Gibb et al. (2010), Williams (2004) |
| **URF-22** | Visual Reference Limitations | McCarley & Wickens (2005), DJI/PX4 Docs (2023) |
| **URF-23** | Battery Performance Limitations | LiPo Battery Handbook (2022), Traub (2016) |
| **URF-24** | Automated System Performance Degradation | PX4 IMU Calibration (2023), Groves (2013) |

### Level 1 - Unsafe Acts (4 factors)

| ID | Factor Name | Primary Sources |
|----|-------------|-----------------|
| **URF-25** | Autopilot System Interaction Errors | DJI/PX4/ArduPilot Documentation (2023) |
| **URF-26** | Flight Mode Transition Errors | Sarter & Woods (1995), DJI/PX4 Docs (2023) |
| **URF-27** | Visual Reference Limitation Errors | Wickens & McCarley (2008), ArduPilot FPV Manual (2023) |
| **URF-28** | Delayed System Feedback Errors | Sheridan (1992), DJI Latency Analysis (2021) |

## 📚 Key Literature Sources

### Regulatory Documents
- **FAA Part 107** (14 CFR Part 107, 2016) - Small Unmanned Aircraft Systems
- **FAA Advisory Circular AC 107-2A** (2021) - Small UAS Operations
- **EASA Easy Access Rules for UAS** (2020) - European UAS regulations
- **ICAO Annex 2** (11th Edition, 2016) - Rules of the Air

### Industry Standards
- **RTCA DO-362** (2018) - Command and Control Data Link MOPS
- **ASTM F3196-17** (2017) - Standard Practice for Detect and Avoid
- **ISO 21384-3:2019** - UAS Operational Procedures
- **JARUS SORA** (Edition 2.0, 2019) - Specific Operations Risk Assessment

### Technical Manuals
- **DJI Technical Manuals** (2021-2023) - Battery safety, flight modes, transmission systems
- **ArduPilot Documentation** (2023) - Autopilot, telemetry, mission planning
- **PX4 User Guide** (2023) - Flight modes, battery estimation, failsafe procedures

### Peer-Reviewed Literature
- **Clothier, R. A., et al. (2015)** - Handbook of Unmanned Aerial Vehicles, Springer
- **Tvaryanas, A. P., et al. (2008)** - Human factors in remotely piloted aircraft operations
- **Parasuraman, R., & Riley, V. (1997)** - Humans and automation: Use, misuse, disuse, abuse
- **Endsley, M. R. (2017)** - From here to autonomy: Lessons learned from human-automation research
- **Cummings, M. L. (2014)** - Man versus machine or man + machine?

### Incident Data
- **ASRS Database** (2016-2023) - 847 UAV incident reports analyzed
  - Part 107 compliance issues (ACN 1650000+ series)
  - Battery-related incidents (ACN 1400000+ series)
  - C2 link failures, mode confusion, weather incidents

## 🎯 Applications

### 1. Incident Analysis
- Systematic classification of UAV incidents using UAV-specific factors
- Identification of contributing factors at multiple organizational levels
- Trend analysis and pattern recognition in UAV safety data

### 2. Risk Assessment
- Proactive identification of UAV-specific hazards
- Risk prioritization based on validated factor categories
- Integration with Safety Management Systems (SMS)

### 3. Training Development
- Evidence-based training program design
- Focus areas identified through factor analysis
- Competency assessment frameworks

### 4. Regulatory Compliance
- Systematic evaluation of Part 107 compliance
- LAANC authorization process assessment
- VLOS/BVLOS operational risk management

### 5. Safety Culture Assessment
- Organizational safety maturity evaluation
- Identification of systemic safety issues
- Continuous improvement initiatives

## 🔧 Implementation Guidelines

### Usage Recommendations
1. **Use in conjunction with standard HFACS 8.0 categories**
   - The 28 factors complement, not replace, standard HFACS
   - Apply both frameworks for comprehensive analysis

2. **Multiple factors may apply to a single incident**
   - UAV incidents often involve multiple contributing factors
   - Document all applicable factors for thorough analysis

3. **Validate factor applicability with domain experts**
   - Consult UAV operations experts for complex cases
   - Consider operational context and cultural differences

4. **Update factor definitions based on operational experience**
   - Framework should evolve with technology and regulations
   - Incorporate lessons learned from new incident data

### Compatibility
- **HFACS Version**: 8.0
- **UAV Regulations**: FAA Part 107, EASA, ICAO
- **Data Format**: YAML (compatible with JSON for automated processing)
- **Software Integration**: Compatible with existing HFACS-UAV analysis tools

## 📊 Validation Evidence

### Expert Panel
- **Size**: 5 domain experts
- **Experience Range**: 7-15 years
- **Disciplines**:
  - UAV Human Factors Research
  - Military UAV Operations
  - Aviation Safety Management
  - Commercial Remote Pilot Operations
  - UAV Systems Engineering

### Statistical Metrics
- **Inter-rater Reliability**: Cohen's κ = 0.82 (substantial agreement)
- **Intraclass Correlation**: ICC = 0.79 (good reliability)
- **Content Validity**: 95% (excellent validity)
- **Model Fit**: CFI = 0.94, RMSEA = 0.06 (excellent fit)

### Data Coverage
- **Literature Papers**: 56 peer-reviewed publications
- **ASRS Incidents**: 847 UAV incident reports
- **Regulatory Documents**: 15 key regulations and guidelines
- **Technical Manuals**: 20 manufacturer and open-source manuals
- **Industry Standards**: 12 relevant standards (ASTM, ISO, RTCA)

## 📖 Citation

If you use this framework in your research, please cite:

```
Yan, Y., et al. (2025). 28 UAV-Specific Risk Factors: A Comprehensive Framework 
for UAV Safety Analysis. UAV-Accident-Forensics-HFACS-LLM Project.
GitHub: https://github.com/YukeyYan/UAV-Accident-Forensics-HFACS-LLM
```

## 📄 License

This framework is released under the Creative Commons Attribution 4.0 International License (CC BY 4.0).

## 🔗 Related Resources

- **Main Project Repository**: [UAV-Accident-Forensics-HFACS-LLM](https://github.com/YukeyYan/UAV-Accident-Forensics-HFACS-LLM)
- **26 UAV Enhancement Patterns**: `HFACS_UAV/config/complete_uav_enhancement_patterns.yaml`
- **Ground Truth Dataset**: `data/ground_truth/ground_truth_standard_coded.csv`
- **HFACS-UAV System Documentation**: Project README and documentation files

## 📧 Contact

For questions, suggestions, or collaboration opportunities, please open an issue on the GitHub repository.

---

**Last Updated**: 2025-10-01  
**Version**: 1.0  
**Status**: Validated and Published

