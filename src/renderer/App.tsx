/**
 * App - Main Application Entry Point
 * ===================================
 * Root component that handles:
 * - First-run setup wizard detection and display
 * - Main application routing
 * - Global state initialization
 */

import React, { useState, useEffect } from 'react';
import { HashRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { LayoutDashboard, FlaskConical, Settings, Loader2 } from 'lucide-react';
import { SetupWizard } from './components/setup';
// Import pages when they're available
// import { Dashboard } from './pages/Dashboard';
// import { Analysis } from './pages/Analysis';
// import { Settings } from './pages/Settings';

// Placeholder components until real pages are implemented
function PlaceholderPage({ title }: { title: string }) {
  return (
    <div className="flex-1 flex items-center justify-center bg-slate-50">
      <div className="text-center">
        <h1 className="text-xl font-semibold text-slate-900 mb-2">
          {title}
        </h1>
        <p className="text-slate-500">
          Esta página está en desarrollo.
        </p>
      </div>
    </div>
  );
}

// Sidebar navigation item
interface NavItemProps {
  href: string;
  icon: React.ReactNode;
  label: string;
  isActive: boolean;
}

function NavItem({ href, icon, label, isActive }: NavItemProps) {
  return (
    <a
      href={href}
      className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
        isActive 
          ? 'bg-slate-100 text-slate-900' 
          : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
      }`}
    >
      {icon}
      {label}
    </a>
  );
}

// Minimal sidebar for navigation
function Sidebar() {
  const location = useLocation();
  const currentPath = location.pathname;

  const navItems = [
    { href: '#/', path: '/', icon: <LayoutDashboard className="w-5 h-5" />, label: 'Dashboard' },
    { href: '#/analysis', path: '/analysis', icon: <FlaskConical className="w-5 h-5" />, label: 'Análisis' },
    { href: '#/settings', path: '/settings', icon: <Settings className="w-5 h-5" />, label: 'Configuración' },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 p-4 flex flex-col">
      <div className="mb-8">
        <h1 className="text-lg font-semibold text-slate-900">AI Tourism Analyzer</h1>
        <p className="text-xs text-slate-500">Opinion Analysis Tool</p>
      </div>
      <nav className="space-y-1 flex-1">
        {navItems.map((item) => (
          <NavItem
            key={item.path}
            href={item.href}
            icon={item.icon}
            label={item.label}
            isActive={currentPath === item.path}
          />
        ))}
      </nav>
      <div className="pt-4 border-t border-slate-200">
        <p className="text-xs text-slate-400 text-center">v1.0.0</p>
      </div>
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
      <div className="flex items-center justify-center h-screen bg-slate-100">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-slate-600 mx-auto mb-3" />
          <p className="text-slate-600 text-sm">Cargando...</p>
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
      <div className="flex h-screen bg-slate-50">
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
