import { useEffect, useState } from "react";
import { motion } from "framer-motion";

import PanchayatSelector from "../components/PanchayatSelector";
import WeatherMap from "../components/WeatherMap";
import PanchayatOverview from "../components/PanchayatOverview";
import ForecastCard from "../components/ForecastCard";
import AdvisoryPanel from "../components/AdvisoryPanel";
import PanchayatComparison from "../components/PanchayatComparison";
import WeatherTrend from "../components/WeatherTrend";
import QuickLinks from "../components/QuickLinks";

import {
  getHealth,
  getWeatherFromApi,
  getForecastFromApi,
  getAdvisoryFromApi,
} from "../services/api";

import { getComparisonData } from "../services/dashboardService";

export default function Dashboard() {
  const [backendWeather, setBackendWeather] = useState(null);
  const [forecastResult, setForecastResult] = useState(null);
  const [advisoryResult, setAdvisoryResult] = useState(null);
  const [comparisonData, setComparisonData] = useState([]);

  const [selected, setSelected] = useState({
    state: "Uttar Pradesh",
    district: "Agra",
    block: "Achhnera",
    panchayat: "ABHAUDOPURA",
  });

  useEffect(() => {
    let cancelled = false;

    Promise.all([getHealth(), getComparisonData()])
      .then(([, comparisons]) => {
        if (cancelled) return;
        setComparisonData(comparisons);
      })
      .catch((error) => console.error("Dashboard data failed:", error));

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!selected.panchayat) return;

    getWeatherFromApi(selected.panchayat)
      .then((data) => {
        setBackendWeather(data);
      })
      .catch((error) => {
        console.error("Weather API failed:", error);
      });
  }, [selected.panchayat]);

  useEffect(() => {
    if (!selected.panchayat) return;

    getForecastFromApi(selected.panchayat)
      .then((data) => {
        setForecastResult({ panchayat: selected.panchayat, items: data });
      })
      .catch((error) => {
        console.error("Forecast API failed:", error);
      });
  }, [selected.panchayat]);

  useEffect(() => {
    const forecast = forecastResult?.panchayat === selected.panchayat
      ? forecastResult.items
      : [];
    const weather = backendWeather?.panchayat === selected.panchayat
      ? backendWeather
      : null;

    if (!weather || forecast.length === 0) {
      return;
    }

    const firstForecastDay = forecast[0];

    getAdvisoryFromApi({
      crop: "Wheat",
      growthStage: "Vegetative",
      rainfall: firstForecastDay.rainfall,
      rainProbability: firstForecastDay.rainProbability,
      temperature: weather.maxTemp,
      humidity: firstForecastDay.humidity,
      windSpeed: firstForecastDay.windSpeed,
    })
      .then((data) => {
        setAdvisoryResult({ panchayat: selected.panchayat, data });
      })
      .catch((error) => {
        console.error("Advisory API failed:", error);
      });
  }, [backendWeather, forecastResult, selected.panchayat]);

  const weather = backendWeather?.panchayat === selected.panchayat
    ? backendWeather
    : null;
  const advisory = advisoryResult?.panchayat === selected.panchayat
    ? advisoryResult.data
    : null;

  return (
    <main className="mx-auto w-full max-w-[1700px] p-4 sm:p-6 xl:p-8">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.45 }}
      >
        <PanchayatSelector
          key={selected.panchayat}
          value={selected.panchayat}
          onChange={(panchayat) =>
            setSelected((current) => ({ ...current, panchayat }))
          }
        />

        <div className="mt-4 grid gap-4 xl:grid-cols-[minmax(0,1fr)_350px]">
          <div className="space-y-4">
            <WeatherMap
              selectedPanchayat={selected.panchayat}
            />

            <div className="grid gap-4 lg:grid-cols-2">
              <PanchayatComparison data={comparisonData} />

              <WeatherTrend
                panchayat={selected.panchayat}
              />
            </div>
          </div>

          <div className="space-y-4">
            <PanchayatOverview
              panchayat={selected.panchayat}
              weather={weather}
            />

            <ForecastCard
              panchayat={selected.panchayat}
            />

            <AdvisoryPanel
              advisory={advisory}
            />

            <QuickLinks />
          </div>
        </div>

        <div className="mt-4 flex flex-wrap items-center justify-center gap-2 rounded-2xl border border-emerald-100 bg-emerald-50 px-5 py-4 text-[11px] font-medium text-emerald-700">
          <span>Better Weather Insights</span>
          <span>→</span>
          <span>Smarter Farming</span>
          <span>→</span>
          <span>Stronger Rural India</span>
        </div>
      </motion.div>
    </main>
  );
}