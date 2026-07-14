'use client'

import { Clock, AlertTriangle, Heart, Users, Zap } from 'lucide-react'

interface TimelineEvent {
  time: string
  type: 'conversation' | 'crime' | 'relationship' | 'system' | 'world'
  description: string
  icon: React.ReactNode
}

const TIMELINE_EVENTS: TimelineEvent[] = [
  {
    time: '06:00',
    type: 'system',
    description: 'Day 247 begins',
    icon: <Zap className="w-3 h-3" />
  },
  {
    time: '08:30',
    type: 'conversation',
    description: 'Noah & Sophia discuss market incident',
    icon: <Users className="w-3 h-3" />
  },
  {
    time: '10:15',
    type: 'crime',
    description: 'Suspicious activity detected at Bank',
    icon: <AlertTriangle className="w-3 h-3" />
  },
  {
    time: '11:45',
    type: 'relationship',
    description: 'Trust increased: Emma & Victor',
    icon: <Heart className="w-3 h-3" />
  },
  {
    time: '14:00',
    type: 'world',
    description: 'Weather: Light rain begins',
    icon: <Clock className="w-3 h-3" />
  },
  {
    time: '14:30',
    type: 'conversation',
    description: 'Court hearing scheduled',
    icon: <Zap className="w-3 h-3" />
  }
]

const typeColors: Record<string, string> = {
  conversation: 'text-secondary',
  crime: 'text-danger',
  relationship: 'text-warning',
  system: 'text-primary',
  world: 'text-muted-foreground'
}

export default function WorldTimeline() {
  return (
    <div className="glass rounded-lg border border-sidebar-border flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="px-4 py-2 border-b border-sidebar-border flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-primary" />
          <h3 className="text-sm font-semibold text-foreground">WORLD TIMELINE</h3>
        </div>
      </div>

      {/* Timeline Horizontal Scroll */}
      <div className="flex-1 overflow-x-auto overflow-y-hidden scrollbar-thin scrollbar-thumb-primary/30 scrollbar-track-transparent">
        <div className="flex gap-3 p-4 min-w-min">
          {TIMELINE_EVENTS.map((event, idx) => (
            <div
              key={idx}
              className="flex flex-col items-center cursor-pointer group transition-all hover:scale-105"
            >
              {/* Timeline Node */}
              <div className="relative mb-3">
                <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center transition-all ${
                  idx % 3 === 0 ? 'border-primary bg-primary/20' :
                  idx % 3 === 1 ? 'border-secondary bg-secondary/20' :
                  'border-muted bg-muted/20'
                } group-hover:border-primary group-hover:shadow-lg group-hover:glow-cyan`}>
                  <span className={`${typeColors[event.type]}`}>
                    {event.icon}
                  </span>
                </div>

                {/* Connector */}
                {idx < TIMELINE_EVENTS.length - 1 && (
                  <div className="absolute left-full top-1/2 -translate-y-1/2 w-6 h-0.5 bg-border" />
                )}
              </div>

              {/* Event Info */}
              <div className="text-center whitespace-nowrap opacity-0 group-hover:opacity-100 transition-all pointer-events-none group-hover:pointer-events-auto">
                <div className="mb-1.5 bg-sidebar border border-sidebar-border rounded px-2 py-1.5">
                  <p className="text-xs font-semibold text-foreground mb-0.5">{event.time}</p>
                  <p className={`text-xs font-medium ${typeColors[event.type]}`}>{event.type}</p>
                  <p className="text-xs text-muted-foreground mt-1 max-w-xs">{event.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
