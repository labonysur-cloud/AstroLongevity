import HeroSection from "@/components/HeroSection";
import PCAScatterPlot from "@/components/PCAScatterPlot";
import GeneSignatureTable from "@/components/GeneSignatureTable";
import DrugDiscoveryTable from "@/components/DrugDiscoveryTable";
import BenchmarkStats from "@/components/BenchmarkStats";
import PathwayEnrichment from "@/components/PathwayEnrichment";
import MoleculeViewer from "@/components/MoleculeViewer";

export default function Home() {
  return (
    <div className="min-h-screen" style={{ background: "var(--background)" }}>
      {/* Header */}
      <HeroSection />

      {/* Main content */}
      <main className="mx-auto max-w-7xl space-y-6 px-4 py-8 sm:px-6 relative z-10">
        
        {/* Real-time 3D Visualizer Section */}
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
          <MoleculeViewer 
            modelUrl="/data/docking_prep/CNTFR_8D74.pdb"
            modelFormat="pdb"
            title="Real-Time Target Visualizer: CNTFR (Protein)"
            description="Interactive 3D view of the Ciliary Neurotrophic Factor Receptor (CNTFR) structure. Scroll to zoom, drag to rotate."
          />
          <MoleculeViewer 
            modelUrl="/data/docking_prep/LDN-193189_25195294.sdf"
            modelFormat="sdf"
            title="Real-Time Perturbagen Visualizer: LDN-193189"
            description="Interactive 3D view of the candidate countermeasure LDN-193189. Scroll to zoom, drag to rotate."
          />
        </div>

        {/* PCA Analysis */}
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
          <PCAScatterPlot 
            dataPath="/data/pca_coordinates.json"
            title="PCA Analysis: OSD-104 (RR-1)"
            description={
              <>
                12 skeletal muscle samples. PC1 explains{" "}
                <span className="text-[--accent] font-semibold">80.8%</span> of transcriptomic variance
              </>
            }
            datasetBadge="NASA OSD-104"
            footerNote="Complete inter-group separation along PC1 (FLT positive, GC negative) confirms a strong biological signal attributable to the spaceflight condition."
          />
          <PCAScatterPlot 
            dataPath="/data/pca_validation_osd243.json"
            title="External Validation PCA: OSD-243"
            description={
              <>
                Unseen validation dataset using ONLY the signature genes.
              </>
            }
            datasetBadge="NASA OSD-243"
            footerNote="Independent cohort (OSD-243) separated cleanly by the spaceflight signature."
          />
          <PCAScatterPlot 
            dataPath="/data/pca_validation_osd245.json"
            title="External Validation PCA: OSD-245"
            description={
              <>
                Second unseen validation dataset using ONLY the signature genes.
              </>
            }
            datasetBadge="NASA OSD-245"
            footerNote="Independent cohort (OSD-245) separated cleanly by the spaceflight signature."
          />
          <PCAScatterPlot 
            dataPath="/data/pca_validation_osd379.json"
            title="External Validation PCA: OSD-379"
            description={
              <>
                Third unseen validation dataset using ONLY the signature genes.
              </>
            }
            datasetBadge="NASA OSD-379"
            footerNote="Independent cohort (OSD-379) separated cleanly by the spaceflight signature."
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
            AstroLongevity : Independent Research Project : Labony Sur
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
            {" "}: OSD-21 : OSD-101 : OSD-104 : OSD-243 : OSD-245 : OSD-379 :{" "}
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
            Pipeline validated: H19 log2FC = -0.568 (manual) vs -0.5675 (NASA) : 3 sig. figs : adj.p = 5.57x10^-10
          </p>
        </footer>
      </main>
    </div>
  );
}
