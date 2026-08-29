# AstroLongevity

**NASA Space Apps Challenge 2026 | Theme: The Next Frontier | Team: Astrophel | Members: Labony Sur, Aupurba Sarker**

🌐 **Live Dashboard:** [https://astrolongevity.vercel.app/](https://astrolongevity.vercel.app/)

---

## What This Project Does

AstroLongevity is an open-source computational biology platform that analyzes NASA spaceflight transcriptomics data to study muscle and bone loss in microgravity, and identifies candidate therapeutic compounds that could reverse the damage.

The platform has three components:

1. **Python Data Pipeline** — Automatically retrieves RNA-Seq differential expression data from the NASA Open Science Data Repository (OSDR) via REST API, validates data integrity through three fail-closed quality control gates, and performs Principal Component Analysis and differential expression analysis.

2. **Cross-Study Concordance Analysis** — Compares gene expression data across three independent NASA spaceflight missions (OSD-21, OSD-101, OSD-104) to identify genes that are consistently dysregulated across missions, producing a robust spaceflight muscle atrophy signature.

3. **In-Silico Drug Screening** (planned for hackathon weekend) — Uses the LINCS L1000 Connectivity Map to score FDA-approved compounds against the atrophy signature. Compounds whose gene expression effect is the opposite of the spaceflight damage are ranked as candidate countermeasures.

Results are presented through an interactive **Next.js web dashboard**.

---

## Why This Matters

Astronauts lose approximately 1% of weight-bearing bone density per month in microgravity, even with two hours of daily exercise. A crewed Mars mission takes three years. Current physical countermeasures are not sufficient for that duration.

The same molecular pathways that break down muscle in space (myostatin signaling, IGF1 suppression) also drive sarcopenia, age-related muscle loss, in elderly people on Earth. Bangladesh's population aged 60 and above is projected to reach 28 million by 2050. This platform can be used by researchers in Bangladesh and globally to screen drug candidates for sarcopenia computationally, at near-zero cost, instead of running expensive wet-laboratory experiments.

---

## NASA Datasets Used

All data is sourced directly from the [NASA Open Science Data Repository (OSDR)](https://osdr.nasa.gov). See [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md) for complete provenance details and validation proof.

| Dataset | Mission | Type | Genes | Status |
|---|---|---|---|---|
| OSD-21 | Early rodent spaceflight | Microarray | 230,756 probes | Downloaded and cleaned |
| OSD-101 | Rodent Research 4 (RR-4) | RNA-Seq DE | 23,257 | Downloaded, QC passed |
| OSD-104 | Rodent Research 1 (RR-1) | RNA-Seq DE | 22,437 | Downloaded, QC passed, PCA complete |

Data is retrieved via the NASA OSDR REST API:
```
https://osdr.nasa.gov/osdr/data/osd/files/{numeric_id}
```

---

## Key Result (Validated)

The H19 gene in OSD-104 shows significant downregulation in spaceflight samples:

| Metric | Value | Source |
|---|---|---|
| Group Mean (Ground Control) | 113,282 | NASA OSD-104 |
| Group Mean (Spaceflight) | 76,442 | NASA OSD-104 |
| Log2 Fold Change | -0.5675 | NASA OSD-104 |
| Adjusted P-value | 5.57e-10 | NASA OSD-104 |
| Manual cross-check | log2(76442/113282) = -0.568 | Calculated |

The manual calculation matches the NASA reference to three significant figures, confirming the pipeline reads authentic, unmodified NASA data.

---

## Repository Structure

```
AstroLongevity/
├── notebooks/
│   └── AstroLongevity_Data_Pipeline.ipynb   # Main Colab notebook (run this)
├── docs/
│   ├── AstroLongevity_Research_Paper.tex    # Full IEEE-format research paper
│   ├── DATA_SOURCES.md                      # NASA open data provenance and validation
│   ├── UI_MOCKUP.md                         # Next.js dashboard design plan
│   ├── PITCH_SCRIPT.md                      # 30-second global video script
│
│   ├── PCA_Publication_Plot.png             # Generated PCA figure (real NASA data)
│   └── Note book.pdf                        # PDF export of executed notebook
├── visualizer/                              # Next.js web dashboard (in development)
│   └── src/app/
└── README.md
```

---

## How to Run the Pipeline

1. Open `notebooks/AstroLongevity_Data_Pipeline.ipynb` in Google Colab.
2. Run all cells in order (Runtime > Run All).
3. The pipeline will:
   - Mount your Google Drive.
   - Download OSD-101 and OSD-104 from NASA OSDR.
   - Run quality control validation on both datasets.
   - Generate the PCA plot.
   - Save everything to `/content/drive/MyDrive/AstroLongevity_Data_Final/`.

No local installation is required. The entire pipeline runs on the free Google Colab tier.

## What Is Already Done

- NASA OSDR API data retrieval (OSD-21, OSD-101, OSD-104 downloaded and verified)
- Three-gate quality control validation (all datasets passed)
- PCA analysis of OSD-104 (PC1 = 21.9%, PC2 = 11.0%, clear FLT/GC separation)
- H19 differential expression result cross-validated against NASA reference
- **Cross-study concordance analysis** across OSD-101 and OSD-104 (141-gene signature extracted)
- **Cross-species translational benchmark** against human clinical atrophy literature (IGF1 validated as a conserved marker)
- Full IEEE research paper with mathematical feasibility study
- NASA open data compliance documentation

## What Will Be Built During the Hackathon (Nov 14-15)

- LINCS L1000 signature reversal and drug ranking (against the newly established 141-gene signature)
- Interactive Next.js dashboard with live gene expression visualization, PCA scatter plots, and cross-species benchmarking

---

## Local Event

**Event:** NASA Space Apps Challenge 2026, Dhaka Local Event (BASIS)
**Team Name:** Astrophel
**Team Members:** Labony Sur (Team Leader), Aupurba Sarker
**Submission Portals:** NASA global portal and BASIS local portal (`nsac.basis.org.bd`)
**Hackathon Dates:** November 14-15, 2026

---

<div align="center">
<table>
  <tr>
    <td width="60%" valign="top">
      <h2>Team Details</h2>
      <p><b>Project Name:</b> AstroLongevity</p>
      <p><b>Team Name:</b> Astrophel</p>
      <p><b>Team Leader:</b> Labony Sur<br><b>Email:</b> labonysur473@gmail.com</p>
      <p><b>Team Member:</b> Aupurba Sarker<br><b>Email:</b> sarker2305101269@diu.edu.bd</p>
    </td>
    <td width="40%" valign="top" align="center">
      <img src="public/Group%20Photo/team_photo.jpg" alt="Team Astrophel" width="250">
    </td>
  </tr>
</table>
</div>
