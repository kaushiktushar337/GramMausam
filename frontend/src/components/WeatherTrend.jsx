import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  CartesianGrid,
  ComposedChart,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { getForecastFromApi } from "../services/api";

const parameters = [
  "Rainfall",
  "Temperature",
  "Humidity",
];

export default function WeatherTrend({ panchayat }) {
  const [activeParameter, setActiveParameter] =
    useState("Rainfall");

  const [forecastResult, setForecastResult] = useState(null);

  useEffect(() => {
    let cancelled = false;

    getForecastFromApi(panchayat)
      .then((data) => {
        if (!cancelled) setForecastResult({ panchayat, items: data });
      })
      .catch((error) => {
        console.error("WeatherTrend API failed:", error);
        if (!cancelled) setForecastResult({ panchayat, items: [] });
      });

    return () => {
      cancelled = true;
    };
  }, [panchayat]);

  const loading = forecastResult?.panchayat !== panchayat;

  const chartData = useMemo(() => {
    const forecast = forecastResult?.panchayat === panchayat
      ? forecastResult.items
      : [];
    return forecast.map((item) => ({
      date: item.date,
      rainfall: item.rainfall,
      probability: item.rainProbability,
      temperature: item.maxTemp,
      humidity: item.humidity,
    }));
  }, [forecastResult, panchayat]);

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5">
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
        <div>
          <h2 className="text-sm font-bold text-slate-800">
            Weather Trend ({panchayat})
          </h2>

          <p className="mt-1 text-[10px] text-slate-400">
            Forecast trend for the selected Panchayat
          </p>
        </div>

        <div className="flex gap-1">
          {parameters.map((parameter) => (
            <button
              key={parameter}
              type="button"
              onClick={() => setActiveParameter(parameter)}
              className={`rounded-lg px-3 py-1.5 text-[10px] font-medium transition ${
                activeParameter === parameter
                  ? "bg-emerald-700 text-white"
                  : "bg-slate-50 text-slate-500 hover:bg-slate-100"
              }`}
            >
              {parameter}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-5 h-[280px] w-full">
        {loading ? (
          <div className="flex h-full items-center justify-center text-xs text-slate-400">
            Loading weather trend...
          </div>
        ) : chartData.length === 0 ? (
          <div className="flex h-full items-center justify-center text-xs text-red-500">
            Weather trend unavailable.
          </div>
        ) : (
          <>
            {activeParameter === "Rainfall" && (
              <RainfallChart data={chartData} />
            )}

            {activeParameter === "Temperature" && (
              <TemperatureChart data={chartData} />
            )}

            {activeParameter === "Humidity" && (
              <HumidityChart data={chartData} />
            )}
          </>
        )}
      </div>
    </section>
  );
}

function RainfallChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <ComposedChart data={data}>
        <CartesianGrid
          strokeDasharray="3 3"
          vertical={false}
          stroke="#e2e8f0"
        />

        <XAxis
          dataKey="date"
          axisLine={false}
          tickLine={false}
          tick={{
            fontSize: 10,
            fill: "#64748b",
          }}
        />

        <YAxis
          yAxisId="rain"
          axisLine={false}
          tickLine={false}
          tick={{
            fontSize: 10,
            fill: "#64748b",
          }}
        />

        <YAxis
          yAxisId="probability"
          orientation="right"
          domain={[0, 100]}
          axisLine={false}
          tickLine={false}
          tick={{
            fontSize: 10,
            fill: "#64748b",
          }}
          tickFormatter={(value) => `${value}%`}
        />

        <Tooltip
          contentStyle={{
            borderRadius: "12px",
            border: "1px solid #e2e8f0",
            fontSize: "11px",
          }}
        />

        <Bar
          yAxisId="rain"
          dataKey="rainfall"
          name="Rainfall (mm)"
          barSize={28}
          fill="#10b981"
          radius={[5, 5, 0, 0]}
        />

        <Line
          yAxisId="probability"
          type="monotone"
          dataKey="probability"
          name="Rain Probability (%)"
          stroke="#0ea5e9"
          strokeWidth={2.5}
          dot={{ r: 3 }}
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
}

function TemperatureChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data}>
        <CartesianGrid
          strokeDasharray="3 3"
          vertical={false}
          stroke="#e2e8f0"
        />

        <XAxis
          dataKey="date"
          axisLine={false}
          tickLine={false}
          tick={{
            fontSize: 10,
            fill: "#64748b",
          }}
        />

        <YAxis
          unit="°C"
          axisLine={false}
          tickLine={false}
          tick={{
            fontSize: 10,
            fill: "#64748b",
          }}
        />

        <Tooltip
          formatter={(value) => [
            `${value}°C`,
            "Max Temperature",
          ]}
          contentStyle={{
            borderRadius: "12px",
            border: "1px solid #e2e8f0",
            fontSize: "11px",
          }}
        />

        <Line
          type="monotone"
          dataKey="temperature"
          name="Max Temperature"
          stroke="#f97316"
          strokeWidth={2.5}
          dot={{ r: 3 }}
          activeDot={{ r: 5 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

function HumidityChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data}>
        <CartesianGrid
          strokeDasharray="3 3"
          vertical={false}
          stroke="#e2e8f0"
        />

        <XAxis
          dataKey="date"
          axisLine={false}
          tickLine={false}
          tick={{
            fontSize: 10,
            fill: "#64748b",
          }}
        />

        <YAxis
          domain={[0, 100]}
          axisLine={false}
          tickLine={false}
          tick={{
            fontSize: 10,
            fill: "#64748b",
          }}
          tickFormatter={(value) => `${value}%`}
        />

        <Tooltip
          formatter={(value) => [
            `${value}%`,
            "Humidity",
          ]}
          contentStyle={{
            borderRadius: "12px",
            border: "1px solid #e2e8f0",
            fontSize: "11px",
          }}
        />

        <Line
          type="monotone"
          dataKey="humidity"
          name="Humidity"
          stroke="#0ea5e9"
          strokeWidth={2.5}
          dot={{ r: 3 }}
          activeDot={{ r: 5 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}