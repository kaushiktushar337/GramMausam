import { useEffect, useState } from "react";
import {
  Bell,
  CalendarDays,
  Menu,
  Search,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import PanchayatSelector from "./PanchayatSelector";

export default function Header({ onMenuClick }) {
  const navigate = useNavigate();
  const [today, setToday] = useState(() => new Date());

  useEffect(() => {
    const interval = setInterval(() => setToday(new Date()), 60_000);
    return () => clearInterval(interval);
  }, []);

  const dateLabel = new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(today);
  const weekdayLabel = new Intl.DateTimeFormat("en-IN", {
    weekday: "long",
  }).format(today);

  return (
    <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/95 backdrop-blur">
      <div className="flex min-h-[72px] items-center gap-3 px-4 sm:px-6 xl:px-8">
        <button
          type="button"
          onClick={onMenuClick}
          className="rounded-xl p-2 text-slate-600 hover:bg-slate-100 lg:hidden"
          aria-label="Open navigation"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div className="flex items-center gap-2 lg:hidden">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-50">
            <span className="text-sm">🌱</span>
          </div>

          <span className="text-sm font-bold text-slate-900">
            GramMausam
          </span>
        </div>

        <div className="relative hidden min-w-0 max-w-2xl flex-1 md:block">
          <Search className="pointer-events-none absolute left-4 top-1/2 z-[60] h-4 w-4 -translate-y-1/2 text-slate-400" />
          <PanchayatSelector
            label={null}
            value=""
            placeholder="Search Panchayats..."
            inputClassName="bg-slate-50 py-3 pl-11 pr-4 focus:bg-white"
            onChange={(panchayat) =>
              navigate(`/panchayat-details?panchayat=${encodeURIComponent(panchayat)}`)
            }
          />
        </div>

        <button
          type="button"
          onClick={() => navigate("/alerts")}
          aria-label="Open alerts"
          title="Open alerts"
          className="relative ml-auto rounded-xl p-2.5 text-slate-600 hover:bg-slate-50"
        >
          <Bell className="h-5 w-5" />

          <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-red-500" />
        </button>

        <div className="hidden items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 sm:flex">
          <CalendarDays className="h-4 w-4 text-slate-500" />

          <div>
            <p className="text-xs font-semibold text-slate-700">
              {dateLabel}
            </p>

            <p className="text-[10px] text-slate-400">
              {weekdayLabel}
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}