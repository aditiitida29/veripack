import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ScanProduct from './pages/ScanProduct';
import InspectionsList from './pages/InspectionsList';
import InspectionDetails from './pages/InspectionDetails';
import ProductsRepository from './pages/ProductsRepository';
import RulesManagement from './pages/RulesManagement';
import UsersManagement from './pages/UsersManagement';
import LegalGuide from './pages/LegalGuide';

function MainLayout() {
  const { isAuthenticated, loading } = useAuth();
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [selectedInspectionId, setSelectedInspectionId] = useState(null);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center space-y-3">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500 mx-auto"></div>
          <p className="text-xs font-semibold text-slate-300">Loading VeriPack Enforcement Platform...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Login />;
  }

  const handleOpenInspection = (id) => {
    setSelectedInspectionId(id);
    setCurrentTab('inspection-detail');
  };

  const handleInspectionComplete = (id) => {
    setSelectedInspectionId(id);
    setCurrentTab('inspection-detail');
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar currentTab={currentTab} setCurrentTab={setCurrentTab} />
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          {currentTab === 'dashboard' && (
            <Dashboard
              onNavigateScan={() => setCurrentTab('scan')}
              onOpenInspection={handleOpenInspection}
            />
          )}

          {currentTab === 'scan' && (
            <ScanProduct onInspectionComplete={handleInspectionComplete} />
          )}

          {currentTab === 'inspections' && (
            <InspectionsList
              onSelectInspection={handleOpenInspection}
              onNewScan={() => setCurrentTab('scan')}
            />
          )}

          {currentTab === 'inspection-detail' && (
            <InspectionDetails
              inspectionId={selectedInspectionId}
              onBack={() => setCurrentTab('inspections')}
            />
          )}

          {currentTab === 'products' && (
            <ProductsRepository onSelectInspection={handleOpenInspection} />
          )}

          {currentTab === 'rules' && <RulesManagement />}

          {currentTab === 'users' && <UsersManagement />}

          {currentTab === 'guide' && <LegalGuide />}
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <MainLayout />
    </AuthProvider>
  );
}
