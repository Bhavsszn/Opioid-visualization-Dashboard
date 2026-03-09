import { NavLink, Outlet } from "react-router-dom";

const navItems = [
  { to: "/", label: "Overview" },
  { to: "/map", label: "Map" },
  { to: "/forecast", label: "Forecast" },
  { to: "/insights", label: "AI Insights" },
  { to: "/pipeline", label: "Pipeline" },
  { to: "/powerbi", label: "Power BI" },
];

export default function AppLayout() {
  return (
    <div className="dashboard-app">
      <aside className="sidebar">
        <div className="brand">Opioid AI Dashboard</div>
        <nav>
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <div className="content-column">
        <main className="content">
          <Outlet />
        </main>
        <footer className="footer">
          <p>© 2026 Bhavya Sharma</p>
          <p>
            Data sources: <a href="https://wonder.cdc.gov/mcd.html" target="_blank" rel="noreferrer">CDC WONDER</a> and <a href="https://www.census.gov/data.html" target="_blank" rel="noreferrer">U.S. Census Bureau</a>
          </p>
        </footer>
      </div>
    </div>
  );
}
