import { useEffect, useState } from "react";
import {
  ArrowRight,
  Cloud,
  CloudRain,
  Sun,
} from "lucide-react";

import { getForecastFromApi } from "../services/api";
import { formatRainfall } from "../services/rainfall";

const icons = {
  rain: CloudRain,
  cloud: Cloud,
  sun: Sun,
};

function getWeatherIcon(condition) {
  const value = condition.toLowerCase();

  if (value.includes("rain")) {
    return "rain";
  }

  if (value.includes("cloud")) {
    return "cloud";
  }

  return "sun";
}

export default function ForecastCard({ panchayat }) {
  const [forecastResult, setForecastResult] = useState(null);

  useEffect(() => {
    let cancelled = false;

    getForecastFromApi(panchayat)
      .then((data) => {
        if (!cancelled) {
          setForecastResult({ panchayat, items: data.slice(0, 3) });
        }
      })
      .catch((error) => {
        console.error("ForecastCard API failed:", error);
        if (!cancelled) setForecastResult({ panchayat, items: [] });
      });

    return () => {
      cancelled = true;
    };
  }, [panchayat]);

  const loading = forecastResult?.panchayat !== panchayat;
  const forecast = loading ? [] : forecastResult.items;

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5">
      <div className="mb-5 flex items-center justify-between">
        <h2 className="text-sm font-bold text-slate-800">
          3-Day Forecast ({panchayat})
        </h2>

        <button
          type="button"
          className="flex items-center gap-1 text-[10px] font-semibold text-sky-600"
        >
          View Full Forecast
          <ArrowRight className="h-3 w-3" />
        </button>
      </div>

      {loading ? (
        <div className="py-10 text-center text-xs text-slate-400">
          Loading forecast...
        </div>
      ) : forecast.length === 0 ? (
        <div className="py-10 text-center text-xs text-red-500">
          Forecast data unavailable.
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-2">
          {forecast.map((item) => {
            const Icon =
              icons[getWeatherIcon(item.condition)];

            return (
              <div
                key={`${panchayat}-${item.date}`}
                className="rounded-xl border border-slate-100 bg-slate-50 p-3 text-center"
              >
                <p className="text-[11px] font-bold text-slate-700">
                  {item.day}
                </p>

                <p className="text-[9px] text-slate-400">
                  {item.date}
                </p>

                <Icon className="mx-auto my-3 h-7 w-7 text-sky-500" />

                <p className="text-xs font-bold text-slate-800">
                  {formatRainfall(item.rainfall)} mm
                </p>

                <p className="mt-1 text-[9px] text-slate-400">
                  Rainfall
                </p>

                <p className="mt-3 text-[10px] font-semibold text-slate-600">
                  {item.maxTemp}° / {item.minTemp}°
                </p>

                <p className="mt-1 text-[9px] text-slate-400">
                  Temperature
                </p>

                <span
                  className={`mt-3 inline-block rounded-full px-2 py-1 text-[8px] font-semibold ${
                    item.rainfall >= 25
                      ? "bg-red-100 text-red-700"
                      : item.rainfall >= 15
                        ? "bg-amber-100 text-amber-700"
                        : "bg-emerald-100 text-emerald-700"
                  }`}
                >
                  {item.rainfall >= 25
                    ? "High Risk"
                    : item.rainfall >= 15
                      ? "Medium Risk"
                      : "Low Risk"}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}