"use client";
import { useEffect, useState } from "react";
import Image from "next/image";

type DrugRow = {
  Drug_Name: string;
  Reversal_Score: number;
  Cell_Line: string;
  Dose: string;
  Time: string;
  PubChem_ID: string;
  Perturbagen_ID: string;
};

export default function DrugDiscoveryTable() {
  const [rows, setRows] = useState<DrugRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/data/l1000_drug_candidates.json")
      .then((res) => res.json())
      .then((data) => {
        setRows(data);
        setLoading(false);
      });
  }, []);

  return (
    <section className="card flex flex-col gap-6">
      <div>
        <h2 className="text-xl font-bold text-[--foreground]">
          Candidate Countermeasure Perturbations (LINCS L1000)
        </h2>
        <p className="mt-1 text-sm text-[--muted]">
          Prioritized compounds whose transcriptional signatures mathematically oppose the spaceflight 
          muscle-atrophy profile. 
          <br/>
          <span className="italic">Note: Higher L1000CDS2 reversal scores indicate stronger transcriptomic opposition, 
          not guaranteed therapeutic efficacy. These are hypotheses for experimental validation.</span>
        </p>
      </div>

      {loading ? (
        <div className="flex h-48 items-center justify-center text-[--muted]">
          Loading candidate countermeasures...
        </div>
      ) : (
        <>
          <div className="overflow-x-auto rounded-lg border border-[--card-border]">
            <table className="w-full text-xs">
              <thead className="border-b border-[--card-border] bg-[--background]">
                <tr>
                  <th className="px-3 py-2 text-left font-semibold text-[--muted] uppercase tracking-wider">Candidate</th>
                  <th className="px-3 py-2 text-left font-semibold text-[--muted] uppercase tracking-wider">L1000CDS2 Reversal Score</th>
                  <th className="px-3 py-2 text-left font-semibold text-[--muted] uppercase tracking-wider">Cell Line</th>
                  <th className="px-3 py-2 text-left font-semibold text-[--muted] uppercase tracking-wider">Dose / Time</th>
                  <th className="px-3 py-2 text-left font-semibold text-[--muted] uppercase tracking-wider">Perturbagen ID</th>
                </tr>
              </thead>
              <tbody>
                {rows.slice(0, 8).map((r, i) => (
                  <tr key={i} className="border-b border-[--card-border] hover:bg-[--background]">
                    <td className="px-3 py-2 font-mono font-bold text-[--accent]">{r.Drug_Name}</td>
                    <td className="px-3 py-2 font-mono font-semibold">{r.Reversal_Score.toFixed(4)}</td>
                    <td className="px-3 py-2 text-[--muted]">{r.Cell_Line}</td>
                    <td className="px-3 py-2 text-[--muted]">{r.Dose} / {r.Time}</td>
                    <td className="px-3 py-2 font-mono text-[--muted]">{r.Perturbagen_ID}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-4 flex flex-col items-center border-t border-[--card-border] pt-6">
            <h3 className="mb-4 text-lg font-bold text-[--foreground]">Transcriptomic Signature Reversal</h3>
            <p className="mb-4 text-center text-sm text-[--muted] max-w-2xl">
              Heatmap demonstrating directional opposition between the observed Spaceflight (OSD-101 + OSD-104) 
              transcriptomic response and the expected effect of the top prioritized countermeasure.
            </p>
            <div className="relative w-full max-w-md h-[500px] rounded-lg overflow-hidden border border-[--card-border]">
              <Image 
                src="/data/Reversal_Heatmap.png" 
                alt="Signature Reversal Heatmap"
                fill
                style={{ objectFit: 'contain' }}
              />
            </div>
          </div>
        </>
      )}
    </section>
  );
}
