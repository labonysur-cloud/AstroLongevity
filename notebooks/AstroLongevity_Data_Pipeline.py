#!/usr/bin/env python
# coding: utf-8

# # AstroLongevity Data Pipeline
# 
# **NASA Space Apps Challenge 2026 | Team Astrophel | Labony Sur, Aupurba Sarker**
# 
# This notebook retrieves real differential expression data from the NASA Open Science Data Repository (OSDR), validates it through three fail-closed quality control gates, performs PCA, cross-study concordance analysis, and saves every output to Google Drive.
# 
# Primary transcriptomic inputs are retrieved from NASA OSDR. All downstream statistics, signatures, visualizations, mappings, and rankings are computationally derived from those inputs or retrieved from external APIs.

# In[1]:


# Cell 1: Environment setup and Google Drive mount

import requests
import pandas as pd
import numpy as np
import json
import shutil
import time
import logging
import sys
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from sklearn.decomposition import PCA
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


LOCAL_CACHE = "nasa_data"
OUTPUT_DIR = "../public/data"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOCAL_CACHE, exist_ok=True)



# In[2]:


# Cell 2: Core pipeline functions
# get_study_files     - fetches the file manifest from NASA OSDR REST API
# download_study_file - selects the correct file by dataset type and streams it to disk
# validate_dataframe  - robust structural and transcriptomic data integrity gates

import requests
import pandas as pd
import numpy as np
import json
import os
import shutil
import time
import logging
import sys
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def get_study_files(osd_id):
    numeric_id = osd_id.split("-")[-1]
    api_url = f"https://osdr.nasa.gov/osdr/data/osd/files/{numeric_id}"
    response = requests.get(api_url, timeout=30)
    if response.status_code != 200:
        raise requests.exceptions.HTTPError(
            f"NASA OSDR API returned HTTP {response.status_code} for {osd_id}."
        )
    resp_data = response.json()
    try:
        file_list = resp_data["studies"][osd_id]["study_files"]
    except KeyError:
        raise ValueError(f"Unexpected JSON structure returned for {osd_id}.")
    if not file_list:
        raise ValueError(f"No files found in the manifest for {osd_id}.")
    return file_list

def download_study_file(osd_id, file_list):
    if osd_id == "OSD-21":
        keywords = ["normalized_intensities"]
    else:
        # Download both to get counts for PCA and stats for concordance
        keywords = ["normalized_counts", "differential_expression"]

    dfs = []
    for keyword in keywords:
        target_file = None
        target_url = None

        for file_info in file_list:
            fname = file_info.get("file_name", "").lower()
            # prefer rRNArm
            if fname.endswith(".csv") and keyword.lower() in fname and "rrnarm" in fname and "unnormalized" not in fname:
                target_file = file_info.get("file_name")
                remote = file_info.get("remote_url", "")
                if not remote.startswith("http"):
                    remote = "https://osdr.nasa.gov" + remote
                target_url = remote
                break

        if target_file is None:
            for file_info in file_list:
                fname = file_info.get("file_name", "").lower()
                if fname.endswith(".csv") and keyword.lower() in fname and "unnormalized" not in fname:
                    target_file = file_info.get("file_name")
                    remote = file_info.get("remote_url", "")
                    if not remote.startswith("http"):
                        remote = "https://osdr.nasa.gov" + remote
                    target_url = remote
                    break

        if target_file is None:
            raise FileNotFoundError(f"Could not find a CSV file containing '{keyword}'.")

        save_path = os.path.join(LOCAL_CACHE, f"{osd_id}_{target_file}")
        logger.info(f"Downloading: {target_file}  ->  {save_path}")

        # Download if not already downloaded
        if not os.path.exists(save_path):
            with requests.get(target_url, stream=True, timeout=120) as r:
                if r.status_code != 200:
                    raise requests.exceptions.HTTPError(f"HTTP {r.status_code}.")
                with open(save_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

        sep = "\t" if save_path.lower().endswith((".tsv", ".txt")) else ","
        df = pd.read_csv(save_path, sep=sep, low_memory=False)
        dfs.append(df)

    if len(dfs) == 1:
        return dfs[0], ""
    else:
        # Merge normalized counts and differential expression
        df_counts = dfs[0]
        df_de = dfs[1]
        df_merged = pd.merge(df_counts, df_de, left_on=df_counts.columns[0], right_on="ENSEMBL", suffixes=("_count", "_de"))
        return df_merged, ""

def validate_dataframe(df, dataset_name):
    # 1. Row count check
    if len(df) <= 1000:
        raise ValueError(f"QC FAIL [{dataset_name}]: Insufficient row count ({len(df)} rows). Expected > 1000.")

    # 2. Null ID check
    first_col = df.columns[0]
    if df[first_col].isna().any():
        raise ValueError(f"QC FAIL [{dataset_name}]: Null values detected in primary identifier column '{first_col}'.")

    # 3. Duplicate ID check
    if df[first_col].duplicated().any():
        dup_count = df[first_col].duplicated().sum()
        logger.warning(f"QC WARNING [{dataset_name}]: {dup_count} duplicate identifiers detected. These will be handled gracefully by the pipeline (e.g. grouped by mean).")

    # 4. Numeric column check
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) == 0:
        raise ValueError(f"QC FAIL [{dataset_name}]: No numeric columns found for expression values.")

    # 5. NA/Inf checks in expression matrix
    if df[numeric_cols].isna().any().any():
        raise ValueError(f"QC FAIL [{dataset_name}]: Missing (NA) values detected in numeric expression matrix.")
    if np.isinf(df[numeric_cols]).any().any():
        raise ValueError(f"QC FAIL [{dataset_name}]: Infinite (Inf) values detected in numeric expression matrix.")

    # 6. Negative count check (only for raw/normalized count columns)
    count_cols = [c for c in numeric_cols if "count" in c.lower()]
    if count_cols:
        if (df[count_cols] < 0).any().any():
            raise ValueError(f"QC FAIL [{dataset_name}]: Negative values detected in expression count columns.")

    logger.info(f"QC COMPLETE [{dataset_name}]: Structural and transcriptomic data integrity verified.")


# In[3]:


# Cell 3: Download all three NASA OSDR datasets and run quality control
#
# OSD-21  : microarray, normalized intensities, 230,000+ probes
# OSD-101 : RNA-Seq normalized counts, 23,257 genes (Rodent Research 4)
# OSD-104 : RNA-Seq normalized counts, 22,437 genes (Rodent Research 1)
#
# All files are saved to LOCAL_CACHE on the Colab instance disk first,
# then copied to Google Drive at the end of this cell.

DATASETS = ["OSD-21", "OSD-101", "OSD-104"]
dataframes = {}
download_times = {}

for study_id in DATASETS:
    logger.info(f"=== Starting {study_id} ===")
    t_start = time.time()
    try:
        file_list = get_study_files(study_id)
        logger.info(f"Manifest retrieved: {len(file_list)} total files listed for {study_id}.")

        df, local_path = download_study_file(study_id, file_list)

        # OSD-21 post-load cleanup:
        # The microarray file contains many annotation columns (SYMBOL, GENENAME, etc.).
        # We keep only rows where SYMBOL is not null and retain all numeric intensity columns.
        if study_id == "OSD-21":
            if "SYMBOL" not in df.columns:
                raise ValueError("OSD-21: Expected 'SYMBOL' column not found after load.")
            before = len(df)
            df = df.dropna(subset=["SYMBOL"]).copy()
            after = len(df)
            logger.info(f"OSD-21 cleanup: Removed {before - after} probes with null SYMBOL. {after} probes retained.")
            # OSD-21 has massive duplicate probes per SYMBOL. We must group them.
            df = df.groupby("SYMBOL").mean(numeric_only=True).reset_index()
            logger.info(f"OSD-21 cleanup: Grouped duplicate probes by SYMBOL mean. {len(df)} unique genes retained.")

        validate_dataframe(df, study_id)
        dataframes[study_id] = df

        elapsed = time.time() - t_start
        download_times[study_id] = round(elapsed, 1)
        logger.info(f"=== {study_id} complete in {elapsed:.1f}s ===")

    except Exception as err:
        logger.error(f"FAILED for {study_id}: {err}")

# Copy everything from local cache to Google Drive

# Summary
print("\nDownload summary:")
for sid in DATASETS:
    if sid in dataframes:
        df = dataframes[sid]
        size_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
        print(f"  {sid}: {df.shape[0]} rows x {df.shape[1]} cols  |  {size_mb:.1f} MB in memory  |  {download_times.get(sid, '?')}s")
    else:
        print(f"  {sid}: FAILED - see error above")


# In[4]:


# Cell 4: Data Ingestion Verification
#
# Prove successful data ingestion by displaying standard Pandas data summaries.

print("DATA INGESTION VERIFICATION")
print("-" * 60)

# --- OSD-104 ---
print("\n[OSD-104] Data Overview")
df104 = dataframes.get("OSD-104")
if df104 is not None:
    print(f"  Gene count    : {len(df104)}")
    display(df104.head())
    display(df104.describe())
else:
    print("  Status        : FILE NOT FOUND IN MEMORY")

print("\n" + "-" * 60)


# In[5]:


# Cell 5: Computational performance benchmark
#
# Measures actual wall-clock time and peak memory usage for each pipeline stage.
# All measurements are from the live run on this Colab instance, not estimated.

import tracemalloc

print("COMPUTATIONAL BENCHMARK")
print("-" * 60)
print(f"Runtime: Local Benchmark")
print()

bench_results = []

# --- Benchmark: API manifest fetch (OSD-104 as representative) ---
tracemalloc.start()
t0 = time.time()
_ = get_study_files("OSD-104")
t_api = time.time() - t0
_, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
bench_results.append({"Stage": "API manifest fetch (OSD-104)", "Time_s": round(t_api, 2), "Peak_RAM_MB": round(peak / 1e6, 1)})
print(f"  API fetch        : {t_api:.2f}s")

# --- Benchmark: CSV parse from disk (OSD-104) ---
osd104_local = os.path.join(LOCAL_CACHE, "OSD-104_GLDS-104_rna_seq_Normalized_Counts_rRNArm_GLbulkRNAseq.csv")
if os.path.exists(osd104_local):
    tracemalloc.start()
    t0 = time.time()
    df_bench = pd.read_csv(osd104_local, low_memory=False)
    t_parse = time.time() - t0
    _, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
    bench_results.append({"Stage": "CSV parse into DataFrame (OSD-104)", "Time_s": round(t_parse, 2), "Peak_RAM_MB": round(peak / 1e6, 1)})
    print(f"  CSV parse        : {t_parse:.2f}s")

    # --- Benchmark: QC gates ---
    tracemalloc.start()
    t0 = time.time()
    validate_dataframe(df_bench, "OSD-104")
    t_qc = time.time() - t0
    _, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
    bench_results.append({"Stage": "Three QC gates (OSD-104)", "Time_s": round(t_qc, 3), "Peak_RAM_MB": round(peak / 1e6, 1)})
    print(f"  QC gates         : {t_qc:.3f}s")

    # --- Benchmark: Log2 transform + PCA ---
    sample_cols = [c for c in df_bench.columns if df_bench[c].dtype in [np.float64, np.int64]
                   and c not in ["Stat", "P.value", "Adj.p.value", "Log2fc", "LRT.p.value", "LRT.adj.p.value"]
                   and ("FLT" in c or "GC" in c or "Mmus" in c or "GSM" in c)]
    if sample_cols:
        tracemalloc.start()
        t0 = time.time()
        log_data = np.log2(df_bench.set_index(df_bench.columns[0])[sample_cols] + 1)
        pca_tmp = PCA(n_components=2)
        pca_tmp.fit_transform(log_data.T)
        t_pca = time.time() - t0
        _, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
        bench_results.append({"Stage": "Log2 transform + PCA (OSD-104)", "Time_s": round(t_pca, 2), "Peak_RAM_MB": round(peak / 1e6, 1)})
        print(f"  Log2 + PCA       : {t_pca:.2f}s")
    del df_bench

df_bench_results = pd.DataFrame(bench_results)
print()
print(df_bench_results.to_string(index=False))
print()
total_t = df_bench_results["Time_s"].sum()
print(f"OSD-104 post-download processing benchmark: {total_t:.2f}s")

bench_path = os.path.join(OUTPUT_DIR, "Benchmark_Results.csv")
df_bench_results.to_csv(bench_path, index=False)


# In[6]:


# Cell 6: PCA of OSD-104 spaceflight vs ground control transcriptomics
#
# Uses the normalized expression columns from the NASA files.
# We apply a log2(x + 1) pseudocount transformation for variance stabilization before PCA.

if "OSD-104" not in dataframes:
    raise RuntimeError("OSD-104 data not loaded. Run Cell 3 first.")

df104 = dataframes["OSD-104"]

stat_keywords = {
    "Stat", "P.value", "Adj.p.value", "Log2fc", "LRT", "Average_Log2fc",
    "Group.Mean", "Group.Stdev", "ENSEMBL", "SYMBOL", "GENENAME", "All.mean", "All.stdev", "Unnamed"
}

sample_cols = []
for c in df104.columns:
    is_stat = any(kw.lower() in c.lower() for kw in stat_keywords)
    is_numeric = pd.api.types.is_numeric_dtype(df104[c])
    if is_numeric and not is_stat and ("FLT" in c.upper() or "GC" in c.upper()) and "_de" not in c.lower():
        sample_cols.append(c)

if len(sample_cols) < 2:
    raise ValueError(f"Cannot run PCA: fewer than 2 expression columns found.\nAll columns: {list(df104.columns)}")

logger.info(f"Sample columns selected for PCA: {sample_cols}")

gene_col = "SYMBOL" if "SYMBOL" in df104.columns else df104.columns[0]
expr_matrix = df104.set_index(gene_col)[sample_cols].dropna()

# Apply log2(x + 1) transform for variance stabilization
log_matrix = np.log2(expr_matrix + 1)
log_matrix.index = log_matrix.index.astype(str)

pca = PCA(n_components=2)
pcs = pca.fit_transform(log_matrix.T.values)

evr1 = pca.explained_variance_ratio_[0] * 100
evr2 = pca.explained_variance_ratio_[1] * 100
logger.info(f"PCA complete: PC1={evr1:.1f}%, PC2={evr2:.1f}%")

conditions = []
for col in sample_cols:
    if "FLT" in col.upper():
        conditions.append("Spaceflight (FLT)")
    elif "GC" in col.upper():
        conditions.append("Ground Control (GC)")
    else:
        conditions.append("Unknown")

pca_df = pd.DataFrame({
    "PC1": pcs[:, 0],
    "PC2": pcs[:, 1],
    "Sample": sample_cols,
    "Condition": conditions
})

print(f"\nPC1 explained variance : {evr1:.1f}%")
print(f"PC2 explained variance : {evr2:.1f}%")
print(f"Total (PC1+PC2)        : {evr1+evr2:.1f}%")
print(f"Samples analyzed       : {len(pca_df)}")
print(pca_df.to_string(index=False))

# Plot PCA
plt.figure(figsize=(8, 6))
sns.scatterplot(
    data=pca_df,
    x="PC1", y="PC2",
    hue="Condition",
    palette={"Spaceflight (FLT)": "red", "Ground Control (GC)": "blue"},
    s=100, edgecolor="black", alpha=0.8
)
plt.title("PCA of OSD-104 Transcriptomics (Log2 Normalized Counts)")
plt.xlabel(f"PC1 ({evr1:.1f}%)")
plt.ylabel(f"PC2 ({evr2:.1f}%)")
plt.grid(True, linestyle="--", alpha=0.5)
plt.legend(title="Condition")
plt.tight_layout()
pca_plot_path = os.path.join(OUTPUT_DIR, "PCA_OSD-104.png")
plt.savefig(pca_plot_path, dpi=300)
plt.show()
logger.info(f"PCA plot saved: {pca_plot_path}")



# In[7]:


# Cell 7: Cross-study concordance analysis
#
# Identifies genes that are significantly and directionally concordantly dysregulated
# across OSD-101 and OSD-104 (both RNA-Seq DE datasets).
#
# OSD-21 is a microarray dataset and uses a different statistical framework
# (RMA normalized intensities, not DESeq2 p-values). Including it in intersection
# requires a separate limma differential expression step which is beyond the
# scope of this pipeline. OSD-21 is retained in the dataframes dictionary
# for downstream use.
#
# The concordance criterion:
#   1. Gene must be significant (adj. p < 0.05) in both OSD-101 and OSD-104
#   2. Log2FC must have the same sign in both datasets (directional consistency)
# Reference: Equation (2) in AstroLongevity_Research_Paper.tex

if "OSD-101" not in dataframes or "OSD-104" not in dataframes:
    raise RuntimeError("OSD-101 or OSD-104 not loaded. Run Cell 3 first.")

df101 = dataframes["OSD-101"].copy()
df104 = dataframes["OSD-104"].copy()

# Identify the adjusted p-value and log2fc column names from the NASA file header.
# NASA GLbulkRNAseq pipeline uses a consistent naming pattern.
def find_col(df, patterns):
    """Return the column name that contains all patterns, preferring Space Flight as numerator."""
    candidates = [col for col in df.columns if all(p.lower() in col.lower() for p in patterns)]
    for col in candidates:
        # Check if Space Flight is the numerator (comes before Ground Control)
        if "Space Flight" in col and "Ground Control" in col:
            if col.lower().find("space flight") < col.lower().find("ground control"):
                return col
    return candidates[0] if candidates else None

# OSD-101 columns
pval_col_101 = find_col(df101, ["Adj.p.value", "Space Flight", "Ground Control"])
log2_col_101 = find_col(df101, ["Log2fc", "Space Flight", "Ground Control"])
print(f"OSD-101 adj p-value column : {pval_col_101}")
print(f"OSD-101 log2fc column      : {log2_col_101}")

# OSD-104 columns
pval_col_104 = find_col(df104, ["Adj.p.value", "Space Flight", "Ground Control"])
log2_col_104 = find_col(df104, ["Log2fc", "Space Flight", "Ground Control"])
print(f"OSD-104 adj p-value column : {pval_col_104}")
print(f"OSD-104 log2fc column      : {log2_col_104}")

if None in [pval_col_101, log2_col_101, pval_col_104, log2_col_104]:
    raise ValueError("Required columns not found. Check NASA file column names above.")

# Drop rows with null SYMBOL or null p-value or null log2fc
df101 = df101.dropna(subset=["SYMBOL", pval_col_101, log2_col_101]).copy()
df104 = df104.dropna(subset=["SYMBOL", pval_col_104, log2_col_104]).copy()

# Significance filter (adj. p < 0.05)
P_THRESH = 0.05
sig101 = df101[df101[pval_col_101] < P_THRESH][["SYMBOL", log2_col_101, pval_col_101]].copy()
sig104 = df104[df104[pval_col_104] < P_THRESH][["SYMBOL", log2_col_104, pval_col_104]].copy()

print(f"\nSignificant genes (adj.p < {P_THRESH}):")
print(f"  OSD-101 : {len(sig101)}")
print(f"  OSD-104 : {len(sig104)}")

# Jaccard similarity of significant gene sets
set101 = set(sig101["SYMBOL"].str.upper())
set104 = set(sig104["SYMBOL"].str.upper())
jaccard = len(set101 & set104) / len(set101 | set104) if (set101 | set104) else 0
print(f"  Jaccard similarity : {jaccard:.4f}")

# Inner join on SYMBOL to get intersection
merged = pd.merge(
    sig101.rename(columns={log2_col_101: "Log2fc_101", pval_col_101: "Adj.p.value_101"}),
    sig104.rename(columns={log2_col_104: "Log2fc_104", pval_col_104: "Adj.p.value_104"}),
    on="SYMBOL"
)
print(f"  Intersection size  : {len(merged)}")

# Directional concordance: log2fc must have the same sign in both studies
concordant = merged[
    (merged["Log2fc_101"] * merged["Log2fc_104"]) > 0
].copy()
print(f"  Directionally concordant : {len(concordant)}")

# Average log2fc across the two studies for ranking
concordant["Average_Log2fc"] = (concordant["Log2fc_101"] + concordant["Log2fc_104"]) / 2

# Final signature table
final_sig = concordant[
    ["SYMBOL", "Average_Log2fc", "Adj.p.value_101", "Adj.p.value_104", "Log2fc_101", "Log2fc_104"]
].sort_values(by="Average_Log2fc", ascending=False).reset_index(drop=True)

print(f"\nTop 10 upregulated concordant genes:")
print(final_sig.head(10).to_string(index=False))
print(f"\nTop 10 downregulated concordant genes:")
print(final_sig.tail(10).to_string(index=False))

# Save
sig_path = os.path.join(OUTPUT_DIR, "Concordant_Atrophy_Signature.csv")
final_sig.to_csv(sig_path, index=False)
logger.info(f"Concordant atrophy signature saved: {sig_path}")
print(f"\nSignature saved to Drive: {sig_path}")


# In[8]:


# Cell 8: Computational Countermeasure Prioritization via LINCS L1000
#
# Maps the murine Spaceflight Concordant Atrophy signature to human orthologs.
# Queries the Ma'ayan Lab L1000CDS2 API to identify small molecules that
# directionally reverse the spaceflight transcriptomic signature.

import requests
import pandas as pd
import os

if 'final_sig' not in locals():
    raise RuntimeError("Signature not found. Run Cell 7 first.")

print("DRUG DISCOVERY: LINCS L1000 API INTEGRATION")
print("-" * 60)

# 1. Extract Top 50 Upregulated and Downregulated genes in Spaceflight
up_sig = final_sig[final_sig["Average_Log2fc"] > 0].head(50)
dn_sig = final_sig[final_sig["Average_Log2fc"] < 0].tail(50)  # tail because sorted descending

# 2. Convert to Human Orthologs
# We map murine symbols to human orthologs via the MyGene.info REST API.
# Genes without an explicit 1:1 homologene mapping fall back to uppercase heuristic.

def map_mouse_to_human(mouse_symbols):
    human_symbols = []
    url = "https://mygene.info/v3/query"
    try:
        # Step A: Get Homologene IDs for mouse symbols
        res = requests.post(url, data={'q': ','.join(mouse_symbols), 'scopes': 'symbol', 'fields': 'homologene', 'species': 'mouse'})
        if res.status_code == 200:
            h_gene_ids = []
            for item in res.json():
                if 'homologene' in item and 'genes' in item['homologene']:
                    # Extract Taxon 9606 (Human) Gene ID
                    for taxon, gene_id in item['homologene']['genes']:
                        if taxon == 9606:
                            h_gene_ids.append(str(gene_id))
                            break
            # Step B: Get Gene Symbols for human gene IDs
            if h_gene_ids:
                res2 = requests.post(url, data={'q': ','.join(h_gene_ids), 'scopes': 'entrezgene', 'fields': 'symbol', 'species': 'human'})
                if res2.status_code == 200:
                    for item in res2.json():
                        if 'symbol' in item:
                            human_symbols.append(item['symbol'])
    except Exception as e:
        print(f"MyGene API mapping failed: {e}")

    # We strictly use only verified 1:1 orthologs. No uppercase fallbacks.
    return list(set(human_symbols))
up_genes_human = map_mouse_to_human(up_sig["SYMBOL"].tolist())
dn_genes_human = map_mouse_to_human(dn_sig["SYMBOL"].tolist())

print(f"Querying L1000CDS2 API with:")
print(f"  {len(up_genes_human)} Upregulated orthologs mapped")
print(f"  {len(dn_genes_human)} Downregulated orthologs")

# 3. Construct API Payload
url = "https://maayanlab.cloud/L1000CDS2/query"
payload = {
    "data": {
        "upGenes": up_genes_human,
        "dnGenes": dn_genes_human
    },
    "config": {
        "aggravate": False,      # False = Reversal (we want countermeasures)
        "searchMethod": "geneSet",
        "share": False,
        "combination": False,
        "db-version": "latest"
    }
}

# 4. Dispatch Request
try:
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    api_data = response.json()
except Exception as e:
    raise RuntimeError(f"L1000CDS2 API Request Failed: {e}")

# 5. Parse Top Candidates
candidates = []
for entry in api_data.get("topMeta", []):
    candidates.append({
        "Drug_Name": entry.get("pert_desc", "Unknown"),
        "Reversal_Score": round(entry.get("score", 0), 4),
        "Cell_Line": entry.get("cell_id", ""),
        "Dose": f"{entry.get('pert_dose', '')} {entry.get('pert_dose_unit', '')}",
        "Time": f"{entry.get('pert_time', '')} {entry.get('pert_time_unit', '')}",
        "PubChem_ID": entry.get("pubchem_id", ""),
        "Perturbagen_ID": entry.get("pert_id", "")
    })

df_drugs = pd.DataFrame(candidates)

# Drop redundant cell line variations of the same drug (keep the highest scoring cell line)
if not df_drugs.empty:
    df_drugs = df_drugs.sort_values("Reversal_Score", ascending=False).drop_duplicates(subset=["Perturbagen_ID"]).reset_index(drop=True)

    print("\nTop 15 Candidate Countermeasures (Signature Reversal):")
    display(df_drugs.head(15))

    # Save results
    drug_path = os.path.join(OUTPUT_DIR, "L1000_Candidate_Drugs.csv")
    df_drugs.to_csv(drug_path, index=False)
    logger.info(f"Drug candidates saved to: {drug_path}")
    print(f"\nSaved candidates to Drive: {drug_path}")
else:
    print("\nNo drugs returned from L1000CDS2 API.")


# In[9]:


# Cell 9: Frontend Data Export
#
# Exports all pipeline outputs as static JSON files to the Next.js `public/data/` 
# directory for lightning-fast frontend dashboard rendering.

import os
import json

print("FRONTEND HAND-OFF")
print("-" * 60)

# Static JSON Export for Next.js Frontend
try:
    if 'pca_df' in locals():
        pca_df.to_json(os.path.join(OUTPUT_DIR, "pca_coordinates.json"), orient="records")
    if 'final_sig' in locals():
        final_sig.head(100).to_json(os.path.join(OUTPUT_DIR, "concordant_signature.json"), orient="records")
    if 'df_bench_results' in locals():
        df_bench_results.to_json(os.path.join(OUTPUT_DIR, "benchmark_stats.json"), orient="records")
    if 'df_drugs' in locals():
        df_drugs.to_json(os.path.join(OUTPUT_DIR, "l1000_drug_candidates.json"), orient="records")

    print(f"\nJSON data exported successfully to: {OUTPUT_DIR}")

except Exception as e:
    print(f"Failed to export JSON: {e}")


