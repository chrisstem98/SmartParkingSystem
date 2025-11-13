import React, { useEffect, useRef, useState } from "react";
import api from "../api/apiClient";

interface HeatPoint {
  x: number;
  y: number;
  value: number; // 0..1
}

interface HeatmapResponse {
  background_url: string | null;
  heatmap_points: HeatPoint[];
}

const HeatmapCanvas: React.FC<{ site: string }> = ({ site }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [backgroundImage, setBackgroundImage] = useState<HTMLImageElement | null>(null);
  const [points, setPoints] = useState<HeatPoint[]>([]);

  // --- Load backend data & image ---
  useEffect(() => {
    async function fetchData() {
      try {
        const res = await api.get(`/heatmap/?site=${site}`);
        const data: HeatmapResponse = res.data;

        setPoints(data.heatmap_points);

        if (data.background_url) {
          const img = new Image();
          img.src = data.background_url;

          img.onload = () => setBackgroundImage(img);
        }
      } catch (err) {
        console.error("Heatmap error:", err);
      }
    }

    fetchData();
  }, [site]);

  // --- Draw heatmap ---
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !backgroundImage) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    canvas.width = backgroundImage.width;
    canvas.height = backgroundImage.height;

    // Draw background map
    ctx.drawImage(backgroundImage, 0, 0);

    // Draw heatmap points
    points.forEach(({ x, y, value }) => {
      const intensity = Math.floor(value * 255);
      ctx.fillStyle = `rgba(255, 0, 0, ${value})`; // red glow
      const radius = 20;

      const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
      gradient.addColorStop(0, `rgba(255,0,0,${value})`);
      gradient.addColorStop(1, "rgba(255,0,0,0)");

      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fill();
    });
  }, [backgroundImage, points]);

  return (
    <div style={{ textAlign: "center" }}>
      <canvas ref={canvasRef} />
    </div>
  );
};

export default HeatmapCanvas;
