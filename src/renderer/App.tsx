/**
 * App - Main Application Entry Point
 * ===================================
 * Root component that handles:
 * - First-run setup wizard detection and display
 * - Main application routing
 * - Global state initialization
 */

import React, { useState, useEffect } from 'react';
import { HashRouter, Routes, Route, Navigate } from 'react-router-dom';
import { SetupWizard } from './components/setup';
// Import pages when they're available
// import { Dashboard } from './pages/Dashboard';
// import { Analysis } from './pages/Analysis';
// import { Settings } from './pages/Settings';

// Placeholder components until real pages are implemented
function PlaceholderPage({ title }: { title: string }) {
  return (
    <div className="flex-1 flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          {title}
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Esta página está en desarrollo.
        </p>
      </div>
    </div>
  );
}

// Minimal sidebar for navigation
function Sidebar() {
  return (
    <aside className="w-64 bg-gray-800 text-white p-4">
      <div className="mb-8">
        <h1 className="text-xl font-bold">AI Tourism Analyzer</h1>
        <p className="text-xs text-gray-400">Opinion Analysis Tool</p>
      </div>
      <nav className="space-y-2">
        <a
          href="#/"
          className="block px-4 py-2 rounded hover:bg-gray-700 transition-colors"
        >
          📊 Dashboard
        </a>
        <a
          href="#/analysis"
          className="block px-4 py-2 rounded hover:bg-gray-700 transition-colors"
        >
          🔬 Análisis
        </a>
        <a
          href="#/settings"
          className="block px-4 py-2 rounded hover:bg-gray-700 transition-colors"
        >
          ⚙️ Configuración
        </a>
      </nav>
    </aside>
  );
}

export function App() {
  const [isFirstRun, setIsFirstRun] = useState<boolean | null>(null);
  const [setupComplete, setSetupComplete] = useState(false);

  useEffect(() => {
    // Check if first run on app start
    window.electronAPI.setup.isFirstRun().then((firstRun) => {
      setIsFirstRun(firstRun);
      // If not first run, setup is already complete
      if (!firstRun) {
        setSetupComplete(true);
      }
    }).catch((error) => {
      console.error('Failed to check first run status:', error);
      // Assume not first run on error
      setIsFirstRun(false);
      setSetupComplete(true);
    });
  }, []);

  // Loading state while checking first-run status
  if (isFirstRun === null) {
    return (
      <div className="flex items-center justify-center h-screen bg-slate-900">
        <div className="text-center">
          <div className="animate-spin w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4" />
          <p className="text-white text-sm">Cargando...</p>
        </div>
      </div>
    );
  }

  // Show setup wizard on first run
  if (isFirstRun && !setupComplete) {
    return <SetupWizard onComplete={() => setSetupComplete(true)} />;
  }

  // Normal app with routing
  return (
    <HashRouter>
      <div className="flex h-screen bg-slate-50 dark:bg-slate-900">
        <Sidebar />
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<PlaceholderPage title="Dashboard" />} />
            <Route path="/analysis" element={<PlaceholderPage title="Análisis" />} />
            <Route path="/settings" element={<PlaceholderPage title="Configuración" />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </HashRouter>
  );
}

export default App;
