import json

with open('notebooks/AstroLongevity_Data_Pipeline.ipynb', 'r', encoding='utf-8') as f:
    d = json.load(f)

# Fix Cell 2: download_study_file keyword
cell2 = d['cells'][2]
source2 = cell2['source']
for i, line in enumerate(source2):
    if 'keyword = "differential_expression"' in line:
        source2[i] = '        keyword = "normalized_counts"\n'
    if 'look for' in line and 'differential_expression' in line:
        source2[i] = line.replace('differential_expression', 'normalized_counts')

# Fix Cell 3: download
cell3 = d['cells'][3]
source3 = cell3['source']
for i, line in enumerate(source3):
    if 'differential expression' in line:
        source3[i] = line.replace('differential expression', 'normalized counts')
cell3['outputs'] = []

# Fix Cell 4: Authenticity
cell4 = d['cells'][4]
source4 = [
    "# Cell 4: Data Ingestion Verification\n",
    "#\n",
    "# Prove successful data ingestion by displaying standard Pandas data summaries.\n",
    "\n",
    "print(\"DATA INGESTION VERIFICATION\")\n",
    "print(\"-\" * 60)\n",
    "\n",
    "# --- OSD-104 ---\n",
    "print(\"\\n[OSD-104] Data Overview\")\n",
    "df104 = dataframes.get(\"OSD-104\")\n",
    "if df104 is not None:\n",
    "    print(f\"  Gene count    : {len(df104)}\")\n",
    "    display(df104.head())\n",
    "    display(df104.describe())\n",
    "else:\n",
    "    print(\"  Status        : FILE NOT FOUND IN MEMORY\")\n",
    "\n",
    "print(\"\\n\" + \"-\" * 60)\n",
    "print(\"Ingestion check complete.\")"
]
cell4['source'] = source4
cell4['outputs'] = []

# Fix Cell 5: Benchmark string hardcoded
cell5 = d['cells'][5]
source5 = cell5['source']
for i, line in enumerate(source5):
    if 'differential_expression' in line:
        source5[i] = line.replace('differential_expression', 'normalized_counts')
cell5['outputs'] = []

# Fix Cell 6 (PCA): removing log2 transform
cell6 = d['cells'][6]
source6 = cell6['source']
for i, line in enumerate(source6):
    if 'log_matrix = np.log2(expr_matrix + 1)' in line:
        source6[i] = 'log_matrix = expr_matrix\n'
    if 'Log2 pseudocount transformation' in line:
        source6[i] = '# Using normalized counts directly\n'
cell6['outputs'] = []

# Find and remove cross-species cell and final summary
cells_to_keep = []
for cell in d['cells']:
    keep = True
    if 'id' in cell:
        if cell['id'] == 'cell-08-crossspecies':
            keep = False
        if cell['id'] == 'cell-09-final-summary':
            keep = False
    if keep:
        cells_to_keep.append(cell)

d['cells'] = cells_to_keep

with open('notebooks/AstroLongevity_Data_Pipeline.ipynb', 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2)
