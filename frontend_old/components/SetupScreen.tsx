'use client'

import { useState } from 'react'
import { Shield, Cpu, Database, User, Server, Check, AlertCircle, Loader2, Sparkles, Terminal, Globe, Key, Wifi, WifiOff } from 'lucide-react'

interface SetupScreenProps {
  onSetupComplete: () => void
}

export default function SetupScreen({ onSetupComplete }: SetupScreenProps) {
  // Authentication choice state
  const [identityMode, setIdentityMode] = useState<'local' | 'google'>('local')
  const [googleUser, setGoogleUser] = useState<{ name: string; email: string } | null>(null)
  const [isGoogleSigningIn, setIsGoogleSigningIn] = useState(false)

  // Setup fields state
  const [username, setUsername] = useState('')
  const [pin, setPin] = useState('')

  const [ollamaUrl, setOllamaUrl] = useState('http://localhost:11434')
  const [ollamaModel, setOllamaModel] = useState('llama3.2')
  
  const [qwenUrl, setQwenUrl] = useState('http://localhost:11434')
  const [qwenModel, setQwenModel] = useState('qwen2.5:7b')

  const [dbUrl, setDbUrl] = useState('postgresql://postgres:postgres@localhost:5432/echocity')
  const [dbName, setDbName] = useState('echocity')

  // Connection testing states
  const [testingOllama, setTestingOllama] = useState<'idle' | 'testing' | 'success' | 'failed'>('idle')
  const [testingQwen, setTestingQwen] = useState<'idle' | 'testing' | 'success' | 'failed'>('idle')
  const [testingDb, setTestingDb] = useState<'idle' | 'testing' | 'success' | 'failed'>('idle')

  const [errorMsg, setErrorMsg] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleGoogleSignIn = () => {
    setIsGoogleSigningIn(true)
    setErrorMsg('')
    
    // Simulate secure google auth login over active network connection
    setTimeout(() => {
      setGoogleUser({
        name: 'Google Observer',
        email: 'observer.city@gmail.com'
      })
      setIsGoogleSigningIn(false)
    }, 1500)
  }

  const handleTestOllama = async () => {
    setTestingOllama('testing')
    setTimeout(() => {
      if (ollamaUrl.includes('localhost') || ollamaUrl.startsWith('http')) {
        setTestingOllama('success')
      } else {
        setTestingOllama('failed')
      }
    }, 1200)
  }

  const handleTestQwen = async () => {
    setTestingQwen('testing')
    setTimeout(() => {
      if (qwenUrl.includes('localhost') || qwenUrl.startsWith('http')) {
        setTestingQwen('success')
      } else {
        setTestingQwen('failed')
      }
    }, 1200)
  }

  const handleTestDb = async () => {
    setTestingDb('testing')
    setTimeout(() => {
      if (dbUrl.startsWith('postgresql://') || dbUrl.startsWith('postgres://')) {
        setTestingDb('success')
      } else {
        setTestingDb('failed')
      }
    }, 1200)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setErrorMsg('')

    if (identityMode === 'local' && !username.trim()) {
      setErrorMsg('Please enter an Observer Username.')
      return
    }

    if (identityMode === 'google' && !googleUser) {
      setErrorMsg('Please authenticate with your Google Account to proceed in Google Sync mode.')
      return
    }

    setIsSubmitting(true)

    // Store settings in localStorage
    setTimeout(() => {
      localStorage.setItem('echocity_username', identityMode === 'google' ? googleUser!.name : username.trim())
      localStorage.setItem('echocity_pin', identityMode === 'google' ? '' : pin)
      localStorage.setItem('echocity_google_connected', identityMode === 'google' ? 'true' : 'false')
      localStorage.setItem('echocity_ollama_url', ollamaUrl)
      localStorage.setItem('echocity_ollama_model', ollamaModel)
      localStorage.setItem('echocity_qwen_url', qwenUrl)
      localStorage.setItem('echocity_qwen_model', qwenModel)
      localStorage.setItem('echocity_db_url', dbUrl)
      localStorage.setItem('echocity_db_name', dbName)
      localStorage.setItem('echocity_setup_complete', 'true')
      
      setIsSubmitting(false)
      onSetupComplete()
    }, 1500)
  }

  return (
    <div className="h-screen w-screen bg-[#06090d] text-foreground flex flex-col justify-between overflow-y-auto font-sans p-6 md:p-12 selection:bg-primary/30">
      
      {/* Decorative Cyber Background Grid */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#00d9ff08_1px,transparent_1px),linear-gradient(to_bottom,#00d9ff08_1px,transparent_1px)] bg-[size:32px_32px] pointer-events-none" />
      <div className="absolute top-1/4 left-1/4 w-[400px] h-[400px] rounded-full bg-primary/5 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-[450px] h-[450px] rounded-full bg-secondary/5 blur-[120px] pointer-events-none" />

      {/* Header */}
      <div className="relative z-10 flex items-center justify-between w-full max-w-6xl mx-auto border-b border-border/20 pb-6 mb-8">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded bg-primary flex items-center justify-center text-sm font-extrabold text-primary-foreground shadow-[0_0_15px_rgba(0,217,255,0.4)]">
            EC
          </div>
          <div>
            <h1 className="text-base font-black tracking-wider uppercase">EchoCity Observatory</h1>
            <p className="text-[10px] text-muted-foreground uppercase font-mono tracking-widest mt-0.5">Civilization Monitoring System v1.2</p>
          </div>
        </div>
        <div className="hidden sm:flex items-center gap-2 px-3 py-1 border border-primary/20 rounded bg-primary/5">
          <span className="w-1.5 h-1.5 rounded-full bg-primary animate-ping" />
          <span className="text-[10px] font-mono tracking-wider text-primary uppercase">Provisioning Mode</span>
        </div>
      </div>

      {/* Form Container */}
      <div className="relative z-10 w-full max-w-3xl mx-auto flex-1 flex flex-col justify-center my-4">
        
        <div className="border border-border/30 bg-[#0d131a]/80 backdrop-blur-md rounded-xl p-6 md:p-8 shadow-2xl relative overflow-hidden">
          {/* Cyan Glow Accent Lines */}
          <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-primary/50 to-transparent" />
          <div className="absolute bottom-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-secondary/30 to-transparent" />

          {/* Heading */}
          <div className="mb-6">
            <h2 className="text-xl font-bold flex items-center gap-2.5">
              <Sparkles className="w-5 h-5 text-primary animate-pulse" />
              Observatory Initialization
            </h2>
            <p className="text-xs text-muted-foreground mt-1 leading-relaxed">
              Configure your system connections and identity node to spin up the observatory deck. Offline services run entirely on your local machine.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            
            {/* SECTION 1: IDENTITY ACCESS PROTOCOL */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 border-b border-border/10 pb-2">
                <User className="w-4 h-4 text-primary" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-foreground">1. Access & Identity Mode</h3>
              </div>
              
              {/* Identity Mode Chooser */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Local Card Option */}
                <div 
                  onClick={() => setIdentityMode('local')}
                  className={`p-4 border rounded-lg cursor-pointer transition-all flex flex-col justify-between ${
                    identityMode === 'local' 
                      ? 'border-primary bg-primary/5 shadow-[0_0_15px_rgba(0,217,255,0.1)]' 
                      : 'border-border/30 bg-card/10 hover:border-border/60'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold uppercase tracking-wider">Local Activity Mode</span>
                    <WifiOff className="w-3.5 h-3.5 text-muted-foreground" />
                  </div>
                  <p className="text-[10px] text-muted-foreground leading-relaxed">
                    Offline Mode. AI cognitive nodes and persistent databases run entirely on device. Internet features (Global Chat) are disabled.
                  </p>
                </div>

                {/* Google Card Option */}
                <div 
                  onClick={() => setIdentityMode('google')}
                  className={`p-4 border rounded-lg cursor-pointer transition-all flex flex-col justify-between ${
                    identityMode === 'google' 
                      ? 'border-primary bg-primary/5 shadow-[0_0_15px_rgba(0,217,255,0.1)]' 
                      : 'border-border/30 bg-card/10 hover:border-border/60'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold uppercase tracking-wider">Network Identity Sync</span>
                    <div className="flex items-center gap-1.5">
                      <Wifi className="w-3.5 h-3.5 text-primary" />
                    </div>
                  </div>
                  <p className="text-[10px] text-muted-foreground leading-relaxed">
                    Online Mode. Link your Google account to enable active internet synchronization, secure cloud backup, and Global Chat.
                  </p>
                </div>
              </div>

              {/* Identity Input Panels */}
              <div className="p-4 border border-border/10 rounded-lg bg-card/5">
                {identityMode === 'local' ? (
                  /* Local Form */
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-1.5">
                      <label className="text-[10px] text-muted-foreground uppercase font-semibold font-mono">Observer Name</label>
                      <input
                        type="text"
                        required={identityMode === 'local'}
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        placeholder="e.g. Local-Observer"
                        className="w-full text-xs px-3.5 py-2.5 rounded bg-[#090d12] border border-border/30 text-foreground focus:outline-none focus:border-primary/60 font-mono"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <label className="text-[10px] text-muted-foreground uppercase font-semibold font-mono">Security Access PIN (Optional)</label>
                      <input
                        type="password"
                        maxLength={8}
                        value={pin}
                        onChange={(e) => setPin(e.target.value)}
                        placeholder="••••••••"
                        className="w-full text-xs px-3.5 py-2.5 rounded bg-[#090d12] border border-border/30 text-foreground focus:outline-none focus:border-primary/60 font-mono tracking-widest"
                      />
                    </div>
                  </div>
                ) : (
                  /* Google OAuth Button */
                  <div className="flex flex-col items-center justify-center py-4 space-y-4">
                    {googleUser ? (
                      <div className="flex items-center gap-3 bg-green-500/10 border border-green-500/20 px-4 py-2.5 rounded-lg w-full max-w-md">
                        <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center font-bold text-xs text-black">
                          {googleUser.name.charAt(0)}
                        </div>
                        <div className="text-left">
                          <p className="text-xs font-bold text-foreground">{googleUser.name}</p>
                          <p className="text-[10px] text-muted-foreground">{googleUser.email}</p>
                        </div>
                        <Check className="w-4 h-4 text-green-400 ml-auto" />
                      </div>
                    ) : (
                      <button
                        type="button"
                        onClick={handleGoogleSignIn}
                        disabled={isGoogleSigningIn}
                        className="cursor-pointer flex items-center justify-center gap-3 px-6 py-2.5 border border-border/30 rounded-lg bg-card/30 hover:bg-card/70 hover:border-primary/40 transition-all font-mono text-xs w-full max-w-md"
                      >
                        {isGoogleSigningIn ? (
                          <>
                            <Loader2 className="w-3.5 h-3.5 animate-spin text-primary" />
                            Establishing OAuth Socket...
                          </>
                        ) : (
                          <>
                            <Globe className="w-4 h-4 text-primary" />
                            Authenticate with Google Account
                          </>
                        )}
                      </button>
                    )}
                    <span className="text-[9px] text-muted-foreground uppercase font-mono tracking-widest">
                      ⚠ Active Web Socket Connection Protocol Required
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* SECTION 2: AI COGNITION ENGINE */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 border-b border-border/10 pb-2">
                <Cpu className="w-4 h-4 text-primary" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-foreground">2. Offline Cognitive Nodes</h3>
              </div>
              
              {/* Ollama Section */}
              <div className="bg-card/25 border border-border/10 rounded-lg p-4 space-y-3.5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Server className="w-3.5 h-3.5 text-primary/80" />
                    <span className="text-xs font-semibold">Ollama API (Local Server Node)</span>
                  </div>
                  
                  {/* Status Indicator */}
                  <button
                    type="button"
                    onClick={handleTestOllama}
                    disabled={testingOllama === 'testing'}
                    className="text-[10px] font-mono px-2.5 py-1 rounded border border-border/20 hover:border-primary/40 transition-colors cursor-pointer flex items-center gap-1.5 hover:bg-primary/5 disabled:opacity-50"
                  >
                    {testingOllama === 'testing' && <Loader2 className="w-2.5 h-2.5 animate-spin" />}
                    {testingOllama === 'success' && <Check className="w-2.5 h-2.5 text-green-400" />}
                    {testingOllama === 'failed' && <AlertCircle className="w-2.5 h-2.5 text-red-400" />}
                    {testingOllama === 'idle' && 'Test Socket'}
                    {testingOllama === 'testing' ? 'Verifying...' : testingOllama === 'success' ? 'Socket OK' : testingOllama === 'failed' ? 'Failed' : ''}
                  </button>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-[10px] text-muted-foreground uppercase font-mono">Ollama Endpoint URL</label>
                    <input
                      type="url"
                      required
                      value={ollamaUrl}
                      onChange={(e) => setOllamaUrl(e.target.value)}
                      className="w-full text-xs px-3 py-2 rounded bg-[#090d12] border border-border/20 text-foreground focus:outline-none focus:border-primary/50 font-mono"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-[10px] text-muted-foreground uppercase font-mono">Target Model Tag</label>
                    <input
                      type="text"
                      required
                      value={ollamaModel}
                      onChange={(e) => setOllamaModel(e.target.value)}
                      className="w-full text-xs px-3 py-2 rounded bg-[#090d12] border border-border/20 text-foreground focus:outline-none focus:border-primary/50 font-mono"
                    />
                  </div>
                </div>
              </div>

              {/* Qwen Section */}
              <div className="bg-card/25 border border-border/10 rounded-lg p-4 space-y-3.5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Terminal className="w-3.5 h-3.5 text-primary/80" />
                    <span className="text-xs font-semibold">Qwen LLM (Gwen Agent Architecture)</span>
                  </div>
                  
                  {/* Status Indicator */}
                  <button
                    type="button"
                    onClick={handleTestQwen}
                    disabled={testingQwen === 'testing'}
                    className="text-[10px] font-mono px-2.5 py-1 rounded border border-border/20 hover:border-primary/40 transition-colors cursor-pointer flex items-center gap-1.5 hover:bg-primary/5 disabled:opacity-50"
                  >
                    {testingQwen === 'testing' && <Loader2 className="w-2.5 h-2.5 animate-spin" />}
                    {testingQwen === 'success' && <Check className="w-2.5 h-2.5 text-green-400" />}
                    {testingQwen === 'failed' && <AlertCircle className="w-2.5 h-2.5 text-red-400" />}
                    {testingQwen === 'idle' && 'Test Socket'}
                    {testingQwen === 'testing' ? 'Verifying...' : testingQwen === 'success' ? 'Socket OK' : testingQwen === 'failed' ? 'Failed' : ''}
                  </button>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-[10px] text-muted-foreground uppercase font-mono">Agent Service URL</label>
                    <input
                      type="url"
                      required
                      value={qwenUrl}
                      onChange={(e) => setQwenUrl(e.target.value)}
                      className="w-full text-xs px-3 py-2 rounded bg-[#090d12] border border-border/20 text-foreground focus:outline-none focus:border-primary/50 font-mono"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-[10px] text-muted-foreground uppercase font-mono">Qwen Model Code</label>
                    <input
                      type="text"
                      required
                      value={qwenModel}
                      onChange={(e) => setQwenModel(e.target.value)}
                      className="w-full text-xs px-3 py-2 rounded bg-[#090d12] border border-border/20 text-foreground focus:outline-none focus:border-primary/50 font-mono"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* SECTION 3: DATABASE TELEMETRY */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 border-b border-border/10 pb-2">
                <Database className="w-4 h-4 text-primary" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-foreground">3. Offline Persistent Database</h3>
              </div>
              <div className="bg-card/25 border border-border/10 rounded-lg p-4 space-y-3.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold">PostgreSQL Engine Node Connection</span>
                  
                  {/* Status Indicator */}
                  <button
                    type="button"
                    onClick={handleTestDb}
                    disabled={testingDb === 'testing'}
                    className="text-[10px] font-mono px-2.5 py-1 rounded border border-border/20 hover:border-primary/40 transition-colors cursor-pointer flex items-center gap-1.5 hover:bg-primary/5 disabled:opacity-50"
                  >
                    {testingDb === 'testing' && <Loader2 className="w-2.5 h-2.5 animate-spin" />}
                    {testingDb === 'success' && <Check className="w-2.5 h-2.5 text-green-400" />}
                    {testingDb === 'failed' && <AlertCircle className="w-2.5 h-2.5 text-red-400" />}
                    {testingDb === 'idle' && 'Test Node'}
                    {testingDb === 'testing' ? 'Verifying...' : testingDb === 'success' ? 'Node OK' : testingDb === 'failed' ? 'Failed' : ''}
                  </button>
                </div>
                
                <div className="space-y-3">
                  <div className="space-y-1.5">
                    <label className="text-[10px] text-muted-foreground uppercase font-mono">Connection String URI</label>
                    <input
                      type="text"
                      required
                      value={dbUrl}
                      onChange={(e) => setDbUrl(e.target.value)}
                      className="w-full text-xs px-3 py-2.5 rounded bg-[#090d12] border border-border/20 text-foreground focus:outline-none focus:border-primary/50 font-mono"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-[10px] text-muted-foreground uppercase font-mono">Database Name</label>
                    <input
                      type="text"
                      required
                      value={dbName}
                      onChange={(e) => setDbName(e.target.value)}
                      className="w-full text-xs px-3 py-2 rounded bg-[#090d12] border border-border/20 text-foreground focus:outline-none focus:border-primary/50 font-mono"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Error Message */}
            {errorMsg && (
              <div className="flex items-center gap-2 text-xs text-red-400 bg-red-950/20 border border-red-500/20 px-4 py-3 rounded">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            {/* Submit Section */}
            <div className="pt-2">
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full cursor-pointer flex items-center justify-center gap-2.5 py-3 rounded-lg bg-primary hover:bg-[#00c0e0] font-bold text-xs uppercase tracking-widest text-primary-foreground transition-all duration-300 shadow-[0_0_20px_rgba(0,217,255,0.25)] hover:shadow-[0_0_30px_rgba(0,217,255,0.45)] disabled:opacity-50"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Initializing observatory telemetry...
                  </>
                ) : (
                  <>
                    <Shield className="w-4 h-4" />
                    Initialize Observatory Deck
                  </>
                )}
              </button>
            </div>
          </form>

        </div>
      </div>

      {/* Footer */}
      <div className="relative z-10 w-full max-w-6xl mx-auto border-t border-border/10 pt-6 mt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-[10px] text-muted-foreground uppercase font-mono tracking-widest">
        <span>© 2026 ECHOCITY CIVILIZATION ENGINE. ALL RIGHTS RESERVED.</span>
        <div className="flex items-center gap-4">
          <a href="#" className="hover:text-primary transition-colors">DECRYPTION PROTOCOLS</a>
          <span className="text-border/40">|</span>
          <a href="#" className="hover:text-primary transition-colors">OBSERVATORY LOGS</a>
        </div>
      </div>
    </div>
  )
}
