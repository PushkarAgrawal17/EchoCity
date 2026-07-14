'use client'

import { useState, useEffect } from 'react'

interface Event {
  id: string
  day: number
  time: string
  location: string
  type: 'social' | 'crime' | 'weather' | 'court' | 'discovery'
  participants?: string[]
  narrative: string
}

const sampleEvents: Event[] = [
  {
    id: '1',
    day: 5,
    time: '14:32',
    location: 'The Town Square',
    type: 'social',
    participants: ['Emma', 'Thomas'],
    narrative: `Emma stepped into the bustling town square, her thoughts still heavy with concern about the recent argument with Thomas. The afternoon sun cast long shadows across the weathered cobblestones. She noticed Thomas near the fountain, his expression troubled. Their eyes met for a moment—a silent acknowledgment of the tension between them. The market vendors' calls echoed around them as if the world didn't notice the weight of their unspoken words.`
  },
  {
    id: '2',
    day: 5,
    time: '13:45',
    location: 'The Café',
    type: 'social',
    participants: ['Noah', 'Sarah', 'Barista'],
    narrative: `The aroma of fresh coffee mingled with whispered conversations as Noah settled into his favorite corner of the café. Sarah arrived moments later, her usual bright demeanor dimmed by something troubling. Over steaming cups, they discussed the peculiar weather patterns that had plagued the village for the past three days. Sarah's fingers traced the rim of her mug nervously. "It's unnatural," she murmured, her eyes distant. Noah listened intently, occasionally nodding, already planning to consult the old records kept in the library.`
  },
  {
    id: '3',
    day: 5,
    time: '12:15',
    location: 'The Market',
    type: 'crime',
    participants: ['Marcus', 'Merchant', 'Guard'],
    narrative: `A commotion erupted near the spice stall when Marcus discovered three bolts of fine silk had gone missing. The merchant threw his hands up in exasperation while the town guard arrived to take statements. Marcus paced back and forth, his usual confidence shaken. This wasn't the first theft—three incidents in two weeks. A pattern was forming, one that suggested more than simple opportunism. The guard made notes in his leather journal, promising to investigate further.`
  },
  {
    id: '4',
    day: 5,
    time: '10:30',
    location: 'The Library',
    type: 'discovery',
    participants: ['Sarah', 'Noah'],
    narrative: `Deep within the library's restricted section, Sarah discovered an ancient tome bound in faded leather. Its pages spoke of cycles—natural rhythms that governed the world in ways the village had forgotten. The text described weather patterns that matched the current anomalies perfectly. As she read aloud to Noah, a sense of urgency grew between them. The knowledge was old but relevant, a key perhaps to understanding what was happening. Sarah's hands trembled slightly as she carefully turned each brittle page.`
  },
  {
    id: '5',
    day: 5,
    time: '09:00',
    location: 'The Tavern',
    type: 'social',
    participants: ['Marcus', 'Emma', 'Thomas'],
    narrative: `The tavern was subdued in the early morning light. Marcus sat at the bar, nursing a drink and contemplating his business troubles. Emma and Thomas arrived separately, neither aware the other would be there. An awkward moment passed before they settled at different tables. Marcus watched the dynamic unfold, understanding immediately that something significant had shifted between them. He'd seen enough village drama to recognize the signs—the avoided glances, the careful distance.`
  }
]

const typeAccent = {
  social: 'text-blue-400 border-blue-500/20 bg-blue-500/5',
  crime: 'text-red-400 border-red-500/20 bg-red-500/5',
  weather: 'text-cyan-400 border-cyan-500/20 bg-cyan-500/5',
  court: 'text-yellow-400 border-yellow-500/20 bg-yellow-500/5',
  discovery: 'text-green-400 border-green-500/20 bg-green-500/5'
}

const typeLabels = {
  social: 'Social Interaction',
  crime: 'Incident Report',
  weather: 'Weather Alert',
  court: 'Court Session',
  discovery: 'Discovery Logs'
}

export default function WorldFeed() {
  const [activeTab, setActiveTab] = useState<'city' | 'simulation'>('city')
  const [events, setEvents] = useState<Event[]>([])
  const [isRunning, setIsRunning] = useState(false)
  const [activeScene, setActiveScene] = useState('cafe')
  const [tickCount, setTickCount] = useState(0)
  const [saveMessage, setSaveMessage] = useState<string | null>(null)
  const [expandedId, setExpandedId] = useState<string | null>(null)

  // Polling simulation status and narrative events
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch current status
        const statusRes = await fetch('http://127.0.0.1:8000/api/simulation/status')
        if (statusRes.ok) {
          const status = await statusRes.json()
          setIsRunning(status.is_running)
          setActiveScene(status.active_scene)
          setTickCount(status.tick_count)
        }

        // Fetch events
        const eventsRes = await fetch('http://127.0.0.1:8000/api/simulation/events')
        if (eventsRes.ok) {
          const logs = await eventsRes.json()
          setEvents(logs)
        }
      } catch (err) {
        console.error('Error polling simulation telemetry:', err)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 2000)
    return () => clearInterval(interval)
  }, [])

  const handleChangeScene = async (scene: string) => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/simulation/scene', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ scene })
      })
      if (res.ok) {
        setActiveScene(scene)
        // Immediately fetch refreshed event logs
        const eventsRes = await fetch('http://127.0.0.1:8000/api/simulation/events')
        if (eventsRes.ok) {
          const logs = await eventsRes.json()
          setEvents(logs)
        }
      }
    } catch (err) {
      console.error('Error switching simulation scene context:', err)
    }
  }

  const handleSave = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/simulation/save', {
        method: 'POST'
      })
      if (res.ok) {
        const result = await res.json()
        setSaveMessage(result.message)
        setTimeout(() => setSaveMessage(null), 3000)
      }
    } catch (err) {
      console.error('Error saving simulation state:', err)
    }
  }

  const handleReset = async () => {
    if (!confirm('Are you sure you want to reset the simulation? This clears case files and resets logs.')) return
    try {
      const res = await fetch('http://127.0.0.1:8000/api/simulation/reset', {
        method: 'POST'
      })
      if (res.ok) {
        setIsRunning(false)
        setEvents([])
        setTickCount(0)
        setActiveScene('cafe')
      }
    } catch (err) {
      console.error('Error resetting simulation state:', err)
    }
  }

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id)
  }

  return (
    <div className="flex flex-col h-full overflow-hidden bg-black/10">
      {/* Header */}
      <div className="px-6 py-4 border-b border-border/20 bg-black/40">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h2 className="text-xs font-bold text-foreground uppercase tracking-wider font-mono">Narrative Feed</h2>
            <p className="text-[10px] text-muted-foreground/60 font-mono mt-0.5">Observatory Intelligence Node</p>
          </div>
          {/* Status badge when on simulation tab */}
          {activeTab === 'simulation' && (
            <div className="flex items-center gap-2 px-3 py-1 rounded-full border border-border/20 bg-black/30 font-mono text-[9px]">
              <span className="text-green-400 font-bold uppercase">📍 Scene: {activeScene}</span>
              <span className="text-muted-foreground/30">|</span>
              <span className="text-muted-foreground/50">Frame: {tickCount}</span>
            </div>
          )}
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-border/10 pb-2 mb-2">
          <button
            onClick={() => setActiveTab('city')}
            className={`flex-1 py-1 text-center font-mono text-xs font-bold border-b-2 transition-all ${
              activeTab === 'city'
                ? 'border-primary text-primary font-bold'
                : 'border-transparent text-muted-foreground/60 hover:text-foreground'
            }`}
          >
            City Headlines
          </button>
          <button
            onClick={() => setActiveTab('simulation')}
            className={`flex-1 py-1 text-center font-mono text-xs font-bold border-b-2 transition-all ${
              activeTab === 'simulation'
                ? 'border-green-500 text-green-400 font-bold glow-green-sm'
                : 'border-transparent text-muted-foreground/60 hover:text-foreground'
            }`}
          >
            Simulation Feed
          </button>
        </div>

        {/* Control Deck for Simulation Tab */}
        {activeTab === 'simulation' && (
          <div className="mt-3 space-y-2 animate-fade-in">
            {/* Scene Selection toggles */}
            <div className="flex flex-wrap items-center gap-2">
              <button
                onClick={() => handleChangeScene('cafe')}
                className={`flex-1 py-1.5 px-3 rounded font-mono text-[10px] font-bold border transition-all duration-300 ${
                  activeScene === 'cafe'
                    ? 'border-green-500 text-green-400 bg-green-500/10 glow-green-sm'
                    : 'border-border/30 text-muted-foreground bg-black/10 hover:text-foreground'
                }`}
              >
                Cafe Gossip
              </button>
              <button
                onClick={() => handleChangeScene('court')}
                className={`flex-1 py-1.5 px-3 rounded font-mono text-[10px] font-bold border transition-all duration-300 ${
                  activeScene === 'court'
                    ? 'border-green-500 text-green-400 bg-green-500/10 glow-green-sm'
                    : 'border-border/30 text-muted-foreground bg-black/10 hover:text-foreground'
                }`}
              >
                Court Trial
              </button>
            </div>

            {/* Core Save/Reset commands */}
            <div className="flex items-center gap-2">
              <button
                onClick={handleSave}
                className="flex-1 py-1.5 px-3 rounded font-mono text-[10px] border border-cyan-500/30 text-cyan-400 bg-cyan-500/5 hover:bg-cyan-500/20 active:scale-95 transition-all duration-300"
              >
                Save State
              </button>
              <button
                onClick={handleReset}
                className="flex-1 py-1.5 px-3 rounded font-mono text-[10px] border border-red-500/30 text-red-400 bg-red-500/5 hover:bg-red-500/20 active:scale-95 transition-all duration-300"
              >
                Reset State
              </button>
            </div>

            {/* Saved message */}
            {saveMessage && (
              <div className="px-3 py-1 rounded border border-green-500/20 bg-green-500/5 font-mono text-[9px] text-green-400 animate-fade-in flex items-center justify-between">
                <span>💾 {saveMessage}</span>
                <span className="text-[8px] text-green-500/50 uppercase">Sync</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Events Feed List */}
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        {activeTab === 'city' ? (
          /* City Headlines Tab */
          <div className="space-y-6 p-6">
            {sampleEvents.map((event) => (
              <div
                key={event.id}
                onClick={() => toggleExpand(event.id)}
                className="group cursor-pointer transition-all pb-5 border-b border-border/10 hover:border-border/25 last:border-0"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono text-muted-foreground/50">
                    Day {event.day} • {event.time}
                  </span>
                  <span className={`text-[9px] font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${typeAccent[event.type]}`}>
                    {typeLabels[event.type]}
                  </span>
                </div>

                <p className="text-xs font-semibold text-foreground/90 font-mono mb-2 group-hover:text-primary transition-colors">
                  📍 {event.location}
                </p>

                <p className={`text-xs leading-relaxed text-foreground/75 font-sans mb-3 ${
                  expandedId === event.id ? '' : 'line-clamp-2'
                }`}>
                  {event.narrative}
                </p>

                <div className="flex items-center justify-between mt-2">
                  {event.participants && (
                    <div className="flex flex-wrap gap-2">
                      {event.participants.map((participant) => (
                        <span
                          key={participant}
                          className="text-[10px] text-primary/70 font-mono border border-primary/10 px-1.5 py-0.5 rounded bg-primary/5"
                        >
                          @{participant}
                        </span>
                      ))}
                    </div>
                  )}

                  {expandedId !== event.id && (
                    <span className="text-[9px] font-mono text-muted-foreground/30 group-hover:text-muted-foreground/60 uppercase transition-all">
                      expand
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* Simulation Feed Tab */
          events.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full p-8 text-center">
              <span className="text-xl mb-2">📡</span>
              <p className="font-mono text-xs text-muted-foreground/60 uppercase tracking-wider">Simulation Feed Idle</p>
              <p className="text-[10px] text-muted-foreground/45 mt-1 max-w-[240px]">
                Click Play above or run `sim-start` in the terminal to stream active Cafe and Court scenes.
              </p>
            </div>
          ) : (
            <div className="space-y-2.5 p-6 font-mono text-xs">
              {events.map((event: any) => (
                <div
                  key={event.id}
                  className="flex items-start gap-2 py-1 leading-relaxed border-b border-border/5 hover:bg-white/5 px-2 rounded transition-all animate-fade-in"
                >
                  {/* Timestamp */}
                  <span className="text-muted-foreground/40 font-mono shrink-0 select-none">
                    [{event.time}]
                  </span>

                  {/* Log Content */}
                  <div className="flex-1">
                    {event.is_dialogue ? (
                      <div>
                        <span className="text-green-400 font-bold shrink-0 mr-1.5">
                          @{event.speaker}:
                        </span>
                        <span className="text-green-300/80">
                          {event.narrative}
                        </span>
                      </div>
                    ) : (
                      <span className="text-muted-foreground/60 italic">
                        * {event.narrative} *
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )
        )}
      </div>
    </div>
  )
}
