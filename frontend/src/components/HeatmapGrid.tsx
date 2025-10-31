import React, { useEffect, useRef, useState } from "react";
import api from "../api/apiClient";

type HeatPoint = { x: number; y: number; value: number };
type HeatResponse = {
  base_image: string;     // π.χ. "/media/parking_layout.jpg"
  max_value: number;      // π.χ. 1.0
  points: HeatPoint[];    // [{x, y, value}]
};

type Props = {
  refreshMs?: number;     // κάθε πόσο να κάνει auto-refresh
  radius?: number;        // μέγεθος "θερμού" κύκλου
  strength?: number;      // ένταση χρώματος (0–1)
};

const HeatmapCanvas: React.FC<Props> = ({
  refreshMs = 10000,      // default κάθε 10 δευτερόλεπτα
  radius = 28,
  strength = 0.9,
}) => {
  const [data, setData] = useState<HeatResponse | null>(null);
  const imgRef = useRef<HTMLImageElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string>("");

  // 🔹 Fetch heatmap data (backend)
  const fetchData = async () => {
    try {
      const res = await api.get("/heatmap/");
      setData(res.data);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (err) {
      console.error("Error fetching heatmap data:", err);
    }
  };

  // 🔹 Initial + periodic refresh
  useEffect(() => {
    fetchData();
    const id = setInterval(fetchData, refreshMs);
    return () => clearInterval(id);
  }, [refreshMs]);

  // 🔹 Draw heatmap
  useEffect(() => {
    const img = imgRef.current;
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!data || !img || !canvas || !container) return;

    const render = () => {
      const displayW = img.clientWidth;
      const displayH = img.clientHeight;

      // Resize canvas to image dimensions
      canvas.width = displayW;
      canvas.height = displayH;
      container.style.width = `${displayW}px`;
      container.style.height = `${displayH}px`;

      const ctx = canvas.getContext("2d");
      if (!ctx) return;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const baseW = img.naturalWidth;
      const baseH = img.naturalHeight;
      const sx = displayW / baseW;
      const sy = displayH / baseH;

      for (const p of data.points) {
        const x = Math.round(p.x * sx);
        const y = Math.round(p.y * sy);
        const r = radius;
        const alpha = Math.max(0, Math.min(1, p.value * strength));

        const grad = ctx.createRadialGradient(x, y, 0, x, y, r);
        grad.addColorStop(0.0, `rgba(255,0,0,${alpha})`);
        grad.addColorStop(0.5, `rgba(255,165,0,${alpha * 0.5})`);
        grad.addColorStop(1.0, `rgba(255,255,0,0)`);

        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(x, y, r, 0, Math.PI * 2);
        ctx.fill();
      }

      // Optional blur
      // @ts-ignore
      if ("filter" in ctx) {
        // @ts-ignore
        ctx.filter = "blur(0.6px)";
        const snapshot = ctx.getImageData(0, 0, canvas.width, canvas.height);
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.putImageData(snapshot, 0, 0);
        // @ts-ignore
        ctx.filter = "none";
      }
    };

    if (img.complete) render();
    else img.onload = render;

    const onResize = () => render();
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, [data, radius, strength]);

  if (!data) return <p className="text-center p-4 text-gray-500">Loading heatmap...</p>;

  return (
    <div className="flex flex-col justify-center items-center min-h-screen bg-gray-100">
      <h1 className="text-2xl font-bold mb-4">Parking Heatmap</h1>
      <h1 className="text-2xl font-bold mb-4">Last updated: {lastUpdated || "Loading..."}</h1>
      <div className="relative flex justify-center items-center">
        {/* Base Image */}
        <img
          ref={imgRef}
          src={`http://localhost:8000${data.base_image}`}
          alt="Parking layout"
          className="rounded-lg shadow-lg max-w-[80vw] h-auto block"
          style={{ display: "block" }}
        />
        {/* Canvas Overlay */}
        <div
          ref={containerRef}
          className="absolute top-0 left-0 pointer-events-none flex justify-center items-center"
          style={{ width: 0, height: 0 }}
        >
          <canvas ref={canvasRef} />
        </div>
      </div>

      {/* Timestamp info */}

    </div>
  );
};

export default HeatmapCanvas;
