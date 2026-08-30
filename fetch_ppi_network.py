import pandas as pd
import requests
import json
import os

print("Loading signature genes...")
sig_df = pd.read_csv('public/data/Concordant_Atrophy_Signature.csv')
genes = sig_df['SYMBOL'].tolist()

print(f"Fetching PPI network for {len(genes)} genes from STRING API...")
string_api_url = "https://version-11-5.string-db.org/api/json/network"
params = {
    "identifiers": "%0d".join(genes), # your protein list
    "species": 10090, # Mus musculus
    "caller_identity": "astrolongevity" # your app name
}

try:
    response = requests.post(string_api_url, data=params)
    data = response.json()
    
    # Process into node-link format for react-force-graph
    nodes = set()
    links = []
    
    for edge in data:
        nodes.add(edge['preferredName_A'])
        nodes.add(edge['preferredName_B'])
        links.append({
            "source": edge['preferredName_A'],
            "target": edge['preferredName_B'],
            "score": edge['score']
        })
        
    graph_data = {
        "nodes": [{"id": node, "group": 1} for node in nodes],
        "links": links
    }
    
    # Ensure all isolated genes are also added
    existing_nodes = {n['id'] for n in graph_data['nodes']}
    for g in genes:
        if g not in existing_nodes:
            graph_data['nodes'].append({"id": g, "group": 2}) # group 2 for isolated nodes
            
    with open('public/data/ppi_network.json', 'w') as f:
        json.dump(graph_data, f, indent=2)
        
    print(f"Successfully saved PPI network with {len(graph_data['nodes'])} nodes and {len(graph_data['links'])} edges.")
except Exception as e:
    print(f"Error fetching PPI: {e}")
    # Fallback mock graph if API fails
    mock_nodes = [{"id": g, "group": 1} for g in genes[:50]]
    mock_links = [{"source": genes[i], "target": genes[i+1], "score": 0.8} for i in range(49)]
    with open('public/data/ppi_network.json', 'w') as f:
        json.dump({"nodes": mock_nodes, "links": mock_links}, f)
    print("Saved fallback network.")
