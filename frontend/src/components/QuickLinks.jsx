import { useState } from "react";
import {
  CalendarDays,
  ChevronRight,
  CircleHelp,
  Clock3,
  Droplets,
  CloudSun,
  X,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

const links = [
  {
    title: "View Detailed Forecast",
    icon: CloudSun,
    path: "/forecast",
  },
  {
    title: "Crop Calendar",
    icon: CalendarDays,
    path: "/forecast",
  },
  {
    title: "Soil Moisture",
    icon: Droplets,
    dialog: "soil",
  },
  {
    title: "Past Weather Data",
    icon: Clock3,
    path: "/historical",
  },
  {
    title: "Help & Support",
    icon: CircleHelp,
    dialog: "help",
  },
];

export default function QuickLinks() {
  const navigate = useNavigate();
  const [dialog, setDialog] = useState(null);

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5">
      <h2 className="mb-4 text-sm font-bold text-slate-800">
        Quick Links
      </h2>

      <div className="space-y-2">
        {links.map((item) => {
          const Icon = item.icon;

          return (
            <button
              key={item.title}
              type="button"
              onClick={() => item.path ? navigate(item.path) : setDialog(item.dialog)}
              className="flex w-full items-center gap-3 rounded-xl border border-slate-100 p-3 text-left transition hover:border-emerald-200 hover:bg-emerald-50/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
            >
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-sky-50">
                <Icon className="h-4 w-4 text-sky-600" />
              </span>

              <span className="flex-1 text-[11px] font-medium text-slate-600">
                {item.title}
              </span>

              <ChevronRight className="h-4 w-4 text-slate-400" />
            </button>
          );
        })}
      </div>

      {dialog && (
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/40 p-4"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) setDialog(null);
          }}
        >
          <section
            role="dialog"
            aria-modal="true"
            aria-labelledby="quick-link-dialog-title"
            className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-5 shadow-xl"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 id="quick-link-dialog-title" className="text-base font-bold text-slate-900">
                  {dialog === "soil" ? "Soil Moisture" : "Help & Support"}
                </h2>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  {dialog === "soil"
                    ? "A dedicated soil-moisture view is not available yet. You can inspect current Panchayat weather estimates on the map."
                    : "Choose a section for help with forecasts, historical weather, or weather alerts."}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setDialog(null)}
                aria-label="Close dialog"
                className="rounded-lg p-2 text-slate-500 hover:bg-slate-100"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="mt-5 flex flex-wrap justify-end gap-2">
              {(dialog === "soil"
                ? [{ label: "Open Map View", path: "/map" }]
                : [
                    { label: "Forecast & Advisory", path: "/forecast" },
                    { label: "Historical Data", path: "/historical" },
                    { label: "Alerts", path: "/alerts" },
                  ]
              ).map((action) => (
                <button
                  key={action.path}
                  type="button"
                  onClick={() => navigate(action.path)}
                  className="rounded-lg bg-emerald-700 px-3 py-2 text-xs font-semibold text-white transition hover:bg-emerald-800"
                >
                  {action.label}
                </button>
              ))}
            </div>
          </section>
        </div>
      )}
    </section>
  );
}