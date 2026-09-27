import {
  AlertTriangle,
  CheckCircle2,
  Leaf,
  Sprout,
} from "lucide-react";

export default function AdvisoryPanel({ advisory }) {
  if (!advisory) {
    return (
      <aside className="space-y-4">
        <section className="rounded-2xl border border-emerald-100 bg-emerald-50/60 p-5">
          <div className="flex items-center gap-2">
            <Leaf className="h-5 w-5 text-emerald-600" />

            <h2 className="text-sm font-bold text-emerald-800">
              Agricultural Advisory
            </h2>
          </div>

          <div className="mt-5 rounded-xl bg-white p-5 text-center text-xs text-slate-400">
            Loading advisory...
          </div>
        </section>
      </aside>
    );
  }

  return (
    <aside className="space-y-4">
      <section className="rounded-2xl border border-emerald-100 bg-emerald-50/60 p-5">
        <div className="flex items-center gap-2">
          <Leaf className="h-5 w-5 text-emerald-600" />

          <h2 className="text-sm font-bold text-emerald-800">
            Agricultural Advisory
          </h2>
        </div>

        <div className="mt-5 rounded-xl border border-slate-200 bg-white p-3">
          <label className="text-[10px] text-slate-500">
            Advisory Level
          </label>

          <div className="mt-1 flex items-center justify-between">
            <span className="text-sm font-semibold text-slate-800">
              {advisory.level}
            </span>

            <span
              className={`rounded-full px-2 py-1 text-[9px] font-semibold ${
                advisory.level === "High"
                  ? "bg-red-100 text-red-700"
                  : advisory.level === "Medium"
                    ? "bg-amber-100 text-amber-700"
                    : "bg-emerald-100 text-emerald-700"
              }`}
            >
              Attention
            </span>
          </div>
        </div>

        <div className="mt-4 rounded-xl border border-emerald-100 bg-white">
          <div className="border-b border-emerald-100 bg-emerald-50 px-4 py-3">
            <p className="text-[10px] font-bold uppercase tracking-wide text-emerald-800">
              Recommended Actions
            </p>
          </div>

          <div className="space-y-4 p-4">
            {advisory.actions.map((action) => (
              <div
                key={action.title}
                className="flex items-start gap-2"
              >
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" />

                <div>
                  <p className="text-[11px] font-semibold text-slate-700">
                    {action.title}
                  </p>

                  <p className="mt-1 text-[11px] leading-5 text-slate-600">
                    {action.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 p-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 shrink-0 text-amber-600" />

            <div>
              <p className="text-[11px] font-bold text-amber-800">
                Weather Risk
              </p>

              <p className="mt-1 text-[11px] leading-5 text-slate-600">
                {advisory.summary}
              </p>
            </div>
          </div>
        </div>

        <div className="mt-4 rounded-xl border border-emerald-100 bg-white p-4">
          <div className="flex items-center gap-3">
            <Sprout className="h-5 w-5 text-emerald-600" />

            <div>
              <p className="text-[10px] font-bold text-emerald-800">
                Advisory Details
              </p>

              <p className="mt-1 text-[11px] text-slate-600">
                Irrigation: {advisory.irrigation}
              </p>

              <p className="mt-1 text-[11px] text-slate-600">
                Field operations: {advisory.fieldOperations}
              </p>
            </div>
          </div>
        </div>
      </section>
    </aside>
  );
}