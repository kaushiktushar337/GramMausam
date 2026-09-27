import {
  CheckCircle2,
  CloudRain,
  Droplets,
  Thermometer,
  Wind,
} from "lucide-react";

import { weatherByPanchayat } from "../data/mockData";
import { formatRainfall } from "./rainfall";

export function createAlerts() {
  const alerts = [];

  Object.entries(weatherByPanchayat).forEach(
    ([panchayat, weather]) => {
      if (weather.rainfall >= 25) {
        alerts.push({
          id: `${panchayat}-rain`,
          panchayat,
          priority:
            weather.rainfall >= 30
              ? "High"
              : "Medium",
          category: "Heavy Rainfall",
          title: `Heavy rainfall expected in ${panchayat}`,
          description:
            `${formatRainfall(weather.rainfall)} mm rainfall is currently estimated. ` +
            "Low-lying fields and drainage channels should be monitored.",
          action:
            "Review irrigation plans and check field drainage.",
          icon: CloudRain,
          time: "Today",
        });
      }

      if (weather.humidity >= 80) {
        alerts.push({
          id: `${panchayat}-humidity`,
          panchayat,
          priority: "Medium",
          category: "High Humidity",
          title: `High humidity in ${panchayat}`,
          description:
            `Current humidity is estimated at ${weather.humidity}%. ` +
            "Moist conditions can increase the suitability of some crop diseases.",
          action:
            "Increase crop scouting and monitor for disease symptoms.",
          icon: Droplets,
          time: "Today",
        });
      }

      if (weather.maxTemp >= 35) {
        alerts.push({
          id: `${panchayat}-heat`,
          panchayat,
          priority: "Medium",
          category: "Heat",
          title: `High daytime temperature in ${panchayat}`,
          description:
            `Maximum temperature may reach ${weather.maxTemp}°C.`,
          action:
            "Monitor crop moisture and heat-sensitive conditions.",
          icon: Thermometer,
          time: "Next 24h",
        });
      }

      if (weather.windSpeed >= 15) {
        alerts.push({
          id: `${panchayat}-wind`,
          panchayat,
          priority: "Medium",
          category: "Wind",
          title: `Strong wind conditions near ${panchayat}`,
          description:
            `Wind speed is estimated at ${weather.windSpeed} km/h from the ${weather.windDirection}.`,
          action:
            "Review wind-sensitive farm operations.",
          icon: Wind,
          time: "Next 24h",
        });
      }

      if (
        weather.rainfall < 20 &&
        weather.maxTemp < 35 &&
        weather.humidity < 80
      ) {
        alerts.push({
          id: `${panchayat}-normal`,
          panchayat,
          priority: "Low",
          category: "Normal Conditions",
          title: `No major weather risk in ${panchayat}`,
          description:
            "No major threshold-based weather alert has been triggered by the current prototype rules.",
          action:
            "Continue regular weather and crop monitoring.",
          icon: CheckCircle2,
          time: "Current",
        });
      }
    }
  );

  return alerts.sort((a, b) => {
    const priorityOrder = {
      High: 0,
      Medium: 1,
      Low: 2,
    };

    return (
      priorityOrder[a.priority] -
      priorityOrder[b.priority]
    );
  });
}