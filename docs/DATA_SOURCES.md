# NASA Open Data Sources: AstroLongevity

This document proves that AstroLongevity uses authentic, unmodified data from NASA's Open Science Data Repository (OSDR). It is written for judges reviewing compliance with the NASA Space Apps Challenge open data requirement.

---

## Data Repository

All datasets are sourced from:

**NASA Open Science Data Repository (OSDR)**
URL: https://osdr.nasa.gov
Operated by: NASA Biological and Physical Sciences Division
Access: Fully public, no account required

---

## Dataset 1: OSD-21

| Field | Value |
|---|---|
| Study ID | OSD-21 |
| Mission | Early rodent spaceflight experiment |
| Organism | Mus musculus (house mouse) |
| Tissue | Skeletal muscle |
| Data Type | Microarray (normalized intensities) |
| File Retrieved | GLDS-21_array_normalized_intensities_probe_GLmicroarray.csv |
| Rows After Cleaning | 230,756 probe entries |
| Direct URL | https://osdr.nasa.gov/bio/repo/data/studies/OSD-21 |
| API Endpoint Used | https://osdr.nasa.gov/osdr/data/osd/files/21 |
| Role in Project | Cross-study concordance (microarray validation) |

---

## Dataset 2: OSD-101

| Field | Value |
|---|---|
| Study ID | OSD-101 |
| Mission | Rodent Research 4 (RR-4) |
| Organism | Mus musculus C57BL/6J |
| Tissue | Skeletal muscle |
| Data Type | Bulk RNA-Seq (Differential Expression) |
| File Retrieved | GLDS-101_rna_seq_differential_expression_rRNArm_GLbulkRNAseq.csv |
| File Size | 18.14 MB |
| Rows | 23,257 genes |
| Columns | 13 |
| Direct URL | https://osdr.nasa.gov/bio/repo/data/studies/OSD-101 |
| API Endpoint Used | https://osdr.nasa.gov/osdr/data/osd/files/101 |
| QC Gate 1 (Rows > 1000) | PASS |
| QC Gate 2 (Zero null gene IDs) | PASS |
| QC Gate 3 (All columns numeric) | PASS |

---

## Dataset 3: OSD-104

| Field | Value |
|---|---|
| Study ID | OSD-104 |
| Mission | Rodent Research 1 (RR-1) |
| Organism | Mus musculus C57-6J SLS |
| Tissue | Skeletal muscle |
| Data Type | Bulk RNA-Seq (Differential Expression) |
| File Retrieved | GLDS-104_rna_seq_differential_expression_rRNArm_GLbulkRNAseq.csv |
| File Size | 17.68 MB |
| Rows | 22,437 genes |
| Columns | 13 |
| Flight Samples | M23, M24, M25, M26, M27, M28 (6 samples) |
| Ground Control Samples | M33, M34, M35, M36, M37, M38 (6 samples) |
| Direct URL | https://osdr.nasa.gov/bio/repo/data/studies/OSD-104 |
| API Endpoint Used | https://osdr.nasa.gov/osdr/data/osd/files/104 |
| QC Gate 1 (Rows > 1000) | PASS |
| QC Gate 2 (Zero null gene IDs) | PASS |
| QC Gate 3 (All columns numeric) | PASS |

---

## How Data Is Retrieved in Code

Data retrieval is fully automated in `notebooks/AstroLongevity_Data_Pipeline.ipynb`.

The pipeline:
1. Calls the NASA OSDR file manifest API for each dataset numeric ID.
2. Reads the returned JSON to find the correct differential expression CSV file.
3. Streams the file to local disk in 8,192-byte chunks using `requests.get(stream=True)`.
4. Loads the disk file into a pandas DataFrame.
5. Runs three fail-closed quality control gates before any analysis begins.

No data is generated, simulated, or modified. All values in the analysis are read directly from NASA pre-computed output files.

---

## Data Storage

Downloaded files are permanently saved to:
- Google Drive: `/content/drive/MyDrive/AstroLongevity_Data_Final/`

Raw CSV files are excluded from this repository via `.gitignore` due to size. The pipeline notebook downloads them fresh from NASA servers on each run.
