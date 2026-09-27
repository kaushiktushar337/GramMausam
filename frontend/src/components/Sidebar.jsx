import grammausamLogo from "../assets/grammausam-logo.png";
import {
  Bell,
  House,
  LandPlot,
  LineChart,
  Map,
  Settings,
  Sprout,
  CloudSun,
  X,
} from "lucide-react";
import { NavLink } from "react-router-dom";

const menuItems = [
  {
    name: "Dashboard",
    path: "/",
    icon: House,
  },
  {
    name: "Map View",
    path: "/map",
    icon: Map,
  },
  {
    name: "Panchayat Details",
    path: "/panchayat-details",
    icon: LandPlot,
  },
  {
    name: "Forecast & Advisory",
    path: "/forecast",
    icon: CloudSun,
  },
  {
    name: "Historical Data",
    path: "/historical",
    icon: LineChart,
  },
  {
    name: "Alerts",
    path: "/alerts",
    icon: Bell,
    badge: 3,
  },
  {
    name: "Settings",
    path: "/settings",
    icon: Settings,
  },
];

export default function Sidebar({ mobile = false, onClose }) {
  return (
    <aside
      className={
        mobile
          ? "fixed inset-y-0 left-0 z-50 flex w-[270px] flex-col border-r border-slate-200 bg-white shadow-xl lg:hidden"
          : "hidden min-h-screen w-[230px] shrink-0 flex-col border-r border-slate-200 bg-white lg:flex"
      }
    >
      <div className="border-b border-slate-100 px-5 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-50">
             <img
  src={grammausamLogo}
  alt="GramMausam"
  className="h-10 w-10 rounded-lg object-contain"
/>
            </div>

            <div>
              <h1 className="text-[19px] font-bold tracking-tight text-slate-900">
                GramMausam
              </h1>

              <p className="text-[10px] text-slate-500">
                Local Weather | Smart Farming
              </p>
            </div>
          </div>

          {mobile && (
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg p-2 text-slate-500 hover:bg-slate-100"
            >
              <X className="h-5 w-5" />
            </button>
          )}
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-5">
        {menuItems.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={mobile ? onClose : undefined}
              className={({ isActive }) =>
                [
                  "group flex items-center gap-3 rounded-xl px-4 py-3 text-sm transition-all",
                  isActive
                    ? "bg-emerald-50 font-semibold text-emerald-700"
                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-900",
                ].join(" ")
              }
            >
              <Icon className="h-[19px] w-[19px]" />

              <span className="flex-1">{item.name}</span>

              {item.badge && (
                <span className="flex h-5 min-w-5 items-center justify-center rounded-full bg-red-500 px-1.5 text-[10px] font-bold text-white">
                  {item.badge}
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      
    </aside>
  );
}