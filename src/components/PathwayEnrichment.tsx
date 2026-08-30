"use client";
import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

type Pathway = {
  Term: string;
  "Adjusted P-value": number;
  "Combined Score": number;
  Overlap: string;
  logP?: number;
  shortTerm?: string;
};

export default function PathwayEnrichment() {
  const [goData, setGoData] = useState<Pathway[]>([]);
  const [keggData, setKeggData] = useState<Pathway[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch("/data/go_enrichment.json").then((res) => res.json()),
      fetch("/data/kegg_enrichment.json").then((res) => res.json()),
    ]).then(([go, kegg]) => {
      // Process GO
      const goProcessed = go.value.slice(0, 5).map((d: Pathway) => ({
        ...d,
        logP: -Math.log10(d["Adjusted P-value"]),
        shortTerm: d.Term.split(" (GO:")[0].substring(0, 40) + (d.Term.length > 40 ? "..." : ""),
      }));
      
      // Process KEGG
      const keggProcessed = kegg.value.map((d: Pathway) => ({
        ...d,
        logP: -Math.log10(d["Adjusted P-value"]),
        shortTerm: d.Term.substring(0, 40),
      }));

      setGoData(goProcessed);
      setKeggData(keggProcessed);
      setLoading(false);
    });
  }, []);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div style={{ background: "#1e293b", border: "1px solid #06b6d4", padding: "10px", borderRadius: "8px", color: "#f1f5f9", maxWidth: "300px" }}>
          <p className="font-bold text-[--accent] mb-1">{data.Term}</p>
          <p className="text-sm">Adj P-value: {data["Adjusted P-value"].toExponential(2)}</p>
          <p className="text-sm">Overlap: {data.Overlap}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
      <section className="card">
        <h2 className="mb-4 text-xl font-bold text-[--foreground]">
          GO Biological Processes
        </h2>
        {loading ? (
          <div className="flex h-64 items-center justify-center text-[--muted]">Loading...</div>
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={goData} layout="vertical" margin={{ top: 5, right: 30, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
              <XAxis type="number" dataKey="logP" stroke="#64748b" name="-log10(adj P)" />
              <YAxis type="category" dataKey="shortTerm" stroke="#64748b" width={220} tick={{ fontSize: 11 }} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="logP" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </section>

      <section className="card">
        <h2 className="mb-4 text-xl font-bold text-[--foreground]">
          KEGG Pathways
        </h2>
        {loading ? (
          <div className="flex h-64 items-center justify-center text-[--muted]">Loading...</div>
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={keggData} layout="vertical" margin={{ top: 5, right: 30, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
              <XAxis type="number" dataKey="logP" stroke="#64748b" name="-log10(adj P)" />
              <YAxis type="category" dataKey="shortTerm" stroke="#64748b" width={150} tick={{ fontSize: 11 }} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="logP" fill="#ec4899" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </section>
    </div>
  );
}
