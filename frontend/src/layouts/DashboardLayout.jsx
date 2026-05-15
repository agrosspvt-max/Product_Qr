import { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  QrCode,
  ListOrdered,
  Boxes,
  Ruler,
  MessageSquare,
  KeyRound,
  Link2,
  LogOut,
  Menu,
  X,
} from "lucide-react";
import clsx from "clsx";
import { useAuth } from "../hooks/useAuth";

const NAV = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/generate", label: "Generate Codes", icon: QrCode },
  { to: "/batches", label: "Batches", icon: ListOrdered },
  { section: "Settings" },
  { to: "/products", label: "Products", icon: Boxes },
  { to: "/quantities", label: "Packaging", icon: Ruler },
  { to: "/presets", label: "WhatsApp Presets", icon: MessageSquare },
  { to: "/settings/zoho", label: "Zoho", icon: KeyRound },
  { to: "/settings/short-domain", label: "Short Domain", icon: Link2 },
];

export default function DashboardLayout() {
  const { user, logout } = useAuth();
  const nav = useNavigate();
  const [open, setOpen] = useState(false);

  function handleLogout() {
    logout();
    nav("/login", { replace: true });
  }

  return (
    <div className="min-h-screen flex bg-slate-50">
      {/* Sidebar */}
      <aside
        className={clsx(
          "fixed lg:static z-30 inset-y-0 left-0 w-64 bg-white border-r border-slate-200",
          "transform lg:translate-x-0 transition-transform",
          open ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="h-16 flex items-center gap-2 px-5 border-b border-slate-200">
          <div className="w-8 h-8 rounded-lg bg-brand-600 grid place-items-center text-white">
            <QrCode size={18} />
          </div>
          <span className="font-semibold text-slate-800">Product QR</span>
        </div>

        <nav className="p-3 space-y-1">
          {NAV.map((item, i) =>
            item.section ? (
              <div
                key={i}
                className="px-2 pt-4 pb-1 text-xs uppercase tracking-wider text-slate-400"
              >
                {item.section}
              </div>
            ) : (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                onClick={() => setOpen(false)}
                className={({ isActive }) =>
                  clsx(
                    "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium",
                    isActive
                      ? "bg-brand-50 text-brand-700"
                      : "text-slate-600 hover:bg-slate-100"
                  )
                }
              >
                <item.icon size={18} />
                {item.label}
              </NavLink>
            )
          )}
        </nav>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0 lg:ml-0">
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 lg:px-6 sticky top-0 z-20">
          <button
            className="lg:hidden btn-ghost"
            onClick={() => setOpen(!open)}
          >
            {open ? <X size={20} /> : <Menu size={20} />}
          </button>
          <div className="flex-1" />
          <div className="flex items-center gap-3">
            <div className="text-right hidden sm:block">
              <div className="text-sm font-medium text-slate-700">
                {user?.full_name || user?.email}
              </div>
              <div className="text-xs text-slate-400">{user?.email}</div>
            </div>
            <button className="btn-secondary" onClick={handleLogout}>
              <LogOut size={16} /> Logout
            </button>
          </div>
        </header>

        <main className="flex-1 p-4 lg:p-8">
          <Outlet />
        </main>
      </div>

      {/* Mobile backdrop */}
      {open && (
        <div
          className="fixed inset-0 bg-black/30 z-20 lg:hidden"
          onClick={() => setOpen(false)}
        />
      )}
    </div>
  );
}
