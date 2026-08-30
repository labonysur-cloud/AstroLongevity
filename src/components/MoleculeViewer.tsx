"use client";
import { useEffect, useRef, useState } from "react";

export default function MoleculeViewer({
  modelUrl,
  modelFormat,
  title,
  description
}: {
  modelUrl: string;
  modelFormat: string;
  title: string;
  description: string;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let viewer: any = null;

    const initViewer = () => {
      if (!window.$3Dmol || !containerRef.current) return;
      
      containerRef.current.innerHTML = "";
      viewer = window.$3Dmol.createViewer(containerRef.current, {
        backgroundColor: "white",
      });

      fetch(modelUrl)
        .then((res) => res.text())
        .then((data) => {
          viewer.addModel(data, modelFormat);
          if (modelFormat === "pdb") {
            viewer.setStyle({}, { cartoon: { color: "spectrum" } });
          } else {
            viewer.setStyle({}, { stick: { colorscheme: "Jmol" } });
          }
          viewer.zoomTo();
          viewer.render();
          viewer.spin("y", 0.5);
          setLoading(false);
        })
        .catch((err) => {
          console.error("Error loading 3D model:", err);
          setLoading(false);
        });
    };

    if (!window.$3Dmol) {
      const script = document.createElement("script");
      script.src = "https://3Dmol.csb.pitt.edu/build/3Dmol-min.js";
      script.onload = initViewer;
      document.body.appendChild(script);
    } else {
      initViewer();
    }

    return () => {
      if (viewer) {
        viewer.clear();
      }
    };
  }, [modelUrl, modelFormat]);

  return (
    <section className="card group relative overflow-hidden transition-all duration-500 hover:shadow-[0_0_30px_rgba(6,182,212,0.3)] hover:-translate-y-1">
      <div className="absolute inset-0 bg-gradient-to-br from-[var(--card)] to-[var(--background)] opacity-50 z-0"></div>
      <div className="relative z-10">
        <h2 className="mb-2 text-xl font-bold text-[var(--foreground)]">{title}</h2>
        <p className="mb-4 text-sm text-[var(--muted)]">{description}</p>
        <div 
          ref={containerRef} 
          className="relative w-full h-[350px] rounded-lg border border-[var(--card-border)] bg-white overflow-hidden shadow-inner"
        >
          {loading && (
            <div className="absolute inset-0 flex items-center justify-center bg-[var(--card)] text-[var(--muted)] z-20">
              Loading 3D visualization...
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

declare global {
  interface Window {
    $3Dmol: any;
  }
}
