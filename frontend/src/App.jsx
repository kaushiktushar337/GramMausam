import { useState } from "react";
import { Route, Routes } from "react-router-dom";

import Sidebar from "./components/Sidebar";
import Header from "./components/Header";

import Dashboard from "./pages/Dashboard";
import PanchayatDetails from "./pages/PanchayatDetails";
import MapView from "./pages/MapView";
import ForecastAdvisory from "./pages/ForecastAdvisory";
import HistoricalData from "./pages/HistoricalData";
import Alerts from "./pages/Alerts";
import Settings from "./pages/Settings";

export default function App() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const closeMobileMenu = () => {
    setMobileMenuOpen(false);
  };

  return (
    <div className="min-h-screen bg-[#f6faf9] text-slate-800">
      <div className="flex min-h-screen">
        <Sidebar />

        {mobileMenuOpen && (
          <>
            <div
              className="fixed inset-0 z-40 bg-slate-950/30 lg:hidden"
              onClick={closeMobileMenu}
            />

            <Sidebar
              mobile
              onClose={closeMobileMenu}
            />
          </>
        )}

        <div className="min-w-0 flex-1">
          <Header
            onMenuClick={() => setMobileMenuOpen(true)}
          />

          <Routes>
            <Route path="/" element={<Dashboard />} />

            <Route
              path="/map"
              element={<MapView />}
            />

            <Route
              path="/panchayat-details"
              element={<PanchayatDetails />}
            />

            <Route
              path="/forecast"
              element={<ForecastAdvisory />}
            />

            <Route
              path="/historical"
              element={<HistoricalData />}
            />

            <Route
              path="/alerts"
              element={<Alerts />}
            />

            <Route
              path="/settings"
              element={<Settings />}
            />
          </Routes>
        </div>
      </div>
    </div>
  );
}