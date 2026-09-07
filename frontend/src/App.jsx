import React from 'react';
import { AppProvider, useApp } from './context/AppContext';
import { AppLayout } from './components/layout/AppLayout';
import { LandingPage } from './components/landing/LandingPage';

const RootRouter = () => {
  const { showLandingPage } = useApp();
  return showLandingPage ? <LandingPage /> : <AppLayout />;
};

export default function App() {
  return (
    <AppProvider>
      <RootRouter />
    </AppProvider>
  );
}
