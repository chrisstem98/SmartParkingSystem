import { Link, useLocation } from "react-router-dom";

export default function Navbar() {
  const { pathname } = useLocation();

  const linkStyle = (path: string) =>
    `px-4 py-2 rounded hover:bg-blue-200 transition ${
      pathname === path ? "bg-blue-500 text-white" : "text-blue-700"
    }`;

  return (
    <nav className="bg-blue-100 shadow flex justify-center gap-6 p-4">
      <Link to="/" className={linkStyle("/")}>Home</Link>
      <Link to="/live" className={linkStyle("/live")}>Live View</Link>
      <Link to="/stats" className={linkStyle("/stats")}>Stats</Link>
      <Link to="/heatmap" className={linkStyle("/heatmap")}>Heatmap</Link>
      <Link to="/reservations" className={linkStyle("/reservations")}>Reservations</Link>
    </nav>
  );
}
