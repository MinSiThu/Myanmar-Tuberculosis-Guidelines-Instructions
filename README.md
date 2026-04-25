# Myanmar Tuberculosis Guidelines Instructions

**Myanmar–English Parallel Instructional Dataset for Tuberculosis Education and AI Research**

---

## Abstract

Tuberculosis (TB) remains a major public health challenge in Myanmar, where access to standardized medical education materials in the Myanmar language is limited. This repository presents the **Myanmar Tuberculosis Instruction Dataset**, a curated, professionally translated instructional dataset derived from World Health Organization (WHO) tuberculosis guidelines, Myanmar National TB Programme (NTP) protocols, and authoritative medical reference books.

The dataset provides Myanmar–English parallel instructional content covering TB diagnosis, treatment, drug management, and patient education. It is designed to support healthcare worker training, public health education, and AI-driven medical language model development in a low-resource language context.

**Keywords:** Tuberculosis, Myanmar Language, WHO Guidelines, National TB Programme, Medical Translation, Healthcare Education, Medical NLP, Low-Resource Languages

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Objectives](#2-objectives)
3. [Methodology](#3-methodology)
4. [Dataset Overview](#4-dataset-overview)
5. [Data Structure and Schema](#5-data-structure-and-schema)
6. [Sample Dataset Entry](#6-sample-dataset-entry)
7. [Ethical Considerations](#7-ethical-considerations)
8. [Validation and Quality Control](#8-validation-and-quality-control)
9. [Limitations](#9-limitations)
10. [Applications](#10-applications)
11. [Baseline AI and NLP Tasks Enabled](#11-baseline-ai-and-nlp-tasks-enabled)
12. [Licensing](#12-licensing)
13. [Versioning and Maintenance](#13-versioning-and-maintenance)
14. [Related Work and Research Gap](#14-related-work-and-research-gap)
15. [Societal Impact](#15-societal-impact)
16. [Conclusion](#16-conclusion)
17. [Acknowledgments](#acknowledgments)
18. [How to Cite](#how-to-cite-this-dataset)

---

## 1. Introduction

Myanmar is classified as a high tuberculosis burden country, facing challenges in early diagnosis, treatment adherence, and healthcare workforce training. While WHO-endorsed TB guidelines and technical documents are widely available in English, Myanmar-language instructional resources remain fragmented and insufficient, particularly in structured formats suitable for scalable education and AI applications.

Language barriers reduce effective guideline dissemination, healthcare worker comprehension, and patient adherence. Simultaneously, advances in artificial intelligence highlight the importance of high-quality, domain-specific datasets in under-represented languages.

This project addresses these challenges by translating, curating, and structuring authoritative TB instructional content into Myanmar language, aligned with global standards and national implementation needs.

---

## 2. Objectives

The objectives of this dataset are:

- To provide standardized TB instructional materials in Myanmar language
- To align local healthcare education with WHO and Myanmar NTP standards
- To support healthcare worker training and patient education
- To enable AI and NLP research in Myanmar medical contexts
- To contribute to equitable access to healthcare knowledge

---

## 3. Methodology

### 3.1 Source Materials

The dataset is compiled from:

- World Health Organization (WHO) tuberculosis guidelines and technical manuals
- Myanmar National TB Programme (NTP) protocols and implementation documents
- Standard medical reference textbooks related to tuberculosis

All source materials were publicly accessible or authorized for educational use.

### 3.2 Translation and Curation

- Medical translation was conducted by the author using standardized Myanmar medical terminology.
- Terminology alignment was maintained using a curated glossary consistent with WHO TB definitions.
- Content was rewritten into clear instructional formats suitable for education and AI instruction-tuning.
- Redundant or outdated information was excluded where appropriate.

### 3.3 Quality Assurance

Quality assurance included:

- Cross-checking translations against original English sources
- Terminology consistency validation
- Instructional clarity and structure review
- Alignment verification with WHO TB guideline versions available at the time of compilation

---

## 4. Dataset Overview

### 4.1 Dataset Access and Links

The Myanmar Tuberculosis Instruction Dataset (v1.0) is available at:

- **Primary Repository:** [https://huggingface.co/datasets/minsithu/Myanmar-Tuberculosis-Guidelines-Instructions](https://huggingface.co/datasets/minsithu/Myanmar-Tuberculosis-Guidelines-Instructions)
- **Source Code / Tools:** [https://github.com/MinSiThu/Myanmar-Tuberculosis-Guidelines-Instructions](https://github.com/MinSiThu/Myanmar-Tuberculosis-Guidelines-Instructions)
- **Documentation:** Included in repository README and dataset card

### 4.2 Dataset Statistics (v1.0)

| Metric | Value |
|--------|-------|
| Total records | 2,043 |
| Instruction–response pairs | 2,043 |
| TB categories | 7 |
| File size | ~2.3 MB |
| Formats | TSV, JSON |

### 4.3 Category Distribution

![Dataset Overview](https://github.com/MinSiThu/Myanmar-Tuberculosis-Guidelines-Instructions/blob/main/chart1_overview.png?raw=true)

| Category | Records |
|----------|---------|
| Treatment guidelines | 525 |
| Healthcare worker training | 499 |
| Drug-resistant TB (MDR-TB) | 266 |
| Patient education | 244 |
| Diagnostic protocols | 237 |
| Drug management | 218 |
| Infection control | 36 |

### 4.4 Dataset Visualizations

#### English Text Analysis

![English Text Lengths](https://github.com/MinSiThu/Myanmar-Tuberculosis-Guidelines-Instructions/blob/main/chart2_en_lengths.png?raw=true)

![English Vocabulary](https://github.com/MinSiThu/Myanmar-Tuberculosis-Guidelines-Instructions/blob/main/chart3_en_vocab.png?raw=true)

![English Statistics](https://github.com/MinSiThu/Myanmar-Tuberculosis-Guidelines-Instructions/blob/main/chart4_en_misc.png?raw=true)

#### Myanmar Text Analysis

![Myanmar Text Lengths](https://github.com/MinSiThu/Myanmar-Tuberculosis-Guidelines-Instructions/blob/main/chart5_my_lengths.png?raw=true)

![Myanmar Characters](https://github.com/MinSiThu/Myanmar-Tuberculosis-Guidelines-Instructions/blob/main/chart6_my_chars.png?raw=true)

![Myanmar Syllables](https://github.com/MinSiThu/Myanmar-Tuberculosis-Guidelines-Instructions/blob/main/chart7_my_syllables.png?raw=true)

#### Bilingual Dashboard

![Bilingual Dashboard](https://github.com/MinSiThu/Myanmar-Tuberculosis-Guidelines-Instructions/blob/main/chart8_bilingual_dashboard.png?raw=true)

---

## 5. Data Structure and Schema

Each dataset entry follows a standardized schema:

| Field | Description |
|-------|-------------|
| id | Unique record identifier |
| instruction_en | English instruction |
| instruction_my | Myanmar translation |
| response_en | English guideline response |
| response_my | Myanmar guideline response |
| category | TB domain category |
| source | WHO / NTP / Reference |
| guideline_version | Guideline year/version |
| notes | Optional annotations |

---

## 6. Sample Dataset Entry

```json
{
  "id": "TB-NTP-001",
  "instruction_en": "What is the primary healthcare strategy used by Myanmar National TB Programme?",
  "instruction_my": "မြန်မာနိုင်ငံ အမျိုးသား တီဘီရောဂါ တိုက်ဖျက်ရေး စီမံကိန်းသည် မည်သည့် ကျန်းမာရေး နည်းဗျူဟာကို အသုံးပြုသနည်း။",
  "response_en": "Myanmar National TB Programme uses a primary healthcare strategy to accelerate TB control activities.",
  "response_my": "မြန်မာနိုင်ငံအမျိုးသား တီဘီရောဂါ တိုက်ဖျက်ရေး စီမံကိန်း သည် ပဏာမ ကျန်းမာရေး စောင့်ရှောက်မှု နည်းဗျူဟာကို အသုံးပြု၍ တီဘီရောဂါ တိုက်ဖျက်ရေး လုပ်ငန်းများ ကို အရှိန်အဟုန်မြှင့် ဆောင်ရွက်ပါသည်။",
  "category": "Healthcare worker training",
  "source": "Myanmar NTP",
  "guideline_version": "2024",
  "notes": "Primary healthcare approach"
}
```

---

## 7. Ethical Considerations

The dataset contains no patient-level, personal, or clinical case data. All content is instructional and guideline-based.

The dataset is intended for educational and research use only and must not replace professional medical judgment or up-to-date clinical guidance.

---

## 8. Validation and Quality Control

Validation procedures included:

- Terminology normalization using a Myanmar medical glossary
- Guideline alignment checks
- Structural consistency review

The dataset prioritizes instructional fidelity, linguistic clarity, and guideline accuracy.

---

## 9. Limitations

- Guideline updates after dataset release may not be reflected.
- Translation interpretation bias may exist.
- The dataset focuses exclusively on TB and does not comprehensively cover TB-HIV or other comorbidities.
- It is instructional, not clinical outcome data.

---

## 10. Applications

The dataset supports:

- Healthcare worker training programs
- AI-powered TB education tools
- Myanmar-language medical LLM instruction tuning
- Medical question-answering systems
- Translation benchmarking
- Low-resource medical NLP research

---

## 11. Baseline AI and NLP Tasks Enabled

- Instruction tuning
- TB guideline QA
- Text classification
- Summarization
- Translation evaluation

---

## 12. Licensing

The dataset is released under the **MIT License**.

Copyright (c) 2026 Min Si Thu

Derivative translations of WHO materials are provided for educational and research purposes.

---

## 13. Versioning and Maintenance

- **Current version:** v1.0
- **Planned updates:** Aligned with WHO TB guideline revisions
- **Change log:** Documented per release

---

## 14. Related Work and Research Gap

Existing TB datasets focus primarily on structured clinical or high-resource language data. This dataset addresses the lack of instructional, guideline-based TB datasets in Myanmar language, enabling both healthcare education and AI research.

---

## 15. Societal Impact

This dataset contributes to:

- Improved access to standardized TB knowledge
- Reduced language barriers in healthcare education
- Empowerment of Myanmar-based AI research
- Progress toward healthcare knowledge equity

---

## 16. Conclusion

The Myanmar Tuberculosis Instruction Dataset provides a structured, authoritative, and AI-ready TB instructional resource in Myanmar language. It bridges global health standards with local accessibility, supporting healthcare capacity building and low-resource medical AI development.

---

## Acknowledgments

The author acknowledges the World Health Organization and Myanmar National TB Programme for publicly available guideline materials that informed this dataset.

---

## How to Cite This Dataset

```bibtex
@dataset{myanmar_tb_instruction_2026,
  title={Myanmar Tuberculosis Instruction Dataset},
  author={Min Si Thu},
  year={2026},
  version={1.0},
  url={https://huggingface.co/datasets/minsithu/Myanmar-Tuberculosis-Guidelines-Instructions}
}
```

---

## References

See [References.md](References.md) for the full list of source materials and authoritative references used in creating this dataset.

---

## Contact

For questions, contributions, or collaboration inquiries, please open an issue on the GitHub repository or contact the author through the Hugging Face dataset page.

