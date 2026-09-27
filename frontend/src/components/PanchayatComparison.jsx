import { BarChart3 } from "lucide-react";
import { formatRainfall } from "../services/rainfall";

export default function PanchayatComparison({
  data,
}) {

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5">
      <div className="mb-4 flex items-center gap-2">
        <BarChart3 className="h-5 w-5 text-emerald-600" />

        <h2 className="text-sm font-bold text-slate-800">
          Panchayat Comparison
        </h2>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[650px] text-left">
          <thead>
            <tr className="border-y border-slate-100 bg-slate-50">
              <th className="px-3 py-3 text-[10px] font-semibold text-slate-500">
                Panchayat
              </th>
              <th className="px-3 py-3 text-[10px] font-semibold text-slate-500">
                Rainfall (mm)
              </th>
              <th className="px-3 py-3 text-[10px] font-semibold text-slate-500">
                Temp (°C)
              </th>
              <th className="px-3 py-3 text-[10px] font-semibold text-slate-500">
                Humidity (%)
              </th>
              <th className="px-3 py-3 text-[10px] font-semibold text-slate-500">
                Risk
              </th>
              <th className="px-3 py-3 text-[10px] font-semibold text-slate-500">
                Confidence
              </th>
            </tr>
          </thead>

          <tbody>
            {data.map((row) => (
              <tr
                key={row.name}
                className="border-b border-slate-100 last:border-0"
              >
                <td className="px-3 py-3 text-xs font-semibold text-slate-700">
                  {row.name}
                </td>

                <td className="px-3 py-3 text-xs text-slate-600">
                  {formatRainfall(row.rainfall)}
                </td>

                <td className="px-3 py-3 text-xs text-slate-600">
                  {row.temp}
                </td>

                <td className="px-3 py-3 text-xs text-slate-600">
                  {row.humidity}
                </td>

                <td className="px-3 py-3">
                  <RiskBadge risk={row.risk} />
                </td>

                <td className="px-3 py-3">
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-16 overflow-hidden rounded-full bg-slate-100">
                      <div
                        className="h-full rounded-full bg-sky-500"
                        style={{
                          width: `${row.confidenceValue}%`,
                        }}
                      />
                    </div>

                    <span className="text-[10px] text-slate-500">
                      {row.confidence}
                    </span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function RiskBadge({ risk }) {
  const classes = {
    Low: "bg-emerald-50 text-emerald-700",
    Medium: "bg-amber-50 text-amber-700",
    High: "bg-red-50 text-red-700",
  };

  const dots = {
    Low: "bg-emerald-500",
    Medium: "bg-amber-400",
    High: "bg-red-500",
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2 py-1 text-[9px] font-semibold ${classes[risk]}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${dots[risk]}`} />
      {risk}
    </span>
  );
}