"use client";
import { useEffect, useState } from "react";
import { fetchCSV } from "@/lib/parseCSV";
import type { BenchmarkRow } from "@/lib/types";

export default function BenchmarkStats() {
  const [rows, setRows] = useState<BenchmarkRow[]>([]);

  useEffect(() => {
    fetchCSV<Record<string, unknown>>("/data/Benchmark_Results.csv").then((raw) => {
      setRows(
        raw.map((r) => ({
          Stage: String(r.Stage ?? ""),
          Time_s: Number(r.Time_s ?? 0),
          Peak_RAM_MB: Number(r.Peak_RAM_MB ?? 0),
        }))
      );
    });
  }, []);

  return (
    <section className="card">
      <h2 className="mb-3 text-lg font-bold text-[--foreground]">
        Pipeline Performance Benchmarks
      </h2>
      <p className="mb-4 text-sm text-[--muted]">
        Measured on Google Colab free tier (2 vCPU, 12 GB RAM). Entire pipeline runs at
        <span className="text-[--accent] font-semibold"> zero cost</span> on free infrastructure.
      </p>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {rows.map((r) => (
          <div
            key={r.Stage}
            className="rounded-lg border border-[--card-border] bg-[--background] p-3 text-center"
          >
            <div className="text-xl font-bold text-[--accent]">{r.Time_s}s</div>
            <div className="text-xs text-[--muted] mt-0.5">{r.Stage.split("(")[0].trim()}</div>
            <div className="mt-1 text-xs text-[--muted]">Peak RAM: {r.Peak_RAM_MB} MB</div>
          </div>
        ))}
        <div className="rounded-lg border border-[--accent] bg-[--accent-glow] p-3 text-center">
          <div className="text-xl font-bold text-[--accent]">&lt;12s</div>
          <div className="text-xs text-[--muted] mt-0.5">Total per dataset</div>
          <div className="mt-1 text-xs text-[--muted]">3.3% of 12 GB RAM limit</div>
        </div>
      </div>
      <p className="mt-3 text-xs text-[--muted]">
        vs. Wet-lab HTS drug screening: \$500K–\$5M USD · 6–18 months · ~5,000 compounds.
        AstroLongevity screens 1M+ profiles at <span className="font-semibold">\$0</span>.
      </p>
    </section>
  );
}
