import { MapPin } from "lucide-react";

export default function LocationSelector({
  selected,
  setSelected,
  panchayats,
  disabled,
}) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-3">
      <Selector
        label="Panchayat"
        value={selected.panchayat}
        options={panchayats}
        disabled={disabled}
        onChange={(value) =>
          setSelected({
            ...selected,
            panchayat: value,
          })
        }
      />
    </section>
  );
}

function Selector({
  label,
  value,
  options,
  onChange,
  disabled,
}) {
  return (
    <div>
      <label className="mb-1.5 flex items-center gap-1 text-[11px] font-medium text-slate-500">
        {label === "Panchayat" && (
          <MapPin className="h-3 w-3" />
        )}

        {label}
      </label>

      <select
        value={value}
        disabled={disabled || options.length === 0}
        onChange={(e) => onChange(e.target.value)}
        className="w-full cursor-pointer rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-medium text-slate-800 outline-none transition focus:border-emerald-400"
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