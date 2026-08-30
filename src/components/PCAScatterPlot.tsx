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
        background: "var(--card)",
        border: "1px solid var(--accent)",
        borderRadius: 8,
        padding: "10px 14px",
        fontSize: 12,
        color: "var(--foreground)",
        maxWidth: 260,
      }}
    >
      <div style={{ fontWeight: 700, marginBottom: 4, color: "var(--accent)" }}>
        {d.Sample.split("_").slice(-2).join(" ")}
      </div>
      <div>
        <span style={{ color: "var(--muted)" }}>Condition: </span>
        {d.Condition}
      </div>
      <div>
        <span style={{ color: "var(--muted)" }}>PC1: </span>
        {d.PC1.toFixed(2)}
      </div>
      <div>
        <span style={{ color: "var(--muted)" }}>PC2: </span>
        {d.PC2.toFixed(2)}
      </div>
    </div>
  );
}

export default function PCAScatterPlot({
  dataPath,
  title,
  description,
  datasetBadge,
  footerNote
}: {
  dataPath: string;
  title: string;
  description: React.ReactNode;
  datasetBadge: string;
  footerNote?: string;
}) {
  const [flt, setFlt] = useState<PCAPoint[]>([]);
  const [gc, setGc] = useState<PCAPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(dataPath).then(res => res.json()).then((rows: any[]) => {
      setFlt(rows.filter((r: any) => r.Condition.includes("FLT") || r.Condition.includes("Spaceflight")));
      setGc(rows.filter((r: any) => r.Condition.includes("GC") || r.Condition.includes("Ground")));
      setLoading(false);
    });
  }, [dataPath]);

  return (
    <section className="card">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-2">
        <div>
          <h2 className="text-xl font-bold text-[--foreground]">
            {title}
          </h2>
          <p className="mt-1 text-sm text-[--muted]">
            {description}
          </p>
        </div>
        <span className="rounded border border-[--card-border] px-2 py-1 text-xs text-[--muted]">
          {datasetBadge}
        </span>
      </div>

      {loading ? (
        <div className="flex h-64 items-center justify-center text-[--muted]">
          Loading PCA data…
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={360}>
          <ScatterChart margin={{ top: 10, right: 30, bottom: 20, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--card-border)" />
            <ReferenceLine x={0} stroke="var(--muted)" strokeDasharray="4 4" opacity={0.5} />
            <ReferenceLine y={0} stroke="var(--muted)" strokeDasharray="4 4" opacity={0.5} />
            <XAxis
              type="number"
              dataKey="PC1"
              name="PC1"
              label={{
                value: "PC1",
                position: "insideBottom",
                offset: -10,
                fill: "var(--muted)",
                fontSize: 12,
              }}
              tick={{ fill: "var(--muted)", fontSize: 11 }}
              domain={["auto", "auto"]}
            />
            <YAxis
              type="number"
              dataKey="PC2"
              name="PC2"
              label={{
                value: "PC2",
                angle: -90,
                position: "insideLeft",
                fill: "var(--muted)",
                fontSize: 12,
              }}
              tick={{ fill: "var(--muted)", fontSize: 11 }}
              domain={["auto", "auto"]}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: 13, paddingTop: 16 }}
              formatter={(value) => (
                <span style={{ color: "var(--foreground)" }}>{value}</span>
              )}
            />
            <Scatter
              name="Spaceflight (FLT)"
              data={flt}
              fill="var(--up)"
              shape="circle"
              r={7}
            />
            <Scatter
              name="Ground Control (GC)"
              data={gc}
              fill="var(--down)"
              shape="circle"
              r={7}
            />
          </ScatterChart>
        </ResponsiveContainer>
      )}

      {footerNote && (
        <p className="mt-3 text-xs text-[--muted]">
          {footerNote}
        </p>
      )}
    </section>
  );
}
