import { useEffect, useState } from "react";
import L from "leaflet";
import {
  Layers3,
  Minus,
  Navigation,
  Plus,
} from "lucide-react";
import {
  GeoJSON,
  MapContainer,
  TileLayer,
  useMap,
} from "react-leaflet";

import {
  getNearbyPanchayatsFromApi,
} from "../services/api";
import { formatRainfall } from "../services/rainfall";

const center = [25.44, 81.84];

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

  const [mapResult, setMapResult] = useState(null);

  useEffect(() => {
    let cancelled = false;

    if (!selectedPanchayat) {
      return undefined;
    }

    getNearbyPanchayatsFromApi(selectedPanchayat)
      .then((areas) => {
        if (!cancelled) {
          setMapResult({
            panchayat: selectedPanchayat,
            status: "success",
            areas,
          });
        }
      })
      .catch((error) => {
        console.error("Panchayat map data failed:", error);
        if (!cancelled) {
          setMapResult({
            panchayat: selectedPanchayat,
            status: "error",
          });
        }
      });

    return () => {
      cancelled = true;
    };
  }, [selectedPanchayat]);

  const currentMapResult = mapResult?.panchayat.toLowerCase()
    === selectedPanchayat?.toLowerCase()
    ? mapResult
    : null;
  const mapLoading = Boolean(selectedPanchayat && !currentMapResult);
  const mapError = currentMapResult?.status === "error"
    ? "Boundary unavailable for this Panchayat."
    : null;
  const areas = currentMapResult?.status === "success"
    ? currentMapResult.areas
    : null;

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 px-4 py-3">
        <div>
          <h2 className="text-sm font-bold text-slate-800">
            Panchayat Weather Map
          </h2>

          <p className="mt-0.5 text-[10px] text-slate-400">
            Selected: {selectedPanchayat}
          </p>
          <p className="mt-0.5 text-[10px] text-slate-400">
            {mapLoading ? "Loading nearby Panchayats..." : mapError || "Nearby Panchayat estimates"}
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

          {areas && (
            <>
              <GeoJSON
                key={selectedPanchayat}
                data={areas}
                style={(feature) => {
                  const isSelected = feature.properties.gpname.toLowerCase()
                    === selectedPanchayat.toLowerCase();
                  return {
                    color: isSelected ? "#0f172a" : "#ffffff",
                    weight: isSelected ? 3 : 1.5,
                    fillColor: getLayerColor(
                      activeLayer,
                      feature.properties.weather
                    ),
                    fillOpacity: isSelected ? 0.72 : 0.5,
                  };
                }}
                onEachFeature={(feature, layer) => {
                  const name = feature.properties.gpname;
                  const weather = feature.properties.weather;
                  layer.bindTooltip(
                    getWeatherTooltip(name, weather),
                    { sticky: true }
                  );
                  layer.on("click", () => onPanchayatSelect?.(name));
                }}
              />
              <FitBoundary boundary={areas} />
            </>
          )}

          <MapControls boundary={areas} />
        </MapContainer>
      </div>

      <MapLegend activeLayer={activeLayer} />
    </div>
  );
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

function FitBoundary({ boundary }) {
  const map = useMap();

  useEffect(() => {
    const bounds = L.geoJSON(boundary).getBounds();
    if (bounds.isValid()) {
      map.fitBounds(bounds, { padding: [32, 32] });
    }
  }, [boundary, map]);

  return null;
}

function MapControls({ boundary }) {
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
        onClick={() => {
          const bounds = boundary
            ? L.geoJSON(boundary).getBounds()
            : null;
          if (bounds?.isValid()) {
            map.fitBounds(bounds, { padding: [32, 32] });
          } else {
            map.setView(center, 11);
          }
        }}
        className="absolute bottom-4 right-4 z-[1000] rounded-full bg-white p-2 shadow-md"
        aria-label="Reset map view"
      >
        <Navigation className="h-4 w-4 text-slate-700" />
      </button>
    </>
  );
}

function getWeatherTooltip(name, weather) {
  const safeName = String(name).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[character]);

  return [
    `<strong>${safeName}</strong>`,
    `Rainfall data date: ${weather.date}`,
    `Rainfall: ${formatRainfall(weather.rainfall)} mm`,
    `Temperature estimate: min ${weather.minTemp}°C / max ${weather.maxTemp}°C`,
    `Humidity estimate: ${weather.humidity}%`,
    `Wind estimate: ${weather.windSpeed} km/h ${weather.windDirection}`,
    `Condition: ${weather.condition}`,
    `Risk: ${weather.risk}`,
  ].join("<br>");
}