export function formatRainfall(value) {
  const rainfall = Number(value);
  if (!Number.isFinite(rainfall)) return "--";

  return rainfall.toFixed(1).replace(/\.0$/, "");
}