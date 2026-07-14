import { useState } from 'react';
import { FiShield, FiCpu, FiDatabase, FiCheck, FiAlertCircle, FiLoader, FiGlobe, FiSettings } from 'react-icons/fi';

interface SetupScreenProps {
  onSetupComplete: () => void;
}

export function SetupScreen({ onSetupComplete }: SetupScreenProps) {
  const [testing, setTesting] = useState(false);
  const [apiConnection, setApiConnection] = useState<'idle' | 'testing' | 'success' | 'failed'>('idle');
  const [dbConnection, setDbConnection] = useState<'idle' | 'testing' | 'success' | 'failed'>('idle');
  const [modelConnection, setModelConnection] = useState<'idle' | 'testing' | 'success' | 'failed' | 'model_not_found'>('idle');
  const [modelName, setModelName] = useState<string>('smollm2:1.7b-instruct');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const runConnectivityTests = async () => {
    setTesting(true);
    setErrorMsg(null);
    setApiConnection('testing');
    setDbConnection('testing');
    setModelConnection('testing');

    try {
      // 1. Test API Server Liveness
      const apiResponse = await fetch('http://127.0.0.1:8000/health').catch(() => null);
      if (!apiResponse || !apiResponse.ok) {
        setApiConnection('failed');
        setDbConnection('failed');
        setModelConnection('failed');
        setErrorMsg('Observatory API server is offline. Please make sure the FastAPI server is running on http://127.0.0.1:8000.');
        setTesting(false);
        return;
      }
      setApiConnection('success');

      // 2. Query detailed connections from API
      const connResponse = await fetch('http://127.0.0.1:8000/api/simulation/check-connections').catch(() => null);
      if (!connResponse || !connResponse.ok) {
        setDbConnection('failed');
        setModelConnection('failed');
        setErrorMsg('Failed to query connection parameters from API.');
        setTesting(false);
        return;
      }

      const status = await connResponse.json();
      
      // DB check
      if (status.db === 'success') {
        setDbConnection('success');
      } else {
        setDbConnection('failed');
        setErrorMsg((prev) => (prev ? prev + '\n' : '') + `Database connection error: ${status.db_error || 'Unknown error'}`);
      }

      // Ollama check
      if (status.ollama === 'success') {
        setModelConnection('success');
      } else if (status.ollama === 'model_not_found') {
        setModelConnection('model_not_found');
        setErrorMsg((prev) => (prev ? prev + '\n' : '') + `Model tag '${status.ollama_model}' is not pulled in Ollama. Run: 'ollama pull ${status.ollama_model}'`);
      } else {
        setModelConnection('failed');
        setErrorMsg((prev) => (prev ? prev + '\n' : '') + `Ollama server error: ${status.ollama_error || 'Failed to connect'}`);
      }

      if (status.ollama_model) {
        setModelName(status.ollama_model);
      }

    } catch (e: any) {
      setErrorMsg(`Connectivity testing encountered an error: ${e.message}`);
    } finally {
      setTesting(false);
    }
  };

  const handleInitialize = () => {
    localStorage.setItem('echocity_setup_complete', 'true');
    onSetupComplete();
  };

  const allGreen = apiConnection === 'success' && dbConnection === 'success' && modelConnection === 'success';

  return (
    <div className="relative flex h-screen w-screen flex-col justify-between overflow-y-auto bg-void p-6 font-echo-mono text-text-primary md:p-12 select-none">
      {/* CRT Scanline styling effect */}
      <div className="crt-scanlines pointer-events-none absolute inset-0 z-10" />

      {/* Decorative Matrix/Cyber Grid */}
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(57,255,157,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(57,255,157,0.03)_1px,transparent_1px)] bg-[size:24px_24px]" />
      <div className="pointer-events-none absolute top-1/4 left-1/4 h-[350px] w-[350px] rounded-full bg-echo-cyan/5 blur-[100px]" />
      <div className="pointer-events-none absolute bottom-1/4 right-1/4 h-[350px] w-[350px] rounded-full bg-echo-green/5 blur-[100px]" />

      {/* Header */}
      <div className="relative z-10 mx-auto flex w-full max-w-4xl items-center justify-between border-b border-white/10 pb-5">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded bg-echo-cyan font-echo-mono text-sm font-extrabold text-void shadow-[0_0_15px_rgba(57,255,253,0.4)]">
            EC
          </div>
          <div>
            <h1 className="text-sm font-bold uppercase tracking-[0.15em] text-text-primary">EchoCity Observatory</h1>
            <p className="mt-0.5 text-[9px] uppercase tracking-[0.2em] text-text-dim">Civilization Engine Console v1.3</p>
          </div>
        </div>
        <div className="flex items-center gap-2 rounded border border-echo-green/20 bg-echo-green/5 px-2.5 py-1 text-[9px] uppercase tracking-wider text-echo-green">
          <span className="h-1.5 w-1.5 animate-ping rounded-full bg-echo-green" />
          Offline First AI Mode
        </div>
      </div>

      {/* Connection Dashboard */}
      <div className="relative z-10 mx-auto flex w-full max-w-xl flex-1 flex-col justify-center py-6">
        <div className="rounded-xl border border-white/10 bg-panel/75 p-6 shadow-2xl backdrop-blur-md relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-echo-cyan/45 to-transparent" />
          <div className="absolute bottom-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-echo-green/30 to-transparent" />

          <div className="mb-6 border-b border-white/5 pb-4">
            <h2 className="text-sm font-bold uppercase tracking-wider flex items-center gap-2 text-text-primary">
              <FiSettings className="animate-spin-slow text-echo-cyan" />
              Core Connection Matrix
            </h2>
            <p className="mt-1.5 text-[11px] leading-relaxed text-text-dim">
              This terminal monitors physical interfaces. Initialize connection loops to authorize simulation deck launch.
            </p>
          </div>

          <div className="space-y-4">
            {/* API SERVER CONNECTION */}
            <div className="flex items-center justify-between rounded-lg border border-white/5 bg-white/[0.02] p-4">
              <div className="flex items-center gap-3">
                <FiGlobe className="text-echo-cyan" size={16} />
                <div>
                  <span className="block text-[11px] uppercase tracking-wider font-semibold">Local API Gateway</span>
                  <span className="text-[10px] text-text-dim">http://127.0.0.1:8000</span>
                </div>
              </div>

              <div className="text-right">
                {apiConnection === 'idle' && <span className="text-[10px] text-text-dim font-bold uppercase">STANDBY</span>}
                {apiConnection === 'testing' && <FiLoader className="animate-spin text-echo-cyan" size={14} />}
                {apiConnection === 'success' && <span className="text-[10px] text-echo-green font-bold uppercase flex items-center gap-1"><FiCheck /> ONLINE</span>}
                {apiConnection === 'failed' && <span className="text-[10px] text-echo-red font-bold uppercase flex items-center gap-1"><FiAlertCircle /> OFFLINE</span>}
              </div>
            </div>

            {/* PERSISTENT DATABASE CONNECTION */}
            <div className="flex items-center justify-between rounded-lg border border-white/5 bg-white/[0.02] p-4">
              <div className="flex items-center gap-3">
                <FiDatabase className="text-echo-amber" size={16} />
                <div>
                  <span className="block text-[11px] uppercase tracking-wider font-semibold">Persistent Database</span>
                  <span className="text-[10px] text-text-dim">echocity.db (SQLite)</span>
                </div>
              </div>

              <div className="text-right">
                {dbConnection === 'idle' && <span className="text-[10px] text-text-dim font-bold uppercase">STANDBY</span>}
                {dbConnection === 'testing' && <FiLoader className="animate-spin text-echo-amber" size={14} />}
                {dbConnection === 'success' && <span className="text-[10px] text-echo-green font-bold uppercase flex items-center gap-1"><FiCheck /> MOUNTED</span>}
                {dbConnection === 'failed' && <span className="text-[10px] text-echo-red font-bold uppercase flex items-center gap-1"><FiAlertCircle /> DISCONNECTED</span>}
              </div>
            </div>

            {/* COGNITIVE AI ENGINE */}
            <div className="flex items-center justify-between rounded-lg border border-white/5 bg-white/[0.02] p-4">
              <div className="flex items-center gap-3">
                <FiCpu className="text-echo-green" size={16} />
                <div>
                  <span className="block text-[11px] uppercase tracking-wider font-semibold">Cognitive AI Node</span>
                  <span className="text-[10px] text-text-dim">Ollama: {modelName}</span>
                </div>
              </div>

              <div className="text-right">
                {modelConnection === 'idle' && <span className="text-[10px] text-text-dim font-bold uppercase">STANDBY</span>}
                {modelConnection === 'testing' && <FiLoader className="animate-spin text-echo-green" size={14} />}
                {modelConnection === 'success' && <span className="text-[10px] text-echo-green font-bold uppercase flex items-center gap-1"><FiCheck /> READY</span>}
                {modelConnection === 'model_not_found' && <span className="text-[10px] text-echo-amber font-bold uppercase flex items-center gap-1"><FiAlertCircle /> NO MODEL</span>}
                {modelConnection === 'failed' && <span className="text-[10px] text-echo-red font-bold uppercase flex items-center gap-1"><FiAlertCircle /> OFFLINE</span>}
              </div>
            </div>
          </div>

          {/* Connection Error Message */}
          {errorMsg && (
            <div className="mt-4 flex items-start gap-2.5 rounded border border-echo-red/25 bg-echo-red/5 p-3 text-[11px] leading-relaxed text-echo-red font-echo-mono">
              <FiAlertCircle className="mt-0.5 flex-shrink-0" size={12} />
              <div className="whitespace-pre-line">{errorMsg}</div>
            </div>
          )}

          {/* Action Deck */}
          <div className="mt-6 flex flex-col gap-3">
            <button
              onClick={runConnectivityTests}
              disabled={testing}
              className="flex w-full cursor-pointer items-center justify-center gap-2 rounded border border-echo-cyan/30 bg-echo-cyan/5 py-2.5 text-xs font-bold uppercase tracking-wider text-echo-cyan transition hover:bg-echo-cyan/15 hover:shadow-[0_0_15px_rgba(57,255,253,0.15)] active:scale-[0.98] disabled:opacity-50"
            >
              {testing ? (
                <>
                  <FiLoader className="animate-spin" size={12} />
                  Resolving Telemetry...
                </>
              ) : (
                'Run Diagnostics'
              )}
            </button>

            <button
              onClick={handleInitialize}
              disabled={!allGreen || testing}
              className="flex w-full cursor-pointer items-center justify-center gap-2 rounded bg-echo-green py-2.5 text-xs font-bold uppercase tracking-wider text-void transition hover:bg-[#32e58c] hover:shadow-[0_0_20px_rgba(57,255,157,0.3)] active:scale-[0.98] disabled:cursor-not-allowed disabled:bg-echo-green/30 disabled:text-void/60 disabled:shadow-none"
            >
              <FiShield size={12} />
              Access Observatory Deck
            </button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="relative z-10 mx-auto flex w-full max-w-4xl flex-col items-center justify-between gap-4 border-t border-white/5 pt-5 text-[9px] tracking-wider text-text-dim sm:flex-row">
        <span>© 2026 ECHOCITY CIVILIZATION CONSOLE.</span>
        <div className="flex items-center gap-4 uppercase">
          <span>DECRYPTION PROTOCOLS</span>
          <span className="opacity-20">|</span>
          <span>SECURE TELEMETRY</span>
        </div>
      </div>
    </div>
  );
}
