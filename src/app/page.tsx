import HeroSection from "@/components/HeroSection";
import PCAScatterPlot from "@/components/PCAScatterPlot";
import GeneSignatureTable from "@/components/GeneSignatureTable";
import DrugDiscoveryTable from "@/components/DrugDiscoveryTable";
import BenchmarkStats from "@/components/BenchmarkStats";

import PathwayEnrichment from "@/components/PathwayEnrichment";

export default function Home() {
  return (
    <div className="min-h-screen" style={{ background: "var(--background)" }}>
      {/* Header */}
      <HeroSection />

      {/* Main content */}
      <main className="mx-auto max-w-7xl space-y-6 px-4 py-8 sm:px-6">
        {/* PCA Analysis */}
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
          <PCAScatterPlot 
            dataPath="/data/pca_coordinates.json"
            title="PCA Analysis — OSD-104 (RR-1)"
            description={
              <>
                12 skeletal muscle samples · PC1 explains{" "}
                <span className="text-[--accent] font-semibold">80.8%</span> of transcriptomic variance
              </>
            }
            datasetBadge="NASA OSD-104"
            footerNote="Complete inter-group separation along PC1 (FLT positive, GC negative) confirms a strong biological signal attributable to the spaceflight condition."
          />
          <PCAScatterPlot 
            dataPath="/data/pca_validation_osd168.json"
            title="External Validation PCA — OSD-168"
            description={
              <>
                Unseen validation dataset using ONLY the 139 signature genes. Clean separation proves signature robustness.
              </>
            }
            datasetBadge="NASA OSD-168"
            footerNote="Even when restricted solely to our 139-gene signature, the unseen OSD-168 samples perfectly segregate by condition."
          />
          <PCAScatterPlot 
            dataPath="/data/pca_validation_osd245.json"
            title="External Validation PCA — OSD-245"
            description={
              <>
                Second unseen validation dataset using ONLY the 139 signature genes.
              </>
            }
            datasetBadge="NASA OSD-245"
            footerNote="A second independent cohort (OSD-245) confirms the universal robustness of the spaceflight signature."
          />
        </div>

        {/* Pathway Enrichment */}
        <PathwayEnrichment />

        {/* Gene Table + Cross-Species side by side on large screens */}
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
          <GeneSignatureTable />
          <div className="flex flex-col gap-6">
            <DrugDiscoveryTable />
          </div>
        </div>

        {/* Pipeline Benchmarks */}
        <BenchmarkStats />

        {/* Footer */}
        <footer className="border-t border-[--card-border] pt-6 text-center text-xs text-[--muted]">
          <p>
            AstroLongevity · Independent Research Project · Labony Sur
          </p>
          <p className="mt-1">
            All data sourced from{" "}
            <a
              href="https://osdr.nasa.gov"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[--accent] hover:underline"
            >
              NASA Open Science Data Repository (OSDR)
            </a>
            {" "}· OSD-21 · OSD-101 · OSD-104 ·{" "}
            <a
              href="https://github.com/labonysur/AstroLongevity"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[--accent] hover:underline"
            >
              GitHub
            </a>
          </p>
          <p className="mt-1 text-[--muted]/60">
            Pipeline validated: H19 log2FC = −0.568 (manual) vs −0.5675 (NASA) · 3 sig. figs · adj.p = 5.57×10⁻¹⁰
          </p>
        </footer>
      </main>
    </div>
  );
}
