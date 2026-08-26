# AstroLongevity

**NASA Space Apps Challenge 2026 Theme: The Next Frontier**

## Project Overview

*Target Categories: Science and Research, Space Exploration*

AstroLongevity is an in-silico computational biology and space pharmacology pipeline designed to systematically analyze spaceflight-induced physiological stress and identify potential therapeutic countermeasure candidates. By analyzing open-access spaceflight transcriptomics, the platform maps the molecular mechanisms of microgravity-induced skeletal muscle degradation and evaluates candidate small molecules capable of reversing these gene expression signatures.

## Datasets and Data Provenance

The pipeline integrates multi-cohort transcriptomic datasets directly from the **NASA Open Science Data Repository (OSDR / GeneLab)**:

* **OSD-21 (STS-108):** *Mus musculus* Gastrocnemius tissue analyzed via Affymetrix Microarray.
* **OSD-104 (Rodent Research-1 / RR-1):** *Mus musculus* Soleus tissue analyzed via Illumina RNA-Seq.
* **OSD-101 (Rodent Research-1 / RR-1):** *Mus musculus* Left Gastrocnemius tissue analyzed via Illumina RNA-Seq.
* **Reference Terrestrial & Compound Libraries:** Orthologous human aging/sarcopenia transcriptomic profiles and open chemical-perturbation signature libraries (such as LINCS L1000/Connectivity Map) for in-silico drug reversal scoring.

## Scientific Pipeline & Methodology

1. **Standardized Ingestion & Quality Control:** Implement fail-closed validation gates for raw and normalized transcript counts, log2-fold-change ($\log_2\text{FC}$) calculations, and statistical significance thresholds ($p$-value / FDR adjusted). Probe-to-gene mapping handles multi-probe resolution deterministically by maximizing absolute signal strength.
2. **Cross-Study Concordance Analysis:** Standardize mouse gene identifiers across different mission platforms (Microarray and RNA-Seq) and extract conserved differentially expressed gene (DEG) signatures driving muscle atrophy under microgravity.
3. **In-Silico Signature Reversal:** Evaluate compound perturbation libraries to identify small molecules that induce an inverse gene expression profile to the spaceflight degradation signature, computing connectivity scores to prioritize candidate countermeasures.
4. **Interactive Open-Science Visualizer:** Provide a reproducible, web-based dashboard allowing researchers to inspect study concordance, explore targeted pathways, and examine ranked countermeasure candidates alongside their underlying statistical evidence.

---

## 2026 NASA Space Apps Timeline & Guidelines

### Official Timeline

| Date | Official Milestone | What You Must Do |
| --- | --- | --- |
| **August 26, 2026** | **Registration Opens**<br> | Create an account on the global site, join your Local Event (Dhaka), and save your local BASIS portal profile. |
| **September 17, 2026** | **Challenge Summaries & Team Formation Open**<br> | Download the *Team Formation Participant Guide*, create your team page on the global portal, and select your challenge area. Update your BASIS dashboard with the team link. |
| **October 28, 2026** | **Challenge Statements Available**<br> | Review the full challenge requirements, evaluation prompts, and dataset lists published by NASA. |
| **November 2, 2026** | **Space Apps Connect Opens**<br> | Join official chat channels to engage directly with NASA Subject Matter Experts (SMEs) and Local Leads. Read the *Space Apps Connect Guide*. |
| **November 13, 2026** | **Global Offers & Judging Guides Available**<br> | Review partner cloud/API credits, download the *Project Submission & Judging Guide*, and prepare your final submission template. |
| **November 14–15, 2026** | **Hackathon Weekend**<br> | Complete your code, deploy the web dashboard, record your demo video, and submit your project before the deadline. |
| **December 2026** | **Global Nominees & Finalists Announced**<br> | Local judging concludes; top local projects are nominated for NASA Global Judging. |
| **January 2027** | **Global Winners Announced**<br> | NASA and space agency partners announce the Global Award winners across all categories. |

### Local Events (Dhaka / BASIS) Requirements

1. **Maintain Dual Registration:** Ensure your profile is registered on both the **BASIS local portal** (`nsac.basis.org.bd`) and the **NASA global site** under the Dhaka location.
2. **Attend Local Briefings:** Check emails from BASIS (`bsf@basis.org.bd`) for any local bootcamps, orientation sessions, or technical guidelines.
3. **Submit Both Dashboards:** During hackathon weekend (Nov 14–15), submit your final repository link, live demo URL, and presentation materials on **both** the NASA global portal and the BASIS local portal.
4. **Local Pitch / Evaluation:** If BASIS hosts a physical or virtual presentation round, present a structured slide deck explaining the problem, your NASA OSDR data pipeline, the prototype, and its real-world impact.

### How to Become a Global Nominee

* **1. Rigorous Use of NASA Open Data:** Clearly cite and display the exact NASA OSDR datasets used (`OSD-21`, `OSD-104`, `OSD-101`). Judges score heavily on direct integration with official space agency data.
* **2. Working Prototype (Not Just Slides):** Provide a live, clickable deployment (e.g., Next.js visualizer on Vercel) alongside your open-source GitHub repository.
* **3. Scientific Defensibility:** Frame your results accurately as a computational discovery/hypothesis-ranking engine. Avoiding inflated clinical claims demonstrates technical maturity.
* **4. Concise 30-Second Global Video:** Craft a focused, fast-paced 30-second video demo clearly communicating:
  * The core problem (microgravity-induced muscle atrophy & terrestrial sarcopenia).
  * The solution (AstroLongevity transcriptomic inversion engine).
  * The data used (NASA OSDR / GeneLab).
  * The real-world impact.
* **5. Complete Submission Package:** Fully populate all fields on your NASA Space Apps project page (abstract, data sources, code links, live demo, and presentation deck) before the submission cutoff.
