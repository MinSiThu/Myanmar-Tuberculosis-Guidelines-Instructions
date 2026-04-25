# Myanmar Tuberculosis Guidelines Instructions

<a href="https://doi.org/10.5281/zenodo.19751460"><img src="https://zenodo.org/badge/1213564334.svg" alt="DOI"></a>

A bilingual instructional dataset built to support Myanmar's ongoing fight against tuberculosis — turning life-saving guidelines into a usable resource for healthcare workers, educators, and AI researchers working with low-resource languages.

---

<img src="https://github.com/MinSiThu/Myanmar-Tuberculosis-Guidelines-Instructions/blob/main/logo.png?raw=true" alt="Myanmar Tuberculosis Guidelines Instructions Logo" width="400" />

## Abstract

Tuberculosis is still one of Myanmar's biggest public health problems. Part of the difficulty is that good, standardized TB education materials in the Myanmar language are hard to come by — most of what's authoritative exists only in English. This repository introduces the **Myanmar Tuberculosis Instruction Dataset**, a curated parallel corpus drawn from WHO tuberculosis guidelines, the Myanmar National TB Programme (NTP), and established medical reference texts.

The data is organized as Myanmar–English instruction–response pairs covering diagnosis, treatment regimens, drug management, and patient education. It's meant to serve two audiences at once: people training healthcare workers or building patient education tools, and researchers building Myanmar-language medical NLP systems where decent training data has been almost nonexistent.

**Keywords:** Tuberculosis · Myanmar Language · WHO Guidelines · National TB Programme · Medical Translation · Healthcare Education · Medical NLP · Low-Resource Languages

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

Myanmar sits on the WHO list of high TB burden countries, and the on-the-ground picture matches the label: late diagnosis, treatment dropouts, and a healthcare workforce that often has to learn from English-only materials. WHO guidelines and technical documents are excellent, but they assume a reader who can work comfortably in English. Myanmar-language TB resources do exist — they're just scattered, inconsistent, and rarely formatted in a way that's useful for either training programs or modern AI systems.

That gap matters in two ways. First, language friction slows down how guidelines actually reach the clinic and the patient. Second, because medical AI now depends heavily on instruction-tuned datasets, low-resource languages risk being left out of every useful tool built in the next few years.

This project is one attempt to close that gap for tuberculosis specifically. The work involved translating, restructuring, and aligning authoritative TB content into Myanmar so it follows global standards while remaining usable in a Myanmar clinical and educational setting.

---

## 2. Objectives

The dataset was built with the following goals in mind:

- Provide standardized TB instructional content in the Myanmar language
- Keep local healthcare education aligned with WHO and Myanmar NTP standards
- Support training for healthcare workers as well as patient-facing education
- Make Myanmar-language medical AI and NLP research practical
- Push back, even modestly, against the inequity in who gets access to good medical knowledge

---

## 3. Methodology

### 3.1 Source Materials

The content draws on three sources:

- WHO tuberculosis guidelines and technical manuals
- Myanmar NTP protocols and implementation documents
- Standard medical reference textbooks covering tuberculosis

Everything used was either publicly available or cleared for educational use.

### 3.2 Translation and Curation

Translation was carried out by the authors, working from a controlled glossary of Myanmar medical terminology. The goal wasn't a literal word-for-word rendering — those tend to read awkwardly in Burmese — but a clear instructional version that a Myanmar healthcare worker would actually find readable. Definitions were kept consistent with WHO TB usage, and content was rewritten into instruction–response pairs suitable for teaching and for instruction tuning. Where source material was redundant or had been superseded, it was dropped.

### 3.3 Quality Assurance

Quality checks happened at several points:

- Translations were cross-referenced against the original English source
- Terminology was checked for internal consistency across entries
- Each entry was reviewed for instructional clarity and structural soundness
- Content was verified against the WHO TB guideline versions in effect at the time of compilation

---

## 4. Dataset Overview

### 4.1 Dataset Access and Links

The Myanmar Tuberculosis Instruction Dataset (v1.0) is hosted at:

- **Primary repository:** [https://huggingface.co/datasets/minsithu/Myanmar-Tuberculosis-Guidelines-Instructions](https://huggingface.co/datasets/minsithu/Myanmar-Tuberculosis-Guidelines-Instructions)
- **Source code and tools:** [https://github.com/MinSiThu/Myanmar-Tuberculosis-Guidelines-Instructions](https://github.com/MinSiThu/Myanmar-Tuberculosis-Guidelines-Instructions)
- **Documentation:** in the repository README and dataset card

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

The distribution leans toward treatment and training, which reflects where the biggest practical gaps in Myanmar-language material currently sit. Infection control is intentionally lighter — most of the relevant guidance is short, procedural, and didn't need padding to bulk up the count.

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

Every record uses the same schema:

| Field | Description |
|-------|-------------|
| id | Unique record identifier |
| instruction_en | Instruction in English |
| instruction_my | Myanmar translation of the instruction |
| response_en | Guideline-aligned response in English |
| response_my | Guideline-aligned response in Myanmar |
| category | TB domain category |
| source | WHO, NTP, or reference text |
| guideline_version | Year/version of the source guideline |
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

There is no patient-level data, no personal data, and no clinical case material in the dataset. Everything is instructional and traces back to published guidelines.

The dataset is meant for education and research. It is not a substitute for clinical judgment, and it should not be used as the sole reference for treating real patients — guidelines change, and any real clinical decision needs the most current source.

---

## 8. Validation and Quality Control

### 8.1 Terminology Standardization

The starting point for translation was a controlled vocabulary built from the Myanmar National TB Programme. NTP terminology is what's actually used in Myanmar clinical practice, so anchoring the dataset there makes the language feel correct to a working clinician rather than translated.

That vocabulary was then applied across the dataset so the same disease, the same regimen, and the same diagnostic procedure get the same Burmese term every time. Where NTP didn't have a defined term — which happens, especially for newer or more technical concepts — we fell back to WHO-aligned phrasing and adapted carefully, keeping the clinical meaning intact.

After the vocabulary was settled, the actual translation and curation work began. Each entry was checked against the controlled terminology before being accepted. Doing it in this order — terminology first, then content — was a deliberate choice; it cuts down on inconsistency much more effectively than trying to harmonize terms after the fact.

### 8.2 Validation Procedures

- Terminology normalization against the Myanmar medical glossary
- Alignment checks against the source guideline
- Structural review for schema consistency

The priority throughout was instructional fidelity and linguistic clarity, in that order.

---

## 9. Limitations

A few things are worth being upfront about:

- WHO and NTP guidelines are revised periodically, and updates released after this dataset will not be reflected until a new version is published.
- Translation involves interpretation, and some bias is unavoidable, even with controlled terminology.
- The scope is TB only. TB–HIV co-management and other comorbidities are touched on but not covered comprehensively.
- This is instructional content, not clinical outcome data. It cannot be used to evaluate treatment effectiveness on its own.

---

## 10. Applications

The dataset has been built with the following uses in mind:

- Training programs for healthcare workers
- AI-assisted TB education tools
- Instruction tuning of Myanmar-language medical LLMs
- Medical question answering in Myanmar
- Benchmarking translation systems on medical text
- General low-resource medical NLP research

---

## 11. Baseline AI and NLP Tasks Enabled

- Instruction tuning
- TB guideline question answering
- Text classification by TB domain category
- Summarization of guideline content
- Translation evaluation between Myanmar and English in a medical setting

---

## 12. Licensing

Released under the **MIT License**.

Copyright (c) 2026 Min Si Thu and Khin Myat Noe.

Translations derived from WHO materials are provided strictly for educational and research purposes.

---

## 13. Versioning and Maintenance

- **Current version:** v1.0
- **Planned updates:** to track WHO TB guideline revisions
- **Change log:** maintained per release

---

## 14. Related Work and Research Gap

Most TB-related datasets are either structured clinical data or English-only research corpora. There is very little instructional, guideline-based TB material in Myanmar that has been organized in a way that's useful for both education and machine learning. This dataset is an attempt to fill that specific gap rather than to compete with broader clinical or epidemiological datasets.

---

## 15. Societal Impact

The hoped-for impact is straightforward:

- TB knowledge that's already standardized internationally becomes more accessible inside Myanmar
- Language barriers in healthcare education shrink, even if only by a small amount
- Myanmar-based AI research gets a usable resource it didn't have before
- The broader project of healthcare knowledge equity moves a step forward

---

## 16. Conclusion

The Myanmar Tuberculosis Instruction Dataset is a focused attempt to make authoritative TB knowledge usable in Myanmar — both for the people teaching and learning it, and for the systems being built on top of it. It connects global standards with local accessibility, and it's offered as a starting point that other contributors are welcome to build on.

---

## Acknowledgments

The authors thank the World Health Organization and the Myanmar National TB Programme for making the guideline materials that underpin this dataset publicly available.

---

## How to Cite This Dataset

```bibtex
@dataset{myanmar_tb_instruction_2026,
  title={Myanmar Tuberculosis Instruction Dataset},
  author={Min Si Thu, Khin Myat Noe},
  year={2026},
  version={1.0},
  url={https://huggingface.co/datasets/minsithu/Myanmar-Tuberculosis-Guidelines-Instructions}
}
```

---

## References

See [References.md](References.md) for the full list of source materials used in building this dataset.

---

## Contact

For questions, contributions, or collaboration, please open an issue on the GitHub repository or reach out through the Hugging Face dataset page.