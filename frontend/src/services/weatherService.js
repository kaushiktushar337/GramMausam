import {
  getWeatherFromApi,
  getForecastFromApi,
  getPanchayats as getPanchayatNamesFromApi,
} from "./api";

export async function getWeather(panchayat) {
  return getWeatherFromApi(panchayat);
}

export async function getForecast(panchayat) {
  return getForecastFromApi(panchayat);
}

export async function getPanchayats() {
  return getPanchayatNamesFromApi();
}