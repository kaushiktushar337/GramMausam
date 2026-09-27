import {
  CloudRain,
  Droplets,
  Navigation,
  Wind,
  ShieldCheck,
} from "lucide-react";

export default function PanchayatOverview({
  panchayat,
  weather,
}) {
  return (
    <div className="space-y-4">
      <section className="rounded-2xl border border-slate-200 bg-white p-5">
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-sm font-bold text-slate-800">
            Panchayat Overview - {panchayat}
          </h2>

          <button className="text-[11px] font-medium text-emerald-600 hover:underline">
            View All
          </button>
        </div>

        <div className="flex items-center gap-4">
          <CloudRain className="h-12 w-12 text-sky-500" />

          <div className="flex-1">
            <div className="text-3xl font-bold text-slate-900">
              {weather?.maxTemp ?? "--"}°C
            </div>

            <p className="text-xs text-slate-500">
              {weather?.condition ?? "Weather unavailable"}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-5 border-l border-slate-100 pl-5">
            <div>
              <p className="text-[10px] text-slate-400">
                Max
              </p>

              <p className="text-sm font-bold text-slate-800">
                {weather?.maxTemp ?? "--"}°C
              </p>
            </div>

            <div>
              <p className="text-[10px] text-slate-400">
                Min
              </p>

              <p className="text-sm font-bold text-slate-800">
                {weather?.minTemp ?? "--"}°C
              </p>
            </div>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-3 divide-x divide-slate-100 border-t border-slate-100 pt-5">
          <Metric
            icon={Droplets}
            label="Humidity"
            value={weather ? `${weather.humidity}%` : "--"}
          />

          <Metric
            icon={Wind}
            label="Wind Speed"
            value={weather ? `${weather.windSpeed} km/h` : "--"}
          />

          <Metric
            icon={Navigation}
            label="Wind Direction"
            value={weather?.windDirection ?? "--"}
          />
        </div>
      </section>

      <section className="rounded-2xl border border-emerald-100 bg-emerald-50/60 p-5">
        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-white p-2">
            <ShieldCheck className="h-5 w-5 text-emerald-600" />
          </div>

          <div className="flex-1">
            <p className="text-[10px] font-semibold uppercase tracking-wide text-emerald-700">
              Forecast Confidence
            </p>

            <p className="mt-1 text-sm font-bold text-slate-800">
              {weather?.confidence ?? "--"}
            </p>
          </div>
        </div>

        <div className="mt-4 h-2 overflow-hidden rounded-full bg-emerald-100">
          <div
            className="h-full rounded-full bg-emerald-500 transition-all"
            style={{
              width: `${weather?.confidenceValue ?? 0}%`,
            }}
          />
        </div>

        <p className="mt-2 text-[10px] text-slate-500">
          Confidence is based on current model conditions and
          historical performance.
        </p>
      </section>
    </div>
  );
}

function Metric({ icon: Icon, label, value }) {
  return (
    <div className="flex flex-col items-center text-center">
      <Icon className="mb-2 h-5 w-5 text-sky-500" />

      <p className="text-[10px] text-slate-400">
        {label}
      </p>

      <p className="mt-1 text-sm font-bold text-slate-800">
        {value}
      </p>
    </div>
  );
}