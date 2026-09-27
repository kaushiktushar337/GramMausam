import { useEffect, useState } from "react";
import {
  AlertTriangle,
  CalendarDays,
  CheckCircle2,
  ChevronRight,
  CloudRain,
  Droplets,
  Leaf,
  ShieldCheck,
  Wind,
} from "lucide-react";

import { crops } from "../services/advisoryService";
import { getAdvisoryFromApi } from "../services/api";
import { formatRainfall } from "../services/rainfall";
import PanchayatSelector from "../components/PanchayatSelector";

import {
  getForecast,
} from "../services/weatherService";


export default function ForecastAdvisory() {
  const [panchayat, setPanchayat] = useState("ABHAUDOPURA");

  const [crop, setCrop] = useState("Wheat");

  const [stage, setStage] = useState(
    crops.Wheat.stages[1]
  );

  const [forecast, setForecast] = useState([]);
  const [advisoryResult, setAdvisoryResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function loadForecast() {
      if (!panchayat) return;

      try {
        setLoading(true);
        setError(null);

        const data = await getForecast(panchayat);

        if (!cancelled) {
          setForecast(data);
        }
      } catch (err) {
        console.error("Forecast API failed:", err);

        if (!cancelled) {
          setForecast([]);
          setError("Unable to load Panchayat forecast.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadForecast();

    return () => {
      cancelled = true;
    };
  }, [panchayat]);

  const stageOptions = crops[crop].stages;

  const today = forecast[0] || {
    rainfall: 0,
    rainProbability: 0,
    maxTemp: 0,
    humidity: 0,
    windSpeed: 0,
  };
  const advisoryKey = `${panchayat}|${crop}|${stage}|${today.date || ""}`;
  const advisory = advisoryResult?.key === advisoryKey
    ? advisoryResult.data
    : null;

  useEffect(() => {
    let cancelled = false;

    if (forecast.length === 0) return;

    const requestKey = advisoryKey;

    getAdvisoryFromApi({
      crop,
      growthStage: stage,
      rainfall: today.rainfall,
      rainProbability: today.rainProbability,
      temperature: today.maxTemp,
      humidity: today.humidity,
      windSpeed: today.windSpeed,
    })
      .then((data) => {
        if (!cancelled) setAdvisoryResult({ key: requestKey, data });
      })
      .catch((err) => {
        console.error("Advisory API failed:", err);
        if (!cancelled) setAdvisoryResult({ key: requestKey, data: null });
      });

    return () => {
      cancelled = true;
    };
  }, [advisoryKey, crop, stage, today.rainfall, today.rainProbability, today.maxTemp, today.humidity, today.windSpeed, forecast.length]);

  const handleCropChange = (value) => {
    setCrop(value);
    setStage(crops[value].stages[0]);
  };

  return (

    <main className="mx-auto w-full max-w-[1700px] p-4 sm:p-6 xl:p-8">
{loading && (
  <div className="mb-4 rounded-2xl border border-slate-200 bg-white p-4 text-center text-xs text-slate-400">
    Loading Panchayat forecast...
  </div>
)}

{error && (
  <div className="mb-4 rounded-2xl border border-red-200 bg-red-50 p-4 text-center text-xs text-red-600">
    {error}
  </div>
)}
      {/* Heading */}
      <div className="mb-5">
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <span>Dashboard</span>
          <span>/</span>
          <span className="font-semibold text-emerald-700">
            Forecast & Advisory
          </span>
        </div>

        <h1 className="mt-3 text-2xl font-bold tracking-tight text-slate-900">
          Forecast & Agricultural Advisory
        </h1>

        <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-500">
          View localized weather forecasts and translate expected
          weather conditions into crop-specific actions.
        </p>
      </div>

      {/* Filters */}
      <section className="rounded-2xl border border-slate-200 bg-white p-4">
        <div className="grid gap-3 md:grid-cols-3">
          <PanchayatSelector
            key={panchayat}
            value={panchayat}
            onChange={setPanchayat}
          />

          <SelectField
            label="Crop"
            value={crop}
            options={Object.keys(crops)}
            onChange={handleCropChange}
          />

          <SelectField
            label="Growth Stage"
            value={stage}
            options={stageOptions}
            onChange={setStage}
          />
        </div>
      </section>

      {/* Today summary */}
      <section className="mt-4 grid gap-4 xl:grid-cols-[1.4fr_1fr_1fr_1fr]">
        <div className="rounded-2xl border border-slate-200 bg-white p-5">
          <p className="text-[10px] uppercase tracking-wide text-slate-400">
            Today's Forecast
          </p>

          <div className="mt-4 flex items-center gap-4">
            <div className="rounded-2xl bg-sky-50 p-4">
              <CloudRain className="h-9 w-9 text-sky-500" />
            </div>

            <div>
              <p className="text-3xl font-bold text-slate-900">
                {today.maxTemp}°C
              </p>

              <p className="mt-1 text-xs text-slate-500">
                {today.condition}
              </p>

              <p className="mt-1 text-[10px] text-slate-400">
                {panchayat} Panchayat
              </p>
            </div>
          </div>
        </div>

        <SummaryCard
          icon={CloudRain}
          title="Rainfall"
          value={`${formatRainfall(today.rainfall)} mm`}
          note={`${today.rainProbability}% probability`}
        />

        <SummaryCard
          icon={Droplets}
          title="Humidity"
          value={`${today.humidity}%`}
          note="Current estimate"
        />

        <SummaryCard
          icon={Wind}
          title="Wind"
          value={`${today.windSpeed} km/h`}
          note="Expected today"
        />
      </section>

      {/* Forecast */}
      <section className="mt-4 rounded-2xl border border-slate-200 bg-white p-5">
        <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
          <div>
            <div className="flex items-center gap-2">
              <CalendarDays className="h-5 w-5 text-emerald-600" />

              <h2 className="text-sm font-bold text-slate-800">
                7-Day Panchayat Forecast
              </h2>
            </div>

            <p className="mt-1 text-[10px] text-slate-400">
              Forecast for {panchayat}
            </p>
          </div>

          <span className="rounded-full bg-emerald-50 px-3 py-1.5 text-[10px] font-semibold text-emerald-700">
            ML Downscaled Rainfall
          </span>
        </div>

        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-7">
          {forecast.map((item, index) => (
            <ForecastDay
              key={item.date}
              data={item}
              today={index === 0}
            />
          ))}
        </div>
      </section>

      {/* Advisory */}
      <div className="mt-4 grid gap-4 xl:grid-cols-[1.25fr_0.75fr]">
        <section className="rounded-2xl border border-emerald-100 bg-emerald-50/50 p-5">
          <div className="flex items-start gap-3">
            <div className="rounded-xl bg-white p-2.5">
              <Leaf className="h-5 w-5 text-emerald-600" />
            </div>

            <div>
              <p className="text-[10px] font-semibold uppercase tracking-wide text-emerald-700">
                Personalized Advisory
              </p>

              <h2 className="mt-1 text-lg font-bold text-slate-800">
                {crop} · {stage}
              </h2>

              <p className="mt-1 text-[11px] text-slate-500">
                Based on today's expected weather conditions.
              </p>
            </div>
          </div>

          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            {advisory?.actions?.map((action) => (
              <div
                key={action.title}
                className="rounded-xl border border-emerald-100 bg-white p-4"
              >
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" />

                  <div>
                    <p className="text-xs font-semibold text-slate-700">
                      {action.title}
                    </p>

                    <p className="mt-1 text-[10px] leading-5 text-slate-500">
                      {action.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-5">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-emerald-600" />

            <h2 className="text-sm font-bold text-slate-800">
              Advisory Summary
            </h2>
          </div>

          <div className="mt-5">
            <div
              className={`rounded-xl p-4 ${
                advisory?.level === "High"
                  ? "bg-red-50"
                  : advisory?.level === "Medium"
                    ? "bg-amber-50"
                    : "bg-emerald-50"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-700">
                  Advisory Priority
                </span>

                <span
                  className={`rounded-full px-2.5 py-1 text-[9px] font-semibold ${getPriorityClass(
                    advisory?.level || "Loading"
                  )}`}
                >
                  {advisory?.level || "Loading"}
                </span>
              </div>

              <p className="mt-3 text-[11px] leading-5 text-slate-600">
                {advisory?.summary || "Loading crop-specific guidance..."}
              </p>
            </div>
          </div>

          <div className="mt-4 space-y-3">
            <RiskIndicator
              label="Rainfall Risk"
              value={advisory?.rainfallRisk || "--"}
            />

            <RiskIndicator
              label="Heat Risk"
              value={advisory?.heatRisk || "--"}
            />

            <RiskIndicator
              label="Wind Risk"
              value={advisory?.windRisk || "--"}
            />

            <RiskIndicator
              label="Moisture Risk"
              value={advisory?.moistureRisk || "--"}
            />
          </div>
        </section>
      </div>

      {/* Decision panel */}
      <section className="mt-4 rounded-2xl border border-slate-200 bg-white p-5">
        <div className="flex items-start gap-3">
          <div className="rounded-xl bg-slate-50 p-2.5">
            <ShieldAlertIcon />
          </div>

          <div>
            <h2 className="text-sm font-bold text-slate-800">
              Decision Support
            </h2>

            <p className="mt-1 text-[10px] text-slate-400">
              Weather information relevant to the selected crop
              and growth stage.
            </p>
          </div>
        </div>

        <div className="mt-5 grid gap-3 md:grid-cols-3">
          <DecisionCard
            title="Irrigation"
            value={advisory?.irrigation || "Loading advisory..."}
          />

          <DecisionCard
            title="Field Operations"
            value={advisory?.fieldOperations || "Loading advisory..."}
          />

          <DecisionCard
            title="Crop Monitoring"
            value={advisory?.monitoring || "Loading advisory..."}
          />
        </div>
      </section>

      <p className="mt-4 text-center text-[10px] text-slate-400">
        Rainfall values are served from the real Panchayat-level
        downscaling output. Advisory actions use the current
        prototype crop-weather rules.
      </p>
    </main>
  );
}

function SelectField({
  label,
  value,
  options,
  onChange,
  disabled = false,
}) {
  return (
    <div>
      <label htmlFor={label.toLowerCase().replaceAll(" ", "-")} className="mb-1.5 block text-[10px] font-medium text-slate-500">
        {label}
      </label>

      <select
        id={label.toLowerCase().replaceAll(" ", "-")}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        disabled={disabled}
        className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-medium text-slate-800 outline-none focus:border-emerald-400 disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-400"
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

function SummaryCard({
  icon: Icon,
  title,
  value,
  note,
}) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[10px] text-slate-400">
            {title}
          </p>

          <p className="mt-2 text-2xl font-bold text-slate-900">
            {value}
          </p>

          <p className="mt-1 text-[10px] text-slate-400">
            {note}
          </p>
        </div>

        <div className="rounded-xl bg-sky-50 p-2.5">
          <Icon className="h-5 w-5 text-sky-500" />
        </div>
      </div>
    </section>
  );
}

function ForecastDay({ data, today }) {
  return (
    <div
      className={`rounded-xl border p-4 text-center ${
        today
          ? "border-emerald-200 bg-emerald-50/60"
          : "border-slate-100 bg-slate-50"
      }`}
    >
      <p className="text-[11px] font-bold text-slate-700">
        {data.day}
      </p>

      <p className="mt-0.5 text-[9px] text-slate-400">
        {data.date}
      </p>

      <CloudRain className="mx-auto my-3 h-7 w-7 text-sky-500" />

      <p className="text-sm font-bold text-slate-800">
        {formatRainfall(data.rainfall)} mm
      </p>

      <p className="mt-1 text-[9px] text-slate-400">
        Rainfall
      </p>

      <div className="mt-3 border-t border-slate-200 pt-3">
        <p className="text-xs font-semibold text-slate-700">
          {data.maxTemp}° / {data.minTemp}°
        </p>

        <p className="mt-1 text-[9px] text-slate-400">
          Temperature
        </p>
      </div>

      <div className="mt-3">
        <p className="text-xs font-semibold text-slate-700">
          {data.rainProbability}%
        </p>

        <p className="mt-1 text-[9px] text-slate-400">
          Rain probability
        </p>
      </div>
    </div>
  );
}

function RiskIndicator({ label, value }) {
  return (
    <div className="flex items-center justify-between border-b border-slate-100 pb-3">
      <span className="text-[11px] text-slate-600">
        {label}
      </span>

      <span
        className={`rounded-full px-2.5 py-1 text-[9px] font-semibold ${getPriorityClass(
          value
        )}`}
      >
        {value}
      </span>
    </div>
  );
}

function DecisionCard({ title, value }) {
  return (
    <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">
      <div className="flex items-center justify-between">
        <p className="text-xs font-semibold text-slate-700">
          {title}
        </p>

        <ChevronRight className="h-4 w-4 text-slate-400" />
      </div>

      <p className="mt-2 text-[11px] leading-5 text-slate-500">
        {value}
      </p>
    </div>
  );
}

function getPriorityClass(level) {
  if (level === "High") {
    return "bg-red-50 text-red-700";
  }

  if (level === "Medium") {
    return "bg-amber-50 text-amber-700";
  }

  return "bg-emerald-50 text-emerald-700";
}

function ShieldAlertIcon() {
  return (
    <AlertTriangle className="h-5 w-5 text-amber-500" />
  );
}

