import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import urllib.request
import json
import os

# 1. Fetch OSD-104 Differential Expression for Volcano Plot
print("Fetching OSD-104 for Volcano Plot...")
url_104 = "https://osdr.nasa.gov/geode-py/ws/studies/OSD-104/download?source=datamanager&file=GLDS-104_rna_seq_differential_expression_GLbulkRNAseq.csv"
req = urllib.request.Request(url_104, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as response:
    df_104 = pd.read_csv(response)

# Ensure columns
df_104 = df_104.rename(columns={
    'Log2fc_(Space Flight)v(Ground Control)': 'log2FoldChange',
    'Adj.p.value_(Space Flight)v(Ground Control)': 'padj'
})
df_104['logP'] = -np.log10(df_104['padj'])

# 2. Load Concordant Signature
sig_df = pd.read_csv('public/data/Concordant_Atrophy_Signature.csv')
sig_genes = set(sig_df['SYMBOL'])

# Mark significance
df_104['Status'] = 'Not Significant'
df_104.loc[(df_104['log2FoldChange'] > 0.5) & (df_104['padj'] < 0.05), 'Status'] = 'Upregulated (OSD-104)'
df_104.loc[(df_104['log2FoldChange'] < -0.5) & (df_104['padj'] < 0.05), 'Status'] = 'Downregulated (OSD-104)'
df_104.loc[df_104['SYMBOL'].isin(sig_genes) & (df_104['log2FoldChange'] > 0), 'Status'] = 'Concordant UP (Signature)'
df_104.loc[df_104['SYMBOL'].isin(sig_genes) & (df_104['log2FoldChange'] < 0), 'Status'] = 'Concordant DOWN (Signature)'

# Volcano Plot
plt.figure(figsize=(10, 8))
colors = {
    'Not Significant': 'lightgrey',
    'Upregulated (OSD-104)': 'peachpuff',
    'Downregulated (OSD-104)': 'lightblue',
    'Concordant UP (Signature)': 'red',
    'Concordant DOWN (Signature)': 'blue'
}
sns.scatterplot(
    data=df_104, x='log2FoldChange', y='logP',
    hue='Status', palette=colors,
    s=20, alpha=0.8, edgecolor=None
)
plt.axvline(x=0.5, color='black', linestyle='--', linewidth=0.5)
plt.axvline(x=-0.5, color='black', linestyle='--', linewidth=0.5)
plt.axhline(y=-np.log10(0.05), color='black', linestyle='--', linewidth=0.5)
plt.title('Volcano Plot: OSD-104 Transcriptomic Response\nHighlighting the 139-Gene Concordant Spaceflight Signature', fontsize=14, pad=15)
plt.xlabel('Log2 Fold Change (Spaceflight vs Ground Control)', fontsize=12)
plt.ylabel('-Log10(Adjusted P-Value)', fontsize=12)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('public/data/Volcano_Plot.png', dpi=300, bbox_inches='tight')
plt.close()
print("Saved Volcano_Plot.png")

# 3. Signature Heatmap
print("Generating Signature Heatmap...")
# We use the log2fc from both OSD-101 and OSD-104 for the signature genes
heat_df = sig_df[['SYMBOL', 'Log2fc_101', 'Log2fc_104']].set_index('SYMBOL')
heat_df.columns = ['OSD-101\n(RR-4)', 'OSD-104\n(RR-1)']

# Sort by Average Log2FC
sig_df['Avg_Log2fc'] = sig_df[['Log2fc_101', 'Log2fc_104']].mean(axis=1)
sig_df = sig_df.sort_values('Avg_Log2fc', ascending=False)
heat_df = heat_df.reindex(sig_df['SYMBOL'])

plt.figure(figsize=(6, 12))
sns.heatmap(
    heat_df,
    cmap='coolwarm',
    center=0,
    cbar_kws={'label': 'Log2 Fold Change'},
    yticklabels=False # Too many genes to show names clearly
)
plt.title('Expression Heatmap of the 139 Concordant\nMuscle Atrophy Signature Genes', fontsize=14, pad=15)
plt.xlabel('Spaceflight Mission', fontsize=12)
plt.ylabel('139 Signature Genes (Sorted by Average Fold Change)', fontsize=12)
plt.tight_layout()
plt.savefig('public/data/Signature_Heatmap.png', dpi=300, bbox_inches='tight')
plt.close()
print("Saved Signature_Heatmap.png")
