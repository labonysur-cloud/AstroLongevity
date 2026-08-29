# Cell 1: Environment setup and Google Drive mount
\n
\nimport requests
\nimport pandas as pd
\nimport numpy as np
\nimport json
\nimport shutil
\nimport time
\nimport logging
\nimport sys
\nimport matplotlib
\nimport matplotlib.pyplot as plt
\nimport matplotlib.patches as mpatches
\nimport seaborn as sns
\nfrom sklearn.decomposition import PCA
\nimport os
\n
\nlogging.basicConfig(
\n    level=logging.INFO,
\n    format="%(asctime)s - %(levelname)s - %(message)s",
\n    force=True,
\n    handlers=[logging.StreamHandler(sys.stdout)]
\n)
\nlogger = logging.getLogger(__name__)
\n
\n
\nLOCAL_CACHE = "nasa_data"
\nOUTPUT_DIR = "../public/data"
\nos.makedirs(OUTPUT_DIR, exist_ok=True)
\nos.makedirs(LOCAL_CACHE, exist_ok=True)
\n
\n# Cell 2: Core pipeline functions
\n# get_study_files     - fetches the file manifest from NASA OSDR REST API
\n# download_study_file - selects the correct file by dataset type and streams it to disk
\n# validate_dataframe  - robust structural and transcriptomic data integrity gates
\n
\nimport requests
\nimport pandas as pd
\nimport numpy as np
\nimport json
\nimport os
\nimport shutil
\nimport time
\nimport logging
\nimport sys
\nimport matplotlib
\nimport matplotlib.pyplot as plt
\nimport matplotlib.patches as mpatches
\nimport seaborn as sns
\nfrom sklearn.decomposition import PCA
\nfrom sklearn.preprocessing import StandardScaler
\n
\n
\ndef get_study_files(osd_id):
\n    numeric_id = osd_id.split("-")[-1]
\n    api_url = f"https://osdr.nasa.gov/osdr/data/osd/files/{numeric_id}"
\n    response = requests.get(api_url, timeout=30)
\n    if response.status_code != 200:
\n        raise requests.exceptions.HTTPError(
\n            f"NASA OSDR API returned HTTP {response.status_code} for {osd_id}."
\n        )
\n    resp_data = response.json()
\n    try:
\n        file_list = resp_data["studies"][osd_id]["study_files"]
\n    except KeyError:
\n        raise ValueError(f"Unexpected JSON structure returned for {osd_id}.")
\n    if not file_list:
\n        raise ValueError(f"No files found in the manifest for {osd_id}.")
\n    return file_list
\n
\ndef download_study_file(osd_id, file_list):
\n    if osd_id == "OSD-21":
\n        keywords = ["normalized_intensities"]
\n    else:
\n        # Download both to get counts for PCA and stats for concordance
\n        keywords = ["normalized_counts", "differential_expression"]
\n
\n    dfs = []
\n    for keyword in keywords:
\n        target_file = None
\n        target_url = None
\n
\n        for file_info in file_list:
\n            fname = file_info.get("file_name", "").lower()
\n            # prefer rRNArm
\n            if fname.endswith(".csv") and keyword.lower() in fname and "rrnarm" in fname and "unnormalized" not in fname:
\n                target_file = file_info.get("file_name")
\n                remote = file_info.get("remote_url", "")
\n                if not remote.startswith("http"):
\n                    remote = "https://osdr.nasa.gov" + remote
\n                target_url = remote
\n                break
\n
\n        if target_file is None:
\n            for file_info in file_list:
\n                fname = file_info.get("file_name", "").lower()
\n                if fname.endswith(".csv") and keyword.lower() in fname and "unnormalized" not in fname:
\n                    target_file = file_info.get("file_name")
\n                    remote = file_info.get("remote_url", "")
\n                    if not remote.startswith("http"):
\n                        remote = "https://osdr.nasa.gov" + remote
\n                    target_url = remote
\n                    break
\n
\n        if target_file is None:
\n            raise FileNotFoundError(f"Could not find a CSV file containing '{keyword}'.")
\n
\n        save_path = os.path.join(LOCAL_CACHE, f"{osd_id}_{target_file}")
\n        logger.info(f"Downloading: {target_file}  ->  {save_path}")
\n
\n        # Download if not already downloaded
\n        if not os.path.exists(save_path):
\n            with requests.get(target_url, stream=True, timeout=120) as r:
\n                if r.status_code != 200:
\n                    raise requests.exceptions.HTTPError(f"HTTP {r.status_code}.")
\n                with open(save_path, "wb") as f:
\n                    for chunk in r.iter_content(chunk_size=8192):
\n                        f.write(chunk)
\n
\n        sep = "\t" if save_path.lower().endswith((".tsv", ".txt")) else ","
\n        df = pd.read_csv(save_path, sep=sep, low_memory=False)
\n        dfs.append(df)
\n
\n    if len(dfs) == 1:
\n        return dfs[0], ""
\n    else:
\n        # Merge normalized counts and differential expression
\n        df_counts = dfs[0]
\n        df_de = dfs[1]
\n        df_merged = pd.merge(df_counts, df_de, left_on=df_counts.columns[0], right_on="ENSEMBL", suffixes=("_count", "_de"))
\n        return df_merged, ""
\n
\ndef validate_dataframe(df, dataset_name):
\n    # 1. Row count check
\n    if len(df) <= 1000:
\n        raise ValueError(f"QC FAIL [{dataset_name}]: Insufficient row count ({len(df)} rows). Expected > 1000.")
\n
\n    # 2. Null ID check
\n    first_col = df.columns[0]
\n    if df[first_col].isna().any():
\n        raise ValueError(f"QC FAIL [{dataset_name}]: Null values detected in primary identifier column '{first_col}'.")
\n
\n    # 3. Duplicate ID check
\n    if df[first_col].duplicated().any():
\n        dup_count = df[first_col].duplicated().sum()
\n        logger.warning(f"QC WARNING [{dataset_name}]: {dup_count} duplicate identifiers detected. These will be handled gracefully by the pipeline (e.g. grouped by mean).")
\n
\n    # 4. Numeric column check
\n    numeric_cols = df.select_dtypes(include=[np.number]).columns
\n    if len(numeric_cols) == 0:
\n        raise ValueError(f"QC FAIL [{dataset_name}]: No numeric columns found for expression values.")
\n
\n    # 5. NA/Inf checks in expression matrix
\n    if df[numeric_cols].isna().any().any():
\n        raise ValueError(f"QC FAIL [{dataset_name}]: Missing (NA) values detected in numeric expression matrix.")
\n    if np.isinf(df[numeric_cols]).any().any():
\n        raise ValueError(f"QC FAIL [{dataset_name}]: Infinite (Inf) values detected in numeric expression matrix.")
\n        
\n    # 6. Negative count check (only for raw/normalized count columns)
\n    count_cols = [c for c in numeric_cols if "count" in c.lower()]
\n    if count_cols:
\n        if (df[count_cols] < 0).any().any():
\n            raise ValueError(f"QC FAIL [{dataset_name}]: Negative values detected in expression count columns.")
\n
\n    logger.info(f"QC COMPLETE [{dataset_name}]: Structural and transcriptomic data integrity verified.")
\n# Cell 3: Download all three NASA OSDR datasets and run quality control
\n#
\n# OSD-21  : microarray, normalized intensities, 230,000+ probes
\n# OSD-101 : RNA-Seq normalized counts, 23,257 genes (Rodent Research 4)
\n# OSD-104 : RNA-Seq normalized counts, 22,437 genes (Rodent Research 1)
\n#
\n# All files are saved to LOCAL_CACHE on the Colab instance disk first,
\n# then copied to Google Drive at the end of this cell.
\n
\nDATASETS = ["OSD-21", "OSD-101", "OSD-104"]
\ndataframes = {}
\ndownload_times = {}
\n
\nfor study_id in DATASETS:
\n    logger.info(f"=== Starting {study_id} ===")
\n    t_start = time.time()
\n    try:
\n        file_list = get_study_files(study_id)
\n        logger.info(f"Manifest retrieved: {len(file_list)} total files listed for {study_id}.")
\n
\n        df, local_path = download_study_file(study_id, file_list)
\n
\n        # OSD-21 post-load cleanup:
\n        # The microarray file contains many annotation columns (SYMBOL, GENENAME, etc.).
\n        # We keep only rows where SYMBOL is not null and retain all numeric intensity columns.
\n        if study_id == "OSD-21":
\n            if "SYMBOL" not in df.columns:
\n                raise ValueError("OSD-21: Expected 'SYMBOL' column not found after load.")
\n            before = len(df)
\n            df = df.dropna(subset=["SYMBOL"]).copy()
\n            after = len(df)
\n            logger.info(f"OSD-21 cleanup: Removed {before - after} probes with null SYMBOL. {after} probes retained.")
\n            # OSD-21 has massive duplicate probes per SYMBOL. We must group them.
\n            df = df.groupby("SYMBOL").mean(numeric_only=True).reset_index()
\n            logger.info(f"OSD-21 cleanup: Grouped duplicate probes by SYMBOL mean. {len(df)} unique genes retained.")
\n
\n        validate_dataframe(df, study_id)
\n        dataframes[study_id] = df
\n
\n        elapsed = time.time() - t_start
\n        download_times[study_id] = round(elapsed, 1)
\n        logger.info(f"=== {study_id} complete in {elapsed:.1f}s ===")
\n
\n    except Exception as err:
\n        logger.error(f"FAILED for {study_id}: {err}")
\n
\n# Copy everything from local cache to Google Drive
\n
\n# Summary
\nprint("\nDownload summary:")
\nfor sid in DATASETS:
\n    if sid in dataframes:
\n        df = dataframes[sid]
\n        size_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
\n        print(f"  {sid}: {df.shape[0]} rows x {df.shape[1]} cols  |  {size_mb:.1f} MB in memory  |  {download_times.get(sid, '?')}s")
\n    else:
\n        print(f"  {sid}: FAILED - see error above")\n# Cell 4: Data Ingestion Verification
\n#
\n# Prove successful data ingestion by displaying standard Pandas data summaries.
\n
\nprint("DATA INGESTION VERIFICATION")
\nprint("-" * 60)
\n
\n# --- OSD-104 ---
\nprint("\n[OSD-104] Data Overview")
\ndf104 = dataframes.get("OSD-104")
\nif df104 is not None:
\n    print(f"  Gene count    : {len(df104)}")
\n    display(df104.head())
\n    display(df104.describe())
\nelse:
\n    print("  Status        : FILE NOT FOUND IN MEMORY")
\n
\nprint("\n" + "-" * 60)
