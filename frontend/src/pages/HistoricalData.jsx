import { useEffect, useState } from "react";
import {
  BarChart3,
  CalendarDays,
  CheckCircle2,
  CloudRain,
  Download,
  Info,
  LineChart as LineChartIcon,
  MapPin,
  Target,
} from "lucide-react";
import {
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { getHistoricalFromApi } from "../services/api";
import PanchayatSelector from "../components/PanchayatSelector";
import {
  getEvaluationMetrics,
  getRainEventMetrics,
} from "../services/historicalService";

const parameters = ["Rainfall"];

export default function HistoricalData() {
  const [panchayat, setPanchayat] = useState("ABHAUDOPURA");
  const [parameter, setParameter] =
    useState("Rainfall");
  const [period, setPeriod] = useState("7 Days");

  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadHistoricalData() {
      try {
        setLoading(true);

        if (!panchayat) {
          setChartData([]);
          return;
        }

        const data = await getHistoricalFromApi(
          panchayat,
          Number.parseInt(period, 10)
        );

        setChartData(data);

        console.log(
          "Historical data from backend:",
          data
        );
      } catch (error) {
        console.error(
          "Historical API failed:",
          error
        );

        setChartData([]);
      } finally {
        setLoading(false);
      }
    }

    loadHistoricalData();
  }, [panchayat, period]);

  const metrics = getEvaluationMetrics(parameter);
  const rainMetrics = getRainEventMetrics();

  const handleExport = () => {
    if (chartData.length === 0) return;

    const rows = [
      ["date", "observation_mm", "block_forecast_mm", "downscaled_mm"],
      ...chartData.map((item) => [
        item.date,
        item.observation,
        item.blockForecast,
        item.downscaled,
      ]),
    ];
    const csv = rows
      .map((row) =>
        row
          .map((value) => `"${String(value ?? "").replace(/"/g, '""')}"`)
          .join(",")
      )
      .join("\r\n");
    const blob = new Blob(["\uFEFF", csv], {
      type: "text/csv;charset=utf-8",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    const filename = `${panchayat.toLowerCase().replace(/[^a-z0-9]+/g, "-")}-historical-${period.toLowerCase().replace(/\s+/g, "-")}.csv`;

    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  };

  return (
    <main className="mx-auto w-full max-w-[1700px] p-4 sm:p-6 xl:p-8">
      {/* Heading */}
      <div className="mb-5">
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <span>Dashboard</span>
          <span>/</span>

          <span className="font-semibold text-emerald-700">
            Historical Data
          </span>
        </div>

        <h1 className="mt-3 text-2xl font-bold tracking-tight text-slate-900">
          Historical Weather Data
        </h1>

        <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-500">
          Review historical weather patterns and compare
          coarse block-level forecasts with localized
          Panchayat estimates.
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

          <Filter
            label="Parameter"
            value={parameter}
            options={parameters}
            onChange={setParameter}
          />

          <Filter
            label="Period"
            value={period}
            options={["3 Days", "7 Days", "30 Days"]}
            onChange={setPeriod}
          />
        </div>
      </section>

      {/* Location information */}
      <section className="mt-4 flex flex-wrap items-center gap-x-6 gap-y-3 rounded-2xl border border-slate-200 bg-white px-5 py-4">
        <LocationItem
          icon={MapPin}
          label="Panchayat"
          value={panchayat}
        />

        <LocationItem
          icon={CalendarDays}
          label="Period"
          value={period}
        />

        <div className="ml-auto flex items-center gap-2 rounded-full bg-amber-50 px-3 py-1.5">
          <Info className="h-3.5 w-3.5 text-amber-600" />

          <span className="text-[10px] font-semibold text-amber-700">
            Demonstration Data
          </span>
        </div>
      </section>

      {/* Chart */}
      <section className="mt-4 rounded-2xl border border-slate-200 bg-white p-5">
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
          <div>
            <div className="flex items-center gap-2">
              <LineChartIcon className="h-5 w-5 text-emerald-600" />

              <h2 className="text-sm font-bold text-slate-800">
                Forecast vs Observation
              </h2>
            </div>

            <p className="mt-1 text-[10px] text-slate-400">
              {parameter} comparison for {panchayat}
            </p>
          </div>

          <div className="flex rounded-xl bg-slate-50 p-1">
            {parameters.map((item) => (
              <button
                key={item}
                type="button"
                onClick={() => setParameter(item)}
                className={`rounded-lg px-3 py-1.5 text-[10px] font-medium transition ${parameter === item
                  ? "bg-white text-emerald-700 shadow-sm"
                  : "text-slate-500 hover:text-slate-700"
                  }`}
              >
                {item}
              </button>
            ))}
          </div>
        </div>

        <div className="mt-6 h-[330px] w-full">
          {loading ? (
            <div className="flex h-full items-center justify-center text-xs text-slate-400">
              Loading historical data...
            </div>
          ) : chartData.length === 0 ? (
            <div className="flex h-full items-center justify-center text-xs text-red-500">
              Historical data unavailable.
            </div>
          ) : (
            <ResponsiveContainer
              width="100%"
              height="100%"
            >
              <ComposedChart data={chartData}>
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
                  axisLine={false}
                  tickLine={false}
                  tick={{
                    fontSize: 10,
                    fill: "#64748b",
                  }}
                />

                <Tooltip
                  contentStyle={{
                    borderRadius: "12px",
                    border: "1px solid #e2e8f0",
                    fontSize: "11px",
                  }}
                />

                <Legend
                  wrapperStyle={{
                    fontSize: "10px",
                    paddingTop: "8px",
                  }}
                />

                <Line
                  type="monotone"
                  dataKey="observation"
                  name="Actual Observation"
                  stroke="#0f172a"
                  strokeWidth={2.5}
                  dot={{ r: 3 }}
                />

                <Line
                  type="monotone"
                  dataKey="blockForecast"
                  name="Block Forecast"
                  stroke="#f59e0b"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={false}
                />

                <Line
                  type="monotone"
                  dataKey="downscaled"
                  name="Downscaled Estimate"
                  stroke="#059669"
                  strokeWidth={2.5}
                  dot={{ r: 3 }}
                />
              </ComposedChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          <LegendCard
            title="Actual Observation"
            colorClass="bg-slate-900"
            text="Reference observation"
          />

          <LegendCard
            title="Block Forecast"
            colorClass="bg-amber-500"
            text="Coarse input"
          />

          <LegendCard
            title="Downscaled Estimate"
            colorClass="bg-emerald-600"
            text="Fine-resolution output"
          />
        </div>
      </section>

      {/* Evaluation cards */}
      <section className="mt-4">
        <div className="mb-3 flex items-center gap-2">
          <Target className="h-5 w-5 text-emerald-600" />

          <div>
            <h2 className="text-sm font-bold text-slate-800">
              Model Evaluation
            </h2>

            <p className="text-[10px] text-slate-400">
              Example validation metrics for the selected
              parameter.
            </p>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <MetricCard
            title="Block Forecast MAE"
            value={metrics.blockMae}
            description="Mean absolute error"
            icon={CloudRain}
            iconBg="bg-amber-50"
            iconColor="text-amber-600"
          />

          <MetricCard
            title="Downscaled MAE"
            value={metrics.downscaledMae}
            description="Mean absolute error"
            icon={CheckCircle2}
            iconBg="bg-emerald-50"
            iconColor="text-emerald-600"
          />

          <MetricCard
            title="Block Forecast RMSE"
            value={metrics.blockRmse}
            description="Root mean squared error"
            icon={BarChart3}
            iconBg="bg-slate-50"
            iconColor="text-slate-600"
          />

          <MetricCard
            title="Downscaled RMSE"
            value={metrics.downscaledRmse}
            description="Root mean squared error"
            icon={Target}
            iconBg="bg-sky-50"
            iconColor="text-sky-600"
          />
        </div>
      </section>

      {/* Comparison table */}
      <section className="mt-4 rounded-2xl border border-slate-200 bg-white p-5">
        <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
          <div>
            <h2 className="text-sm font-bold text-slate-800">
              Forecast Error Comparison
            </h2>

            <p className="mt-1 text-[10px] text-slate-400">
              Lower error indicates closer agreement with the
              observation.
            </p>
          </div>

          
        </div>

        <div className="mt-5 overflow-x-auto">
          <table className="w-full min-w-[650px]">
            <thead>
              <tr className="border-y border-slate-100 bg-slate-50 text-left">
                <th className="px-4 py-3 text-[10px] font-semibold text-slate-500">
                  Metric
                </th>

                <th className="px-4 py-3 text-[10px] font-semibold text-slate-500">
                  Block Forecast
                </th>

                <th className="px-4 py-3 text-[10px] font-semibold text-slate-500">
                  Downscaled Estimate
                </th>

                <th className="px-4 py-3 text-[10px] font-semibold text-slate-500">
                  Purpose
                </th>
              </tr>
            </thead>

            <tbody>
              <ComparisonRow
                metric="MAE"
                block={metrics.blockMae}
                downscaled={metrics.downscaledMae}
                purpose="Average absolute error"
              />

              <ComparisonRow
                metric="RMSE"
                block={metrics.blockRmse}
                downscaled={metrics.downscaledRmse}
                purpose="Penalizes larger errors"
              />

              <ComparisonRow
                metric="Spatial usefulness"
                block="Coarse"
                downscaled="Fine-resolution"
                purpose="Local decision support"
              />
            </tbody>
          </table>
        </div>
      </section>

      {/* Rain event metrics */}
      <section className="mt-4 grid gap-4 xl:grid-cols-[1fr_1fr]">
        <section className="rounded-2xl border border-slate-200 bg-white p-5">
          <div className="flex items-center gap-2">
            <CloudRain className="h-5 w-5 text-sky-500" />

            <div>
              <h2 className="text-sm font-bold text-slate-800">
                Rain Event Detection
              </h2>

              <p className="text-[10px] text-slate-400">
                Example classification metrics.
              </p>
            </div>
          </div>

          <div className="mt-5 overflow-hidden rounded-xl border border-slate-100">
            <table className="w-full">
              <thead>
                <tr className="bg-slate-50 text-left">
                  <th className="px-3 py-3 text-[9px] font-semibold text-slate-500">
                    Event
                  </th>

                  <th className="px-3 py-3 text-[9px] font-semibold text-slate-500">
                    Precision
                  </th>

                  <th className="px-3 py-3 text-[9px] font-semibold text-slate-500">
                    Recall
                  </th>

                  <th className="px-3 py-3 text-[9px] font-semibold text-slate-500">
                    F1
                  </th>
                </tr>
              </thead>

              <tbody>
                {rainMetrics.map((row) => (
                  <tr
                    key={row.label}
                    className="border-t border-slate-100"
                  >
                    <td className="px-3 py-3 text-[10px] font-medium text-slate-700">
                      {row.label}
                    </td>

                    <td className="px-3 py-3 text-[10px] text-slate-600">
                      {row.precision}
                    </td>

                    <td className="px-3 py-3 text-[10px] text-slate-600">
                      {row.recall}
                    </td>

                    <td className="px-3 py-3 text-[10px] text-slate-600">
                      {row.f1}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="rounded-2xl border border-emerald-100 bg-emerald-50/60 p-5">
          <div className="flex items-center gap-2">
            <Info className="h-5 w-5 text-emerald-600" />

            <h2 className="text-sm font-bold text-slate-800">
              Why Historical Validation Matters
            </h2>
          </div>

          <div className="mt-4 space-y-3">
            <InfoStep
              number="01"
              title="Use historical forecast data"
              text="Collect the original coarse weather forecast for past dates."
            />

            <InfoStep
              number="02"
              title="Compare with observations"
              text="Measure the error against observed weather conditions."
            />

            <InfoStep
              number="03"
              title="Test the downscaled output"
              text="Generate fine-resolution estimates and calculate the same metrics."
            />

            <InfoStep
              number="04"
              title="Measure improvement"
              text="Determine whether the downscaling layer actually improves local estimates."
            />
          </div>
        </section>
      </section>

      {/* Export */}
      <section className="mt-4 flex flex-col gap-3 rounded-2xl border border-slate-200 bg-white p-5 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-sm font-bold text-slate-800">
            Historical Dataset
          </h2>

          <p className="mt-1 text-[10px] text-slate-400">
            Download the selected historical observations and estimates as a CSV file.
          </p>
        </div>

        <button
          type="button"
          onClick={handleExport}
          disabled={loading || chartData.length === 0}
          className="flex items-center justify-center gap-2 rounded-xl bg-emerald-700 px-4 py-2.5 text-xs font-semibold text-white transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Download className="h-4 w-4" />
          Export Data
        </button>
      </section>

      
    </main>
  );
}

function Filter({
  label,
  value,
  options,
  onChange,
}) {
  return (
    <div>
      <label className="mb-1.5 block text-[10px] font-medium text-slate-500">
        {label}
      </label>

      <select
        value={value}
        onChange={(event) =>
          onChange(event.target.value)
        }
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

function LocationItem({
  icon: Icon,
  label,
  value,
}) {
  return (
    <div className="flex items-center gap-2">
      <Icon className="h-4 w-4 text-slate-400" />

      <div>
        <p className="text-[9px] uppercase tracking-wide text-slate-400">
          {label}
        </p>

        <p className="mt-0.5 text-xs font-semibold text-slate-700">
          {value}
        </p>
      </div>
    </div>
  );
}

function LegendCard({
  title,
  colorClass,
  text,
}) {
  return (
    <div className="flex items-center gap-3 rounded-xl bg-slate-50 p-3">
      <span
        className={`h-2.5 w-8 rounded-full ${colorClass}`}
      />

      <div>
        <p className="text-[10px] font-semibold text-slate-700">
          {title}
        </p>

        <p className="text-[9px] text-slate-400">
          {text}
        </p>
      </div>
    </div>
  );
}

function MetricCard({
  title,
  value,
  description,
  icon: Icon,
  iconBg,
  iconColor,
}) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-[10px] text-slate-400">
            {title}
          </p>

          <p className="mt-2 text-xl font-bold text-slate-900">
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

function ComparisonRow({
  metric,
  block,
  downscaled,
  purpose,
}) {
  return (
    <tr className="border-b border-slate-100 last:border-none">
      <td className="px-4 py-3 text-xs font-semibold text-slate-700">
        {metric}
      </td>

      <td className="px-4 py-3 text-xs text-slate-600">
        {block}
      </td>

      <td className="px-4 py-3 text-xs font-semibold text-emerald-700">
        {downscaled}
      </td>

      <td className="px-4 py-3 text-[10px] text-slate-500">
        {purpose}
      </td>
    </tr>
  );
}

function InfoStep({
  number,
  title,
  text,
}) {
  return (
    <div className="flex items-start gap-3 rounded-xl border border-emerald-100 bg-white p-3">
      <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-emerald-100 text-[9px] font-bold text-emerald-700">
        {number}
      </span>

      <div>
        <p className="text-[11px] font-semibold text-slate-700">
          {title}
        </p>

        <p className="mt-1 text-[10px] leading-5 text-slate-500">
          {text}
        </p>
      </div>
    </div>
  );
}