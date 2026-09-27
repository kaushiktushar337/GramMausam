import { getPanchayats, getWeatherFromApi } from "./api";

export async function getComparisonData() {
  const panchayats = (await getPanchayats()).slice(0, 5);
  const results = await Promise.allSettled(
    panchayats.map(async (name) => ({
      name,
      ...(await getWeatherFromApi(name)),
    }))
  );

  return results
    .filter((result) => result.status === "fulfilled")
    .map(({ value }) => ({
      name: value.name,
      rainfall: value.rainfall,
      temp: `${value.maxTemp} / ${value.minTemp}`,
      humidity: value.humidity,
      risk: value.risk,
      confidence: value.confidence,
      confidenceValue: value.confidenceValue,
    }));
}