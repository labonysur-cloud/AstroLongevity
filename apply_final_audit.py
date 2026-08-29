import json
import os
import re

nb_path = 'notebooks/AstroLongevity_Data_Pipeline.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

def replace_in_cell(cell, old, new):
    if old in "".join(cell['source']):
        src = "".join(cell['source'])
        src = src.replace(old, new)
        cell['source'] = [line + '\n' for line in src.split('\n')[:-1]]

for cell in nb['cells']:
    src_str = "".join(cell['source'])
    
    if cell['cell_type'] == 'markdown':
        replace_in_cell(cell, "Three QC gates", "QC validation")
        replace_in_cell(cell, "three QC gates", "QC validation")
        replace_in_cell(cell, "Our pipeline performs differential expression", "Our pipeline consumes NASA OSDR differential-expression outputs and performs cross-study concordance analysis")
        replace_in_cell(cell, "saves every output to Google Drive", "exports pipeline outputs to the project's `public/data` directory")
        replace_in_cell(cell, "then copied to Google Drive at the end of this cell.", "")
        
    elif cell['cell_type'] == 'code':
        # Issue 12/22: Cache Checksum / Parser Error
        if 'def download_study_file' in src_str:
            new_download = """
        if os.path.exists(save_path):
            try:
                # Verify file integrity by attempting to read it
                pd.read_csv(save_path, nrows=5)
                logger.info(f"Using valid cached file: {target_file}")
            except Exception:
                logger.warning(f"Corrupted cache detected for {target_file}. Deleting and redownloading.")
                os.remove(save_path)
        
        if not os.path.exists(save_path):
            logger.info(f"Downloading from NASA OSDR: {target_file}")
            with requests.get(target_url, stream=True, timeout=120) as r:
"""
            replace_in_cell(cell, """
        if os.path.exists(save_path):
            logger.info(f"Using cached file: {target_file}")
        else:
            logger.info(f"Downloading from NASA OSDR: {target_file}")

        # Download if not already downloaded
        if not os.path.exists(save_path):
            with requests.get(target_url, stream=True, timeout=120) as r:
""", new_download)

        # Issue 6 & 7: NaNs and duplicate SYMBOLs
        if 'def validate_dataframe' in src_str:
            # Exclude stat columns from strict NA checking
            na_check = """
    # General NA checking for non-statistical numeric columns
    stat_cols = [c for c in df.columns if any(k in c.lower() for k in ["stat", "p.value", "pvalue", "log2fc", "lrt"])]
    strict_numeric = [c for c in numeric_cols if c not in stat_cols]
    if df[strict_numeric].isna().any().any():
        raise ValueError(f"QC FAIL [{dataset_name}]: Missing values in core numeric matrix.")
"""
            if "General NA checking" not in src_str:
                replace_in_cell(cell, 'if np.isinf(df[numeric_cols]).any().any():', na_check + '    if np.isinf(df[numeric_cols]).any().any():')
        
        # Issue 8: Benchmark wording
        replace_in_cell(cell, 'Three QC gates (OSD-104)', 'QC validation (OSD-104)')
        replace_in_cell(cell, 'All measurements are from the live run on this Colab instance', 'All measurements are from the live local execution')
        
        # Issue 28: PCA low-expression filtering & Issue 27: Wording
        if 'log_matrix = np.log2(expr_matrix + 1)' in src_str:
            pca_fix = """
# Filter low-expression genes to remove noise before PCA
expr_matrix = expr_matrix[expr_matrix.mean(axis=1) > 10]

# Apply log2(x + 1) transformation to reduce count-scale skew before PCA
log_matrix = np.log2(expr_matrix + 1)
"""
            replace_in_cell(cell, '# Apply log2(x + 1) transform for variance stabilization\nlog_matrix = np.log2(expr_matrix + 1)', pca_fix.strip())
            
        # Issue 15, 16, 17, 26: SYMBOL_STD, Merge, Tail(50)
        if 'concordant = pd.merge(df101_sig, df104_sig, on="SYMBOL"' in src_str:
            merge_fix = """
    # Standardize symbols to prevent case-mismatch dropping
    df101_sig["SYMBOL_STD"] = df101_sig["SYMBOL"].str.upper().str.strip()
    df104_sig["SYMBOL_STD"] = df104_sig["SYMBOL"].str.upper().str.strip()
    
    # Assert uniqueness before merge
    assert df101_sig["SYMBOL_STD"].is_unique, "Duplicate SYMBOL_STD in OSD-101"
    assert df104_sig["SYMBOL_STD"].is_unique, "Duplicate SYMBOL_STD in OSD-104"
    
    concordant = pd.merge(df101_sig, df104_sig, on="SYMBOL_STD", suffixes=("_101", "_104"))
    concordant["SYMBOL"] = concordant["SYMBOL_101"] # Retain original case for display
    concordant["Average_Log2fc"] = (concordant["Log2fc_101"] + concordant["Log2fc_104"]) / 2
"""
            # Replace the old merge logic block
            # I will just write a regex to replace the specific chunk
            pass
            
        # Instead of complex regex, let's just do targeted string replacements for Cell 7
        replace_in_cell(cell, 'df101_sig = df101.dropna(subset=["SYMBOL", "Adj.p.value", "Log2fc"])', 'df101_sig = df101.dropna(subset=["SYMBOL", "Adj.p.value", "Log2fc"]).copy()\n    df101_sig["SYMBOL_STD"] = df101_sig["SYMBOL"].str.upper().str.strip()\n    df101_sig = df101_sig.drop_duplicates(subset=["SYMBOL_STD"])')
        replace_in_cell(cell, 'df104_sig = df104.dropna(subset=["SYMBOL", "Adj.p.value", "Log2fc"])', 'df104_sig = df104.dropna(subset=["SYMBOL", "Adj.p.value", "Log2fc"]).copy()\n    df104_sig["SYMBOL_STD"] = df104_sig["SYMBOL"].str.upper().str.strip()\n    df104_sig = df104_sig.drop_duplicates(subset=["SYMBOL_STD"])')
        replace_in_cell(cell, 'set101 = set(sig101["SYMBOL"].str.upper())', 'set101 = set(sig101["SYMBOL_STD"])')
        replace_in_cell(cell, 'set104 = set(sig104["SYMBOL"].str.upper())', 'set104 = set(sig104["SYMBOL_STD"])')
        
        replace_in_cell(cell, 'concordant = pd.merge(df101_sig, df104_sig, on="SYMBOL", suffixes=("_101", "_104"))', 'concordant = pd.merge(df101_sig, df104_sig, on="SYMBOL_STD", suffixes=("_101", "_104"))\n    concordant["SYMBOL"] = concordant["SYMBOL_101"]')
        replace_in_cell(cell, 'dn_sig = final_sig[final_sig["Average_Log2fc"] < 0].tail(50)', 'dn_sig = final_sig[final_sig["Average_Log2fc"] < 0].sort_values("Average_Log2fc", ascending=True).head(50)')
        
        # Issue 4, 5, 18, 19, 25: Orthology mapping drops, overlaps, PubChem validation
        if 'def map_mouse_to_human' in src_str:
            mapping_logic = """
                    print(f"  Input {label} mouse genes: {len(mouse_symbols)}")
                    print(f"  Strict 1:1 human orthologs retained: {len(df_map)}")
                    return df_map['Human_Symbol'].tolist()
"""
            replace_in_cell(cell, 'print(f"  {len(mouse_symbols)} input {label} mouse genes -> {len(df_map)} strict 1:1 human orthologs")\n                    return df_map[\'Human_Symbol\'].tolist()', mapping_logic.strip() + '\n')
            
            overlap_check = """
# Validate orthogonality
overlap = set(up_genes_human) & set(dn_genes_human)
if overlap:
    raise ValueError(f"Biological ambiguity: Human genes {overlap} appear in both UP and DOWN signatures.")

if len(up_genes_human) < 10 or len(dn_genes_human) < 10:
    raise RuntimeError("Insufficient orthologs mapped to perform a robust L1000CDS2 gene-set search.")
"""
            replace_in_cell(cell, 'url = "https://maayanlab.cloud/L1000CDS2/query"', overlap_check + '\nurl = "https://maayanlab.cloud/L1000CDS2/query"')
            
            pubchem_fix = """
    pubchem = entry.get("pubchem_id", "")
    if str(pubchem) == "0" or not pubchem:
        pubchem = "Unknown"
        
    candidates.append({
"""
            replace_in_cell(cell, 'candidates.append({', pubchem_fix.strip() + '\n')

        # Issue 12 & 23: Metadata export and 141 gene export
        if 'final_sig.head(100).to_json' in src_str:
            replace_in_cell(cell, 'final_sig.head(100).to_json', 'final_sig.to_json')
            
            metadata_export = """
    # Save Pipeline Metadata
    import sys
    import platform
    import pkg_resources
    
    metadata = {
        "environment": "Local Benchmark",
        "platform": platform.platform(),
        "python_version": sys.version,
        "packages": {
            "pandas": pkg_resources.get_distribution("pandas").version,
            "numpy": pkg_resources.get_distribution("numpy").version,
            "scikit-learn": pkg_resources.get_distribution("scikit-learn").version,
            "requests": pkg_resources.get_distribution("requests").version
        },
        "l1000_db_version": "latest (pinned to execution timestamp)",
    }
    with open(os.path.join(OUTPUT_DIR, "pipeline_metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)
"""
            replace_in_cell(cell, 'print(f"\\nJSON data exported successfully', metadata_export.strip() + '\n    print(f"\\nJSON data exported successfully')

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2)
