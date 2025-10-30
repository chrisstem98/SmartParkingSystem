import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import LiveView from "./pages/LiveView";

function Home() {
  return (
    <div className="p-6 text-center text-2xl">
       Welcome to <strong>Smart Parking Dashboard</strong>
      <p className="text-gray-500 mt-2"></p>
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
        <Route path="/stats" element={<div className="p-6 text-xl">Stats coming soon...</div>} />
        <Route path="/heatmap" element={<div className="p-6 text-xl">Heatmap coming soon...</div>} />
        <Route path="/reservations" element={<div className="p-6 text-xl"> Reservation demo coming soon...</div>} />
      </Routes>
    </Router>
  );
}
