"use client";
import { useEffect, useRef, useState } from "react";
import dynamic from "next/dynamic";

// Dynamically import react-force-graph-3d to avoid SSR issues with window/document
const ForceGraph3D = dynamic(() => import("react-force-graph-3d"), { ssr: false });

export default function KnowledgeGraph() {
  const [data, setData] = useState<{ nodes: any[]; links: any[] } | null>(null);

  useEffect(() => {
    fetch("/data/ppi_network.json")
      .then((res) => res.json())
      .then((json) => setData(json));
  }, []);

  return (
    <section className="card">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-2">
        <div>
          <h2 className="text-xl font-bold text-[--foreground]">
            Protein-Protein Interaction (PPI) Knowledge Graph
          </h2>
          <p className="mt-1 text-sm text-[--muted]">
            Real-time 3D network topology of the 139 signature genes. Pulled directly from the STRING DB. Nodes are colored by sub-network modules. You can drag, zoom, and rotate the network.
          </p>
        </div>
        <span className="rounded border border-[--card-border] px-2 py-1 text-xs text-[--muted]">
          STRING Network
        </span>
      </div>

      <div className="relative w-full h-[500px] rounded-lg border border-[var(--card-border)] overflow-hidden bg-black/5 shadow-inner">
        {data ? (
          <ForceGraph3D
            graphData={data}
            nodeLabel="id"
            nodeAutoColorBy="group"
            linkWidth={1}
            linkOpacity={0.3}
            backgroundColor="rgba(0,0,0,0)"
            nodeRelSize={6}
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-[--muted]">
            Loading 3D Knowledge Graph...
          </div>
        )}
      </div>
    </section>
  );
}
