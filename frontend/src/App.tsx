import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import LiveView from "./pages/LiveView";
import Statistics from "./pages/Statistics";
import HeatmapPage from "./pages/HeatmapPage";
import AdminReservationsPage from "./pages/AdminReservationsPage";
function Home() {
  return (
    <div className="p-6 text-center text-2xl">
      Welcome to <strong>Smart Parking Dashboard</strong>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/live" element={<LiveView />} />
        <Route path="/stats" element={<Statistics />} />
        <Route path="/heatmap" element={<HeatmapPage />} />
        <Route path="/reservations" element={<AdminReservationsPage />} />
      </Routes>
    </Router>
  );
}
