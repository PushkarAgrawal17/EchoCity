import { useState, useEffect } from 'react';
import { CityPage } from './pages/CityPage';
import { SetupScreen } from './components/setup/SetupScreen';

function App() {
  const [setupComplete, setSetupComplete] = useState<boolean>(false);
  const [mounted, setMounted] = useState<boolean>(false);

  useEffect(() => {
    setMounted(true);
    const complete = localStorage.getItem('echocity_setup_complete');
    if (complete === 'true') {
      setSetupComplete(true);
    }
  }, []);

  if (!mounted) {
    return <div className="h-screen w-screen bg-void" />;
  }

  if (!setupComplete) {
    return <SetupScreen onSetupComplete={() => setSetupComplete(true)} />;
  }

  return <CityPage />;
}

export default App;
