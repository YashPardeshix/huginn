import { NavLink } from "react-router-dom";

const navItems = [
  { path: "/", label: "RUNS" },
  { path: "/fix-comparison", label: "FIX COMPARISON" },
  { path: "/repositories", label: "REPOSITORIES" },
  { path: "/metrics", label: "METRICS" },
  { path: "/audit", label: "AUDIT" },
];

export default function NavBar() {
  return (
    <div className="border-b border-outline">
      <div className="flex items-center justify-between px-8 py-4 border-b border-outline">
        <div className="flex items-center gap-4">
          <span className="font-mono text-sm tracking-widest text-on-surface">
            HUGINN // V1.0
          </span>
        </div>
        <div className="flex items-center gap-4 font-mono text-xs text-on-surface-muted">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 bg-trustworthy inline-block" />
            SYS.OK
          </span>
        </div>
      </div>
      <div className="flex items-center gap-2 px-8">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `font-mono text-xs tracking-widest px-4 py-3 ${
                isActive
                  ? "text-on-surface bg-surface-mid"
                  : "text-on-surface-muted hover:text-on-surface"
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </div>
    </div>
  );
}
