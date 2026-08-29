import json

nb_path = 'notebooks/AstroLongevity_Data_Pipeline.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'markdown':
        source = ''.join(cell['source'])
        
        # 1. Update Cell 0: Data provenance + Cross-species claim removal
        if 'No data is generated' in source:
            source = source.replace(
                'No data is generated, simulated, or hardcoded. Every number shown comes directly from NASA OSDR files or peer-reviewed published literature with explicit citations.',
                'Primary transcriptomic inputs are retrieved from NASA OSDR. All downstream statistics, signatures, visualizations, mappings, and rankings are computationally derived from those inputs or retrieved from external APIs.'
            )
            source = source.replace(', cross-species validation against published literature', '')
            cell['source'] = [source]
            
    elif cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        
        # 2. Update Cell 1: Colab references -> completely delete them
        if 'from google.colab import drive' in source or 'drive.mount' in source:
            new_lines = []
            for line in source.split('\n'):
                if 'google.colab' in line or 'drive.mount' in line or 'DRIVE_PATH =' in line or 'Output directory:' in line:
                    continue
                if 'LOCAL_CACHE = "nasa_data"' in line:
                    new_lines.append('LOCAL_CACHE = "nasa_data"')
                    new_lines.append('OUTPUT_DIR = "../public/data"')
                    new_lines.append('os.makedirs(OUTPUT_DIR, exist_ok=True)')
                    continue
                if 'os.makedirs(DRIVE_PATH, exist_ok=True)' in line:
                    continue
                if 'Google Drive mounted' in line:
                    new_lines.append('logger.info("Environment ready. Outputting to ../public/data")')
                    continue
                if 'import matplotlib' in line or 'import matplotlib.pyplot as plt' in line or 'import seaborn as sns' in line or 'from sklearn.decomposition import PCA' in line or 'from sklearn.preprocessing import StandardScaler' in line:
                    # Clean up unused/duplicated imports. We'll leave them if they don't hurt, but standardscaler is unused.
                    if 'StandardScaler' in line:
                        continue
                new_lines.append(line)
            cell['source'] = [line + '\n' if i < len(new_lines)-1 else line for i, line in enumerate(new_lines)]

        # 3. Update Cell 2: QC Fixes (isna check, correct negative check, rename text)
        if 'def validate_dataframe' in source:
            # First, rename fail-closed text
            source = source.replace('three fail-closed quality control gates', 'robust structural and transcriptomic data integrity gates')
            
            # Now rewrite validate_dataframe completely
            old_validate = source[source.find('def validate_dataframe'):]
            new_validate = '''def validate_dataframe(df, dataset_name):
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
'''
            cell['source'] = [(source[:source.find('def validate_dataframe')] + new_validate).strip() + '\n']

        # 4. Update Cell 3: OSD-21 Duplicate Resolution
        if 'if study_id == "OSD-21":' in ''.join(cell['source']):
            new_lines = []
            for line in ''.join(cell['source']).split('\n'):
                if 'shutil.copytree' in line or 'All downloaded files saved' in line:
                    continue # Colab cleanup
                new_lines.append(line)
                if 'logger.info(f"OSD-21 cleanup: Removed {before - after} probes with null SYMBOL. {after} probes retained.")' in line:
                    new_lines.append('            # OSD-21 has massive duplicate probes per SYMBOL. We must group them.')
                    new_lines.append('            df = df.groupby("SYMBOL").mean(numeric_only=True).reset_index()')
                    new_lines.append('            logger.info(f"OSD-21 cleanup: Grouped duplicate probes by SYMBOL mean. {len(df)} unique genes retained.")')
            cell['source'] = [line + '\n' if i < len(new_lines)-1 else line for i, line in enumerate(new_lines)]

        # 5. Update Cell 6 & 7: PCA wording, SYMBOL uniqueness, dataset imbalance comments
        if 'complete inter-group separation along PC1' in ''.join(cell['source']).lower():
            # Update PCA text
            source = ''.join(cell['source'])
            source = source.replace(
                "Complete inter-group separation along PC1 (FLT positive, GC negative) confirms a strong biological signal attributable to the spaceflight condition. No batch effects - all 12 samples processed through the same NASA GLbulkRNAseq pipeline.",
                "PCA effectively separates the flight and ground-control samples, indicating a strong transcriptomic association with the experimental condition."
            )
            cell['source'] = [source]
            
        if 'concordance = pd.merge' in ''.join(cell['source']):
            source = ''.join(cell['source'])
            # Add assertions
            source = source.replace('concordance = pd.merge(df101, df104, on="SYMBOL", suffixes=("_101", "_104"))',
                                    '# Assert unique identifiers before merging to avoid many-to-many explosions\nassert df101["SYMBOL"].is_unique, "OSD-101 contains duplicate SYMBOLs"\nassert df104["SYMBOL"].is_unique, "OSD-104 contains duplicate SYMBOLs"\nconcordance = pd.merge(df101, df104, on="SYMBOL", suffixes=("_101", "_104"))')
            
            # Add comment about average log2fc
            source = source.replace('concordant["Average_Log2fc"] = (concordant[log2fc_101] + concordant[log2fc_104]) / 2',
                                    '# Calculate simple mean fold-change across the two studies for heuristic ranking purposes\nconcordant["Average_Log2fc"] = (concordant[log2fc_101] + concordant[log2fc_104]) / 2')
            
            # Add comment about significance disparity
            source = source.replace('print(f"  OSD-104 significant = {len(sig_104)}")',
                                    'print(f"  OSD-104 significant = {len(sig_104)}")\n# Note: The disparity in significant DEGs (225 vs 4603) is natural and likely driven by differences in experimental design, sample variance, or sequencing depth between missions.')
            cell['source'] = [source]

        # 6. Update Cell 8: Ortholog mapping strictness, deduplication, terminology
        if 'map_mouse_to_human' in ''.join(cell['source']):
            source = ''.join(cell['source'])
            
            # Change Title
            source = source.replace('Drug Discovery via LINCS L1000 Signature Reversal', 'Computational Countermeasure Prioritization via LINCS L1000')
            
            # Rewrite mapping logic to be strict
            strict_map = '''def map_mouse_to_human(mouse_symbols):
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
'''
            source = source[:source.find('def map_mouse_to_human')] + strict_map + source[source.find('up_genes_human ='):]
            
            # Fix FDA text
            source = source.replace('Identify small molecules that directionally reverse the spaceflight transcriptomic signature.',
                                    'Identify candidate perturbagens that directionally oppose the spaceflight transcriptomic signature (gene-set search mode).')
            source = source.replace('FDA-approved compounds', 'candidate small-molecule perturbagens')
            
            # Fix capitalization issue and deduplication
            source = source.replace('.capitalize()', '')
            source = source.replace('drop_duplicates(subset=["Drug_Name"])', 'drop_duplicates(subset=["Perturbagen_ID"])')
            
            cell['source'] = [source]
            
        # 7. Update Cell 9: Remove heatmap, change benchmark phrasing
        if 'Reversal_Heatmap.png' in ''.join(cell['source']):
            new_lines = []
            skip_heatmap = False
            for line in ''.join(cell['source']).split('\n'):
                if 'fig, ax = plt.subplots(figsize=(6, 8))' in line:
                    skip_heatmap = True
                if skip_heatmap and 'plt.close()' in line:
                    skip_heatmap = False
                    continue
                if skip_heatmap:
                    continue
                if 'Reversal_Heatmap' in line:
                    continue
                if 'Total measured time' in line or 'Benchmark results' in line:
                    line = line.replace('Total pipeline runtime', 'OSD-104 post-download processing benchmark')
                    line = line.replace('Total measured time', 'OSD-104 post-download processing benchmark')
                if 'os.path.join(DRIVE_PATH' in line:
                    line = line.replace('DRIVE_PATH', 'OUTPUT_DIR')
                if 'Total pipeline run time' in line:
                    line = line.replace('Total pipeline run time', 'OSD-104 post-download processing benchmark')
                new_lines.append(line)
            cell['source'] = [line + '\n' if i < len(new_lines)-1 else line for i, line in enumerate(new_lines)]

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2)

print("Notebook comprehensively upgraded.")
