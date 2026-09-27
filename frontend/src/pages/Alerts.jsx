import { useEffect, useState } from "react";
import {
  AlertTriangle,
  Bell,
  Check,
  CheckCircle2,
  CloudRain,
  Droplets,
  Filter,
  MapPin,
  ShieldAlert,
  Thermometer,
  Wind,
} from "lucide-react";

import { getAlertsFromApi } from "../services/api";

const priorityOptions = ["All", "High", "Medium", "Low"];

export default function Alerts() {
  const [selectedPanchayat, setSelectedPanchayat] =
    useState("All");

  const [priority, setPriority] = useState("All");

  const [alerts, setAlerts] = useState([]);

  const [readAlerts, setReadAlerts] = useState([]);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadAlerts() {
      try {
        setLoading(true);
        setError(null);

        const data = await getAlertsFromApi();

        setAlerts(data);

        console.log("Alerts from backend:", data);
      } catch (error) {
        console.error("Alerts API failed:", error);
        setError("Unable to load weather alerts.");
      } finally {
        setLoading(false);
      }
    }

    loadAlerts();
  }, []);

  const panchayatOptions = [
    "All",
    ...new Set(
      alerts.map((alert) => alert.panchayat)
    ),
  ];

  const filteredAlerts = alerts.filter((alert) => {
    const matchesPanchayat =
      selectedPanchayat === "All" ||
      alert.panchayat === selectedPanchayat;

    const matchesPriority =
      priority === "All" ||
      alert.priority === priority;

    return matchesPanchayat && matchesPriority;
  });

  const unreadCount = alerts.filter(
    (alert) => !readAlerts.includes(alert.id)
  ).length;

  const markAsRead = (id) => {
    setReadAlerts((current) => {
      if (current.includes(id)) {
        return current;
      }

      return [...current, id];
    });
  };

  const markAllAsRead = () => {
    setReadAlerts(alerts.map((alert) => alert.id));
  };

  return (
    <main className="mx-auto w-full max-w-[1700px] p-4 sm:p-6 xl:p-8">
      {/* Heading */}
      <div className="mb-5">
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <span>Dashboard</span>
          <span>/</span>
          <span className="font-semibold text-emerald-700">
            Alerts
          </span>
        </div>

        <div className="mt-3 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">
              Rainfall Alerts
            </h1>

            
          </div>

          <div className="flex items-center gap-2">
            <span className="flex h-9 min-w-9 items-center justify-center rounded-full bg-red-50 px-3 text-xs font-bold text-red-600">
              {unreadCount}
            </span>

            <span className="text-[11px] text-slate-500">
              Unread
            </span>
          </div>
        </div>
      </div>

      {/* Filters */}
      <section className="rounded-2xl border border-slate-200 bg-white p-4">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div className="grid gap-3 sm:grid-cols-2">
            <FilterField
              label="Panchayat"
              value={selectedPanchayat}
              options={panchayatOptions}
              onChange={setSelectedPanchayat}
            />

            <FilterField
              label="Priority"
              value={priority}
              options={priorityOptions}
              onChange={setPriority}
            />
          </div>

          <button
            type="button"
            onClick={markAllAsRead}
            className="flex items-center justify-center gap-2 rounded-xl border border-slate-200 px-4 py-2.5 text-xs font-semibold text-slate-600 transition hover:bg-slate-50"
          >
            <Check className="h-4 w-4" />
            Mark all as read
          </button>
        </div>
      </section>

      {/* Summary cards */}
      <section className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <AlertSummaryCard
          icon={Bell}
          title="Total Alerts"
          value={alerts.length}
          description="Date-stamped model output"
          iconBg="bg-slate-50"
          iconColor="text-slate-600"
        />

        <AlertSummaryCard
          icon={ShieldAlert}
          title="High Priority"
          value={
            alerts.filter(
              (alert) => alert.priority === "High"
            ).length
          }
          description="Requires closer attention"
          iconBg="bg-red-50"
          iconColor="text-red-600"
        />

        <AlertSummaryCard
          icon={AlertTriangle}
          title="Medium Priority"
          value={
            alerts.filter(
              (alert) => alert.priority === "Medium"
            ).length
          }
          description="Monitor local conditions"
          iconBg="bg-amber-50"
          iconColor="text-amber-600"
        />

        <AlertSummaryCard
          icon={CheckCircle2}
          title="Low Priority"
          value={
            alerts.filter(
              (alert) => alert.priority === "Low"
            ).length
          }
          description="Informational"
          iconBg="bg-emerald-50"
          iconColor="text-emerald-600"
        />
      </section>

      {/* Alert list */}
      <section className="mt-4 rounded-2xl border border-slate-200 bg-white">
        <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-emerald-600" />

            <div>
              <h2 className="text-sm font-bold text-slate-800">
                Alert Feed
              </h2>

              <p className="mt-0.5 text-[10px] text-slate-400">
                {filteredAlerts.length} alert
                {filteredAlerts.length === 1 ? "" : "s"} shown
              </p>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="flex min-h-[260px] items-center justify-center text-xs text-slate-400">
            Loading alerts...
          </div>
        ) : error ? (
          <div className="flex min-h-[260px] items-center justify-center px-5 text-center">
            <p className="text-xs text-red-500">
              {error}
            </p>
          </div>
        ) : filteredAlerts.length === 0 ? (
          <EmptyAlerts />
        ) : (
          <div className="divide-y divide-slate-100">
            {filteredAlerts.map((alert) => {
              const isRead = readAlerts.includes(alert.id);

              return (
                <AlertItem
                  key={alert.id}
                  alert={alert}
                  isRead={isRead}
                  onMarkRead={markAsRead}
                />
              );
            })}
          </div>
        )}
      </section>

      {/* Alert logic */}
      <section className="mt-4 grid gap-4 xl:grid-cols-[1fr_1fr]">
        <section className="rounded-2xl border border-slate-200 bg-white p-5">
          <div className="flex items-center gap-2">
            <ShieldAlert className="h-5 w-5 text-emerald-600" />

            <div>
              <h2 className="text-sm font-bold text-slate-800">
                Backend Alert Rule
              </h2>

              <p className="mt-1 text-[10px] text-slate-400">
                Based on rainfall prediction output
              </p>
            </div>
          </div>

          <div className="mt-5 space-y-3">
            <LogicRow
              condition="Predicted rainfall ≥ 25 mm"
              result="Heavy rainfall alert"
            />

            <LogicRow
              condition="Predicted rainfall ≥ 30 mm"
              result="High priority"
            />
          </div>
        </section>

        <section className="rounded-2xl border border-emerald-100 bg-emerald-50/60 p-5">
          <div className="flex items-center gap-2">
            <CloudRain className="h-5 w-5 text-sky-500" />

            <h2 className="text-sm font-bold text-slate-800">
              Data Availability
            </h2>
          </div>

          <div className="mt-4 space-y-3">
            <FlowRow
              number="01"
              text="Alerts use the latest date available in the Panchayat rainfall dataset."
            />

            <FlowRow
              number="02"
              text="The prediction date is included with each alert."
            />

            <FlowRow
              number="03"
              text="The source dataset currently provides rainfall predictions only."
            />

            <FlowRow
              number="04"
              text="Temperature, humidity and wind alerts are omitted until backend data is available."
            />
          </div>
        </section>
      </section>

      <p className="mt-4 text-center text-[10px] text-slate-400">
        Alerts are based on model rainfall predictions, not live observations. Check local conditions before acting.
      </p>
    </main>
  );
}

const alertIcons = {
  "Heavy Rainfall": CloudRain,
  "High Humidity": Droplets,
  Heat: Thermometer,
  Wind,
};

function AlertItem({
  alert,
  isRead,
  onMarkRead,
}) {
  const Icon = alertIcons[alert.category] || AlertTriangle;

  return (
    <div
      className={`px-5 py-5 transition ${
        isRead ? "bg-white" : "bg-emerald-50/30"
      }`}
    >
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start">
        <div
          className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${getIconBg(
            alert.priority
          )}`}
        >
          <Icon
            className={`h-5 w-5 ${getIconColor(
              alert.priority
            )}`}
          />
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="text-sm font-bold text-slate-800">
              {alert.title}
            </h3>

            {!isRead && (
              <span className="h-2 w-2 rounded-full bg-emerald-500" />
            )}
          </div>

          <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1">
            <span className="flex items-center gap-1 text-[9px] text-slate-400">
              <MapPin className="h-3 w-3" />
              {alert.panchayat}
            </span>

            <span className="text-[9px] text-slate-300">
              |
            </span>

            <span className="text-[9px] text-slate-400">
              {alert.category}
            </span>

            <span className="text-[9px] text-slate-300">
              |
            </span>

            <span className="text-[9px] text-slate-400">
              {alert.time}
            </span>
          </div>

          <p className="mt-3 max-w-3xl text-[11px] leading-5 text-slate-500">
            {alert.description}
          </p>

          <div className="mt-3 rounded-xl border border-slate-100 bg-white p-3">
            <p className="text-[9px] font-semibold uppercase tracking-wide text-emerald-700">
              Suggested Action
            </p>

            <p className="mt-1 text-[10px] leading-5 text-slate-600">
              {alert.action}
            </p>
          </div>
        </div>

        <div className="flex shrink-0 items-center justify-between gap-3 sm:flex-col sm:items-end">
          <span
            className={`rounded-full px-2.5 py-1 text-[9px] font-semibold ${getPriorityClass(
              alert.priority
            )}`}
          >
            {alert.priority}
          </span>

          {!isRead && (
            <button
              type="button"
              onClick={() => onMarkRead(alert.id)}
              className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-[9px] font-semibold text-slate-500 hover:bg-slate-50"
            >
              <Check className="h-3 w-3" />
              Mark read
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function AlertSummaryCard({
  icon: Icon,
  title,
  value,
  description,
  iconBg,
  iconColor,
}) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-4">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[10px] text-slate-400">
            {title}
          </p>

          <p className="mt-2 text-2xl font-bold text-slate-900">
            {value}
          </p>

          <p className="mt-1 text-[9px] text-slate-400">
            {description}
          </p>
        </div>

        <div className={`rounded-xl p-2.5 ${iconBg}`}>
          <Icon className={`h-5 w-5 ${iconColor}`} />
        </div>
      </div>
    </section>
  );
}

function FilterField({
  label,
  value,
  options,
  onChange,
}) {
  return (
    <div className="min-w-0 sm:w-56">
      <label className="mb-1.5 block text-[10px] font-medium text-slate-500">
        {label}
      </label>

      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-medium text-slate-800 outline-none focus:border-emerald-400"
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </div>
  );
}

function LogicRow({
  condition,
  result,
}) {
  return (
    <div className="flex flex-col gap-2 rounded-xl border border-slate-100 bg-slate-50 p-3 sm:flex-row sm:items-center sm:justify-between">
      <span className="text-[10px] font-medium text-slate-600">
        {condition}
      </span>

      <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-[9px] font-semibold text-emerald-700">
        {result}
      </span>
    </div>
  );
}

function FlowRow({
  number,
  text,
}) {
  return (
    <div className="flex items-start gap-3 rounded-xl border border-emerald-100 bg-white p-3">
      <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-emerald-100 text-[9px] font-bold text-emerald-700">
        {number}
      </span>

      <p className="text-[10px] leading-5 text-slate-500">
        {text}
      </p>
    </div>
  );
}

function EmptyAlerts() {
  return (
    <div className="flex min-h-[260px] flex-col items-center justify-center px-5 text-center">
      <div className="rounded-2xl bg-emerald-50 p-4">
        <CheckCircle2 className="h-8 w-8 text-emerald-600" />
      </div>

      <h3 className="mt-4 text-sm font-bold text-slate-800">
        No alerts found
      </h3>

      <p className="mt-1 max-w-sm text-[11px] leading-5 text-slate-500">
        No alerts match the current Panchayat and priority
        filters.
      </p>
    </div>
  );
}

function getPriorityClass(priority) {
  if (priority === "High") {
    return "bg-red-50 text-red-700";
  }

  if (priority === "Medium") {
    return "bg-amber-50 text-amber-700";
  }

  return "bg-emerald-50 text-emerald-700";
}

function getIconBg(priority) {
  if (priority === "High") {
    return "bg-red-50";
  }

  if (priority === "Medium") {
    return "bg-amber-50";
  }

  return "bg-emerald-50";
}

function getIconColor(priority) {
  if (priority === "High") {
    return "text-red-600";
  }

  if (priority === "Medium") {
    return "text-amber-600";
  }

  return "text-emerald-600";
}