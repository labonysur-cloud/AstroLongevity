import HeroSection from "@/components/HeroSection";
import PCAScatterPlot from "@/components/PCAScatterPlot";
import GeneSignatureTable from "@/components/GeneSignatureTable";
import DrugDiscoveryTable from "@/components/DrugDiscoveryTable";
import BenchmarkStats from "@/components/BenchmarkStats";

export default function Home() {
  return (
    <div className="min-h-screen" style={{ background: "var(--background)" }}>
      {/* Header */}
      <HeroSection />

      {/* Main content */}
      <main className="mx-auto max-w-7xl space-y-6 px-4 py-8 sm:px-6">
        {/* PCA Analysis */}
        <PCAScatterPlot />

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
            AstroLongevity · NASA Space Apps Challenge 2026 · Team Astrophel · Labony Sur, Aupurba Sarker
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
