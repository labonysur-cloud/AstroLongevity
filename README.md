# AstroLongevity

**Author: Labony Sur**

🚀 **Live Dashboard:** [https://astrolongevity.vercel.app/](https://astrolongevity.vercel.app/)

---

## What This Project Does

AstroLongevity is an open-source computational biology platform that analyzes NASA spaceflight transcriptomics data to study muscle and bone loss in microgravity, and identifies candidate therapeutic compounds that reverse the damage using in-silico drug screening.

The platform has three core components:

1. **Python Data Pipeline** – Automatically retrieves RNA-Seq normalized counts and differential expression statistics from the NASA Open Science Data Repository (OSDR) via REST API, validates data integrity through robust structural and transcriptomic data integrity gates, and performs Principal Component Analysis (PCA) with strict variance stabilization.

2. **Cross-Study Concordance Analysis** – Computes the directional intersection of gene expression across independent NASA spaceflight missions (OSD-101, OSD-104 ONLY) to identify genes that are consistently dysregulated in microgravity, producing a robust 141-gene spaceflight muscle atrophy signature (OSD-21 is retained for future cross-platform validation).

3. **In-Silico Drug Screening** – Dynamically queries the Ma'ayan Lab LINCS L1000 CDS2 API to score thousands of small-molecule perturbagens against the spaceflight atrophy signature. Compounds whose gene expression effect mathematically reverses the spaceflight damage (e.g., Withaferin A, Narciclasine) are ranked as candidate countermeasures.

Results are presented through a fully interactive **Next.js web dashboard**.

---

## Why This Matters

Astronauts lose approximately 1% of weight-bearing bone density per month in microgravity, even with two hours of daily exercise. A crewed Mars mission takes three years. Current physical countermeasures are not sufficient for that duration.

The same molecular pathways that break down muscle in space also drive sarcopenia, age-related muscle loss, in elderly people on Earth. Bangladesh's population aged 60 and above is projected to reach 28 million by 2050. This platform allows researchers globally to screen drug candidates for sarcopenia computationally, at near-zero cost, AstroLongevity narrows the experimental search space by identifying transcriptional signatures associated with spaceflight muscle loss and prioritizing candidate compounds for downstream validation.

---

## NASA Datasets Used

All data is sourced directly from the [NASA Open Science Data Repository (OSDR)](https://osdr.nasa.gov). 

| Dataset | Mission | Type | Genes | Status |
|---|---|---|---|---|
| OSD-21 | Early rodent spaceflight | Microarray | 230,756 probes | Downloaded and cleaned |
| OSD-101 | Rodent Research 4 (RR-4) | RNA-Seq Normalized Counts | 23,257 | Ingested, Concordance Computed |
| OSD-104 | Rodent Research 1 (RR-1) | RNA-Seq Normalized Counts | 22,437 | Ingested, PCA Complete |

Data is retrieved dynamically via the NASA OSDR REST API:
```
https://osdr.nasa.gov/osdr/data/osd/files/{numeric_id}
```

---

## Repository Structure

```
AstroLongevity/
├── notebooks/
│   └── AstroLongevity_Data_Pipeline.ipynb   # Main Jupyter notebook (Run this)
├── public/data/                             # Pre-computed static JSON endpoints
│   ├── benchmark_stats.json
│   ├── concordant_signature.json
│   ├── l1000_drug_candidates.json
│   ├── pca_coordinates.json
│   └── Reversal_Heatmap.png
├── src/                                     # Next.js web dashboard components
└── docs/
    └── AstroLongevity_Research_Paper.tex    # IEEE-format research paper
```

---

## How to Run the Pipeline

1. Open `notebooks/AstroLongevity_Data_Pipeline.ipynb` in Google Colab or Jupyter Notebook.
2. Run all cells in order.
3. The pipeline will:
   - Download OSD-101 and OSD-104 from NASA OSDR.
   - Run quality control validation on the datasets.
   - Log2 transform normalized counts and generate the PCA coordinates.
   - Compute the cross-study concordance signature.
   - Hit the L1000CDS2 API to discover spaceflight-reversal drug candidates.
   - Export all results seamlessly as JSON to `public/data/` for the Next.js frontend.

No local installation or massive database download is required. The entire pipeline executes in under 3 minutes.

## Technical Milestones Achieved

- **NASA OSDR API Data Retrieval:** Implemented exact string matching to pull verified `Normalized_Counts` and `differential_expression` CSVs.
- **PCA Analysis:** Successfully variance-stabilized OSD-104 counts; PCA effectively separates Spaceflight and Ground Control samples, indicating a strong transcriptomic association with the experimental condition (PC1 = 80.8%, PC2 = 12.1%).
- **Cross-Study Concordance:** Computed the 141-gene intersection across OSD-101 and OSD-104, strictly matching directionality (`Log2fc_(Space Flight)v(Ground Control)`).
- **LINCS L1000 API Integration:** Dynamically mapped murine orthologs to human targets to query the L1000CDS2 API, successfully identifying *Withaferin A*, *LDN-193189*, and *Narciclasine* as high-scoring countermeasures.
- **Static Data Handoff:** Fully wired the Python backend to the Next.js frontend via high-performance JSON exports.

---

## Citations & Data Sources

This research utilizes data, APIs, and tools provided by the open science and bioinformatics communities. If you build upon this work, please ensure you cite the primary sources:

### NASA Open Science Data Repository (OSDR)
* **OSD-21**: NASA GeneLab. (2011). *Rodent spaceflight microarray - skeletal muscle normalized intensities*. [https://osdr.nasa.gov/bio/repo/data/studies/OSD-21](https://osdr.nasa.gov/bio/repo/data/studies/OSD-21)
* **OSD-101**: NASA GeneLab. (2017). *Rodent Research 4 (RR-4) RNA-Seq*. [https://osdr.nasa.gov/bio/repo/data/studies/OSD-101](https://osdr.nasa.gov/bio/repo/data/studies/OSD-101)
* **OSD-104**: NASA GeneLab. (2017). *Rodent Research 1 (RR-1) RNA-Seq*. [https://osdr.nasa.gov/bio/repo/data/studies/OSD-104](https://osdr.nasa.gov/bio/repo/data/studies/OSD-104)

### Bioinformatics Tools & APIs
* **L1000CDS2 (Drug Screening)**: Duan, Q., et al. (2016). *L1000CDS2: LINCS L1000 characteristic direction signatures search engine.* npj Systems Biology and Applications, 2(1), 1-12. [https://maayanlab.cloud/L1000CDS2](https://maayanlab.cloud/L1000CDS2)
* **MyGene.info (Ortholog Mapping)**: Xin, J., et al. (2016). *High-performance web services for querying gene and variant annotation.* Genome Biology, 17(1), 1-7. [https://mygene.info](https://mygene.info)
* **GenAge (Human Aging Genomic Resources)**: Tacutu, R., et al. (2018). *Human Ageing Genomic Resources: new and updated databases.* Nucleic Acids Research, 46(D1), D1083-D1090. [https://genomics.senescence.info/genes](https://genomics.senescence.info/genes)
* **PubChem (Chemical Structures)**: Kim, S., et al. (2021). *PubChem in 2021: new data content and improved web interfaces.* Nucleic Acids Research, 49(D1), D1388-D1395. [https://pubchem.ncbi.nlm.nih.gov](https://pubchem.ncbi.nlm.nih.gov)
* **RCSB PDB (Protein Structures)**: Burley, S. K., et al. (2021). *RCSB Protein Data Bank: powerful new tools for exploring 3D structures of biological macromolecules for basic and applied research and education in fundamental biology, biomedicine, biotechnology, bioengineering and energy sciences.* Nucleic Acids Research, 49(D1), D437-D451. [https://www.rcsb.org](https://www.rcsb.org)

---

