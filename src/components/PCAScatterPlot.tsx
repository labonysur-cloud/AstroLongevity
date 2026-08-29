"use client";
import { useEffect, useState } from "react";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

import type { PCAPoint } from "@/lib/types";

type TooltipPayload = { payload: PCAPoint };

function CustomTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: TooltipPayload[];
}) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div
      style={{
        background: "#1e293b",
        border: "1px solid #06b6d4",
        borderRadius: 8,
        padding: "10px 14px",
        fontSize: 12,
        color: "#f1f5f9",
        maxWidth: 260,
      }}
    >
      <div style={{ fontWeight: 700, marginBottom: 4, color: "#06b6d4" }}>
        {d.Sample.split("_").slice(-2).join(" ")}
      </div>
      <div>
        <span style={{ color: "#94a3b8" }}>Condition: </span>
        {d.Condition}
      </div>
      <div>
        <span style={{ color: "#94a3b8" }}>PC1: </span>
        {d.PC1.toFixed(2)}
      </div>
      <div>
        <span style={{ color: "#94a3b8" }}>PC2: </span>
        {d.PC2.toFixed(2)}
      </div>
    </div>
  );
}

export default function PCAScatterPlot() {
  const [flt, setFlt] = useState<PCAPoint[]>([]);
  const [gc, setGc] = useState<PCAPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/data/pca_coordinates.json").then(res => res.json()).then((rows) => {
      setFlt(rows.filter((r) => r.Condition.includes("FLT") || r.Condition.includes("Spaceflight")));
      setGc(rows.filter((r) => r.Condition.includes("GC") || r.Condition.includes("Ground")));
      setLoading(false);
    });
  }, []);

  return (
    <section className="card">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-2">
        <div>
          <h2 className="text-xl font-bold text-[--foreground]">
            PCA Analysis — OSD-104 (Rodent Research 1)
          </h2>
          <p className="mt-1 text-sm text-[--muted]">
            12 skeletal muscle samples · PC1 explains{" "}
            <span className="text-[--accent] font-semibold">80.8%</span> of transcriptomic variance ·
            PC2 explains{" "}
            <span className="text-[--accent] font-semibold">12.1%</span>
          </p>
        </div>
        <span className="rounded border border-[--card-border] px-2 py-1 text-xs text-[--muted]">
          NASA OSD-104 · GLbulkRNAseq pipeline
        </span>
      </div>

      {loading ? (
        <div className="flex h-64 items-center justify-center text-[--muted]">
          Loading PCA data…
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={360}>
          <ScatterChart margin={{ top: 10, right: 30, bottom: 20, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <ReferenceLine x={0} stroke="#334155" strokeDasharray="4 4" />
            <ReferenceLine y={0} stroke="#334155" strokeDasharray="4 4" />
            <XAxis
              type="number"
              dataKey="PC1"
              name="PC1"
              label={{
                value: "PC1 (80.8% variance)",
                position: "insideBottom",
                offset: -10,
                fill: "#64748b",
                fontSize: 12,
              }}
              tick={{ fill: "#64748b", fontSize: 11 }}
              domain={["auto", "auto"]}
            />
            <YAxis
              type="number"
              dataKey="PC2"
              name="PC2"
              label={{
                value: "PC2 (12.1%)",
                angle: -90,
                position: "insideLeft",
                fill: "#64748b",
                fontSize: 12,
              }}
              tick={{ fill: "#64748b", fontSize: 11 }}
              domain={["auto", "auto"]}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: 13, paddingTop: 16 }}
              formatter={(value) => (
                <span style={{ color: "#f1f5f9" }}>{value}</span>
              )}
            />
            <Scatter
              name="Spaceflight (FLT)"
              data={flt}
              fill="#ef4444"
              shape="circle"
              r={7}
            />
            <Scatter
              name="Ground Control (GC)"
              data={gc}
              fill="#3b82f6"
              shape="circle"
              r={7}
            />
          </ScatterChart>
        </ResponsiveContainer>
      )}

      <p className="mt-3 text-xs text-[--muted]">
        Complete inter-group separation along PC1 (FLT positive, GC negative) confirms a strong
        biological signal attributable to the spaceflight condition. No batch effects —
        all 12 samples processed through the same NASA GLbulkRNAseq pipeline.
      </p>
    </section>
  );
}
