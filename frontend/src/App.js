import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LiveView from "./pages/LiveView";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/live" element={<LiveView />} />
        <Route path="/" element={<div className="p-6 text-2xl">Welcome to Smart Parking Dashboard</div>} />
      </Routes>
    </Router>
  );
}

export default App;
