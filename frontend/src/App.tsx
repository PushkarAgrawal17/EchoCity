import { useState, useEffect } from 'react';
import { CityPage } from './pages/CityPage';
import { SetupScreen } from './components/setup/SetupScreen';

function App() {
  const [setupComplete, setSetupComplete] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const verifyServerAndState = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/health');
        if (!response.ok) {
          throw new Error('API server unhealthy');
        }
        
        const complete = localStorage.getItem('echocity_setup_complete');
        if (complete === 'true') {
          setSetupComplete(true);
        }
      } catch (error) {
        // Force diagnostic checks if the FastAPI backend is offline
        setSetupComplete(false);
      } finally {
        setLoading(false);
      }
    };

    verifyServerAndState();
  }, []);

  if (loading) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-void font-echo-mono text-xs text-text-dim">
        <span className="h-2 w-2 animate-ping rounded-full bg-echo-cyan mr-2" />
        INITIALIZING OBSERVATORY GATEWAY...
      </div>
    );
  }

  if (!setupComplete) {
    return <SetupScreen onSetupComplete={() => setSetupComplete(true)} />;
  }

  return <CityPage />;
}

export default App;
