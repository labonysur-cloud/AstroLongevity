export default function HeroSection() {
  return (
    <header className="w-full border-b border-[--card-border] bg-[--card] px-6 py-8">
      <div className="mx-auto max-w-7xl">
        {/* Top badges */}
        <div className="mb-4 flex flex-wrap items-center gap-3">
          <span className="rounded-full bg-[--accent] px-3 py-1 text-xs font-bold text-[--background] tracking-widest uppercase">
            NASA Space Apps Challenge 2026
          </span>
          <span className="rounded-full border border-[--accent] px-3 py-1 text-xs text-[--accent]">
            Dhaka Local Event · Team Sur
          </span>
          <span className="rounded-full border border-[--card-border] px-3 py-1 text-xs text-[--muted]">
            Theme: The Next Frontier
          </span>
        </div>

        {/* Title */}
        <h1 className="text-4xl font-bold tracking-tight text-[--foreground] sm:text-5xl">
          Astro<span className="text-[--accent]">Longevity</span>
        </h1>
        <p className="mt-2 max-w-3xl text-base text-[--muted]">
          Analyzing NASA OSDR spaceflight transcriptomics to identify muscle atrophy gene
          signatures and computationally screen drug candidates for astronaut health and
          terrestrial sarcopenia research.
        </p>

        {/* Stat cards */}
        <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
          {[
            { value: "141", label: "Concordant Genes", sub: "across OSD-101 + OSD-104" },
            { value: "3", label: "NASA Datasets", sub: "OSD-21 · OSD-101 · OSD-104" },
            { value: "22,437", label: "Genes Analyzed", sub: "OSD-104 RNA-Seq" },
            { value: "10", label: "Drug Candidates", sub: "in-silico ranked" },
          ].map((s) => (
            <div
              key={s.label}
              className="card border border-[--accent] bg-[--accent-glow] text-center"
              style={{ background: "var(--accent-glow)", borderColor: "var(--accent)" }}
            >
              <div className="text-3xl font-bold text-[--accent]">{s.value}</div>
              <div className="text-sm font-semibold text-[--foreground]">{s.label}</div>
              <div className="mt-1 text-xs text-[--muted]">{s.sub}</div>
            </div>
          ))}
        </div>

        {/* Dataset pills */}
        <div className="mt-5 flex flex-wrap gap-2 text-xs">
          {[
            "OSD-21: Microarray · 230,756 probes",
            "OSD-101: RNA-Seq · 23,257 genes · Rodent Research 4",
            "OSD-104: RNA-Seq · 22,437 genes · Rodent Research 1",
          ].map((d) => (
            <span
              key={d}
              className="rounded border border-[--card-border] bg-[--background] px-3 py-1 text-[--muted]"
            >
              {d}
            </span>
          ))}
        </div>
      </div>
    </header>
  );
}
