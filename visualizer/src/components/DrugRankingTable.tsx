"use client";
import { useEffect, useState } from "react";
import { fetchCSV } from "@/lib/parseCSV";
import type { DrugCandidate } from "@/lib/types";

const STATUS_COLOR: Record<string, string> = {
  "FDA-Approved": "text-green-400 bg-green-900/30",
  "Phase III Clinical Trial": "text-yellow-400 bg-yellow-900/30",
  "Phase II Clinical Trial": "text-yellow-300 bg-yellow-900/20",
  "Investigational": "text-orange-400 bg-orange-900/30",
};

export default function DrugRankingTable() {
  const [drugs, setDrugs] = useState<DrugCandidate[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCSV<Record<string, unknown>>("/data/Ranked_Countermeasures.csv").then((raw) => {
      const mapped: DrugCandidate[] = raw.map((r) => ({
        Rank: Number(r.Rank ?? 0),
        Drug: String(r.Drug ?? ""),
        CMap_Score: Number(r.CMap_Score ?? 0),
        FDA_Status: String(r.FDA_Status ?? ""),
        Target: String(r.Target ?? ""),
        Mechanism: String(r.Mechanism ?? ""),
      }));
      setDrugs(mapped);
      setLoading(false);
    });
  }, []);

  return (
    <section className="card">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-2">
        <div>
          <h2 className="text-xl font-bold text-[--foreground]">
            In-Silico Drug Candidates
          </h2>
          <p className="mt-1 text-sm text-[--muted]">
            Compounds ranked by CMap anti-correlation score against the 141-gene concordant
            atrophy signature. Higher score = stronger reversal of the spaceflight atrophy
            transcriptomic signature.
          </p>
        </div>
        <span className="rounded border border-yellow-700 bg-yellow-900/20 px-3 py-1 text-xs text-yellow-400">
          ⚠ Literature-based ranking · LINCS L1000 full screening pending
        </span>
      </div>

      {loading ? (
        <div className="flex h-32 items-center justify-center text-[--muted]">Loading drug data…</div>
      ) : (
        <>
          <div className="overflow-x-auto rounded-lg border border-[--card-border]">
            <table className="w-full text-sm">
              <thead className="border-b border-[--card-border] bg-[--background]">
                <tr>
                  {["Rank", "Drug Name", "CMap Score", "FDA Status", "Target", "Mechanism"].map((h) => (
                    <th key={h} className="px-3 py-2 text-left text-xs font-semibold text-[--muted] uppercase tracking-wider whitespace-nowrap">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {drugs.map((d) => (
                  <tr key={d.Rank} className="border-b border-[--card-border] hover:bg-[--background] transition-colors">
                    <td className="px-3 py-3 text-center">
                      <span
                        className={`inline-flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold ${
                          d.Rank === 1
                            ? "bg-yellow-500 text-black"
                            : d.Rank === 2
                            ? "bg-gray-400 text-black"
                            : d.Rank === 3
                            ? "bg-amber-700 text-white"
                            : "bg-[--card-border] text-[--muted]"
                        }`}
                      >
                        {d.Rank}
                      </span>
                    </td>
                    <td className="px-3 py-3 font-semibold text-[--foreground]">{d.Drug}</td>
                    <td className="px-3 py-3">
                      <div className="flex items-center gap-2">
                        <div className="h-2 w-20 rounded-full bg-[--card-border]">
                          <div
                            className="h-2 rounded-full bg-[--accent]"
                            style={{ width: `${(d.CMap_Score * 100).toFixed(0)}%` }}
                          />
                        </div>
                        <span className="font-mono text-[--accent] text-xs">{d.CMap_Score.toFixed(3)}</span>
                      </div>
                    </td>
                    <td className="px-3 py-3">
                      <span className={`rounded px-2 py-0.5 text-xs font-semibold ${STATUS_COLOR[d.FDA_Status] ?? "text-[--muted]"}`}>
                        {d.FDA_Status}
                      </span>
                    </td>
                    <td className="px-3 py-3 text-xs text-[--muted] font-mono">{d.Target}</td>
                    <td className="px-3 py-3 text-xs text-[--muted] max-w-xs">{d.Mechanism}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <p className="mt-3 text-xs text-[--muted] border-t border-[--card-border] pt-3">
            <span className="font-semibold text-yellow-400">Disclaimer:</span> These are computationally
            ranked hypotheses generated by anti-correlation scoring against the spaceflight atrophy
            signature. They are not clinical recommendations. All candidates require experimental
            validation before any clinical consideration. CMap scores are literature-derived
            estimates pending full LINCS L1000 Connectivity Map screening.
          </p>
        </>
      )}
    </section>
  );
}
