"use client";
import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { fetchCSV } from "@/lib/parseCSV";
import type { CrossSpeciesRow } from "@/lib/types";

export default function CrossSpeciesChart() {
  const [rows, setRows] = useState<CrossSpeciesRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCSV<Record<string, unknown>>("/data/Human_Mouse_CrossSpecies_Benchmark.csv").then((raw) => {
      const mapped: CrossSpeciesRow[] = raw.map((r) => ({
        Gene: String(r.Gene ?? ""),
        Mouse_Log2FC: Number(r.Spaceflight_Mouse_Log2FC ?? 0),
        Mouse_Adj_P: Number(r.Mouse_Adj_P_value ?? 1),
        Human_Log2FC: Number(r.Human_Atrophy_Log2FC ?? 0),
        Agreement: String(r.Directional_Agreement ?? ""),
        Human_Source: String(r.Human_Source ?? ""),
      }));
      setRows(mapped);
      setLoading(false);
    });
  }, []);

  const chartData = rows.map((r) => ({
    gene: r.Gene,
    Mouse: r.Mouse_Log2FC,
    Human: r.Human_Log2FC,
    agreement: r.Agreement === "YES",
  }));

  return (
    <section className="card">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-[--foreground]">
          Cross-Species Translational Validation
        </h2>
        <p className="mt-1 text-sm text-[--muted]">
          Mouse spaceflight Log2FC (OSD-104) vs. Human clinical atrophy Log2FC for 4 key
          genes. Green border = directional agreement (conserved marker). Red border = discordance.
        </p>
      </div>

      {loading ? (
        <div className="flex h-48 items-center justify-center text-[--muted]">
          Loading cross-species data…
        </div>
      ) : (
        <>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData} margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <ReferenceLine y={0} stroke="#334155" />
              <XAxis dataKey="gene" tick={{ fill: "#94a3b8", fontWeight: 700, fontSize: 13 }} />
              <YAxis
                label={{ value: "Log2FC", angle: -90, position: "insideLeft", fill: "#64748b", fontSize: 12 }}
                tick={{ fill: "#64748b", fontSize: 11 }}
              />
              <Tooltip
                contentStyle={{ background: "#1e293b", border: "1px solid #06b6d4", borderRadius: 8, fontSize: 12 }}
                labelStyle={{ color: "#06b6d4", fontWeight: 700 }}
                itemStyle={{ color: "#f1f5f9" }}
                formatter={(value) => (typeof value === "number" ? value.toFixed(4) : value)}
              />
              <Legend
                wrapperStyle={{ fontSize: 13, paddingTop: 12 }}
                formatter={(v) => <span style={{ color: "#f1f5f9" }}>{v}</span>}
              />
              <Bar dataKey="Mouse" name="Mouse (Spaceflight)" radius={[4, 4, 0, 0]}>
                {chartData.map((entry, i) => (
                  <Cell
                    key={i}
                    fill={entry.Mouse > 0 ? "#ef4444" : "#3b82f6"}
                    stroke={entry.agreement ? "#22c55e" : "#ef4444"}
                    strokeWidth={2}
                  />
                ))}
              </Bar>
              <Bar dataKey="Human" name="Human (Atrophy)" radius={[4, 4, 0, 0]}>
                {chartData.map((entry, i) => (
                  <Cell
                    key={i}
                    fill={entry.Human > 0 ? "#fca5a5" : "#93c5fd"}
                    opacity={0.75}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>

          {/* Table */}
          <div className="mt-4 overflow-x-auto rounded-lg border border-[--card-border]">
            <table className="w-full text-xs">
              <thead className="border-b border-[--card-border] bg-[--background]">
                <tr>
                  {["Gene", "Mouse Log2FC", "Mouse Adj.p", "Human Log2FC", "Agreement", "Human Reference"].map((h) => (
                    <th key={h} className="px-3 py-2 text-left font-semibold text-[--muted] uppercase tracking-wider">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.Gene} className="border-b border-[--card-border] hover:bg-[--background]">
                    <td className="px-3 py-2 font-mono font-bold text-[--foreground]">{r.Gene}</td>
                    <td className={`px-3 py-2 font-mono font-semibold ${r.Mouse_Log2FC > 0 ? "text-[--up]" : "text-[--down]"}`}>
                      {r.Mouse_Log2FC > 0 ? "+" : ""}{r.Mouse_Log2FC.toFixed(4)}
                    </td>
                    <td className="px-3 py-2 font-mono text-[--muted]">{r.Mouse_Adj_P.toExponential(2)}</td>
                    <td className={`px-3 py-2 font-mono font-semibold ${r.Human_Log2FC > 0 ? "text-[--up]" : "text-[--down]"}`}>
                      {r.Human_Log2FC > 0 ? "+" : ""}{r.Human_Log2FC.toFixed(2)}
                    </td>
                    <td className="px-3 py-2">
                      {r.Agreement === "YES" ? (
                        <span className="rounded bg-green-900/40 px-2 py-0.5 text-[--agree] font-bold">✓ YES</span>
                      ) : (
                        <span className="rounded bg-red-900/40 px-2 py-0.5 text-[--up]">✗ NO</span>
                      )}
                    </td>
                    <td className="px-3 py-2 text-[--muted] max-w-xs truncate" title={r.Human_Source}>
                      {r.Human_Source.split(",")[0]}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <p className="mt-3 text-xs text-[--muted]">
            <span className="font-semibold text-[--agree]">IGF1</span> shows directional agreement
            between mouse spaceflight and human clinical atrophy (both downregulated),
            validating it as a conserved cross-species marker. H19, MYOD1, and VEGFA show
            discordance — consistent with known species-specific regulatory differences.
          </p>
        </>
      )}
    </section>
  );
}
