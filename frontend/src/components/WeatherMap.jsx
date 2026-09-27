import { useEffect, useState } from "react";
import {
  Layers3,
  Minus,
  Navigation,
  Plus,
} from "lucide-react";
import {
  CircleMarker,
  MapContainer,
  Rectangle,
  TileLayer,
  Tooltip,
  useMap,
} from "react-leaflet";

import { getWeatherFromApi } from "../services/api";

const center = [25.44, 81.84];

const panchayatData = [
  {
    name: "Bara",
    bounds: [
      [25.48, 81.78],
      [25.53, 81.84],
    ],
  },
  {
    name: "Kareli",
    bounds: [
      [25.4, 81.76],
      [25.47, 81.82],
    ],
  },
  {
    name: "Soraon",
    bounds: [
      [25.44, 81.84],
      [25.5, 81.91],
    ],
  },
  {
    name: "Phaphamau",
    bounds: [
      [25.35, 81.82],
      [25.42, 81.9],
    ],
  },
  {
    name: "Jasra",
    bounds: [
      [25.35, 81.75],
      [25.41, 81.81],
    ],
  },
];

const layers = [
  "Rainfall",
  "Temperature",
  "Humidity",
  "Wind",
  "Risk",
];

export default function WeatherMap({
  selectedPanchayat,
  onPanchayatSelect,
}) {
  const [activeLayer, setActiveLayer] =
    useState("Rainfall");

  const [backendWeather, setBackendWeather] =
    useState({});

  useEffect(() => {
    let cancelled = false;

    async function loadWeather() {
      try {
        const names = [...new Set([
          ...panchayatData.map((item) => item.name),
          selectedPanchayat,
        ].filter(Boolean))];
        const results = await Promise.allSettled(
          names.map(async (name) => ({
            name,
            weather: await getWeatherFromApi(name),
          }))
        );

        if (cancelled) {
          return;
        }

        const weatherMap = {};

        results.forEach((result) => {
          if (result.status === "fulfilled") {
            weatherMap[result.value.name] = result.value.weather;
          }
        });

        setBackendWeather(weatherMap);

        console.log(
          "WeatherMap backend data:",
          weatherMap
        );
      } catch (error) {
        console.error(
          "WeatherMap API failed:",
          error
        );
      }
    }

    loadWeather();

    return () => {
      cancelled = true;
    };
  }, [selectedPanchayat]);

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 px-4 py-3">
        <div>
          <h2 className="text-sm font-bold text-slate-800">
            Panchayat Weather Map
          </h2>

          <p className="mt-0.5 text-[10px] text-slate-400">
            Live Panchayat estimates with illustrative boundaries
          </p>
        </div>

        <div className="flex max-w-full gap-1 overflow-x-auto">
          {layers.map((layer) => (
            <button
              key={layer}
              type="button"
              onClick={() => setActiveLayer(layer)}
              className={`whitespace-nowrap rounded-lg px-3 py-1.5 text-[10px] font-medium transition ${activeLayer === layer
                  ? "bg-emerald-700 text-white"
                  : "bg-slate-50 text-slate-600 hover:bg-slate-100"
                }`}
            >
              {layer}
            </button>
          ))}
        </div>
      </div>

      <div className="h-[420px] p-2 sm:h-[500px]">
        <MapContainer
          center={center}
          zoom={11}
          scrollWheelZoom
          zoomControl={false}
          className="h-full w-full"
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {panchayatData.map((item) => {
           
            const weather = backendWeather[item.name];
            if (!weather) {
              return null;
            }

            const isSelected =
              item.name === selectedPanchayat;

            const fillColor = getLayerColor(
              activeLayer,
              weather
            );

            return (
              <Rectangle
                key={item.name}
                bounds={item.bounds}
                eventHandlers={{
                  click: () => {
                    onPanchayatSelect?.(item.name);
                  },
                }}
                pathOptions={{
                  color: isSelected
                    ? "#0f172a"
                    : "#ffffff",
                  weight: isSelected ? 3 : 1,
                  fillColor,
                  fillOpacity: isSelected
                    ? 0.72
                    : 0.48,
                }}
              >
                <Tooltip direction="center">
                  <div className="text-center">
                    <strong>{item.name}</strong>

                    <br />

                    {getLayerValue(
                      activeLayer,
                      weather
                    )}

                    <br />

                    <span>
                      {weather.risk} risk
                    </span>
                  </div>
                </Tooltip>
              </Rectangle>
            );
          })}

          <CircleMarker
            center={center}
            radius={5}
            pathOptions={{
              color: "#ffffff",
              fillColor: "#0f766e",
              fillOpacity: 1,
              weight: 2,
            }}
          />

          <MapControls />
        </MapContainer>
      </div>

      <MapLegend activeLayer={activeLayer} />
    </div>
  );
}

function getLayerValue(layer, weather) {
  switch (layer) {
    case "Rainfall":
      return `${weather.rainfall} mm`;

    case "Temperature":
      return `${weather.maxTemp}°C`;

    case "Humidity":
      return `${weather.humidity}%`;

    case "Wind":
      return `${weather.windSpeed} km/h`;

    case "Risk":
      return `${weather.risk} Risk`;

    default:
      return "";
  }
}

function getLayerColor(layer, weather) {
  if (layer === "Rainfall") {
    if (weather.rainfall >= 30) {
      return "#f97316";
    }

    if (weather.rainfall >= 25) {
      return "#facc15";
    }

    if (weather.rainfall >= 20) {
      return "#22c55e";
    }

    return "#4ade80";
  }

  if (layer === "Temperature") {
    if (weather.maxTemp >= 35) {
      return "#ef4444";
    }

    if (weather.maxTemp >= 32) {
      return "#f97316";
    }

    return "#facc15";
  }

  if (layer === "Humidity") {
    if (weather.humidity >= 84) {
      return "#2563eb";
    }

    if (weather.humidity >= 80) {
      return "#38bdf8";
    }

    return "#7dd3fc";
  }

  if (layer === "Wind") {
    if (weather.windSpeed >= 15) {
      return "#dc2626";
    }

    if (weather.windSpeed >= 12) {
      return "#f59e0b";
    }

    return "#22c55e";
  }

  if (layer === "Risk") {
    if (weather.risk === "High") {
      return "#ef4444";
    }

    if (weather.risk === "Medium") {
      return "#f59e0b";
    }

    return "#22c55e";
  }

  return "#22c55e";
}

function MapLegend({ activeLayer }) {
  const legends = {
    Rainfall: ["5", "15", "25", "35", "40+"],
    Temperature: ["28", "30", "32", "34", "36+"],
    Humidity: ["60", "70", "80", "90", "95+"],
    Wind: ["5", "10", "15", "20", "25+"],
    Risk: ["Low", "Medium", "High"],
  };

  const values = legends[activeLayer];

  return (
    <div className="border-t border-slate-100 px-4 py-3">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-[11px] font-semibold text-slate-700">
            {activeLayer}
          </p>

          <div className="mt-2 flex items-center gap-1">
            {getLegendColors(activeLayer).map(
              (color) => (
                <span
                  key={color}
                  className="h-2.5 w-8 rounded-full"
                  style={{
                    backgroundColor: color,
                  }}
                />
              )
            )}
          </div>

          <div className="mt-1 flex justify-between text-[8px] text-slate-400">
            {values.map((value) => (
              <span key={value}>{value}</span>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2 text-[10px] text-slate-400">
          <span>Localized Layer</span>
          <Layers3 className="h-4 w-4" />
        </div>
      </div>
    </div>
  );
}

function getLegendColors(layer) {
  if (layer === "Risk") {
    return [
      "#22c55e",
      "#f59e0b",
      "#ef4444",
    ];
  }

  return [
    "#2563eb",
    "#22c55e",
    "#facc15",
    "#f97316",
    "#dc2626",
  ];
}

function MapControls() {
  const map = useMap();

  return (
    <>
      <div className="absolute left-3 top-3 z-[1000] flex flex-col overflow-hidden rounded-lg border border-slate-200 bg-white shadow-md">
        <button
          type="button"
          onClick={() => map.zoomIn()}
          className="p-2 hover:bg-slate-50"
          aria-label="Zoom in"
        >
          <Plus className="h-4 w-4" />
        </button>

        <button
          type="button"
          onClick={() => map.zoomOut()}
          className="border-t border-slate-100 p-2 hover:bg-slate-50"
          aria-label="Zoom out"
        >
          <Minus className="h-4 w-4" />
        </button>
      </div>

      <button
        type="button"
        onClick={() => map.setView(center, 11)}
        className="absolute bottom-4 right-4 z-[1000] rounded-full bg-white p-2 shadow-md"
        aria-label="Reset map view"
      >
        <Navigation className="h-4 w-4 text-slate-700" />
      </button>
    </>
  );
}