'use client'

import { useState } from 'react'
import { Network, Heart, AlertCircle, Briefcase, Home, Zap, Book } from 'lucide-react'

interface Citizen {
  id: string
  name: string
  occupation: string
  emotion: string
  stress: number
  trust: number
  location: string
  goal: string
  secrets?: string[]
}

const CITIZENS: Citizen[] = [
  {
    id: '1',
    name: 'Noah',
    occupation: 'Banker',
    emotion: 'Anxious',
    stress: 75,
    trust: 45,
    location: 'Bank',
    goal: 'Acquire evidence',
    secrets: ['Witnessed crime at market']
  },
  {
    id: '2',
    name: 'Sophia',
    occupation: 'Judge',
    emotion: 'Observant',
    stress: 55,
    trust: 82,
    location: 'Court',
    goal: 'Seek truth'
  },
  {
    id: '3',
    name: 'Emma',
    occupation: 'Therapist',
    emotion: 'Empathetic',
    stress: 40,
    trust: 88,
    location: 'Clinic',
    goal: 'Help citizens'
  },
  {
    id: '4',
    name: 'Victor',
    occupation: 'Detective',
    emotion: 'Determined',
    stress: 65,
    trust: 70,
    location: 'Police Station',
    goal: 'Solve crime'
  },
  {
    id: '5',
    name: 'Maya',
    occupation: 'Journalist',
    emotion: 'Curious',
    stress: 50,
    trust: 60,
    location: 'News Station',
    goal: 'Uncover truth'
  }
]

interface CognitiveGraphProps {
  onSelectCitizen: (id: string) => void
  selectedCitizen: string | null
}

export default function CognitiveGraph({ onSelectCitizen, selectedCitizen }: CognitiveGraphProps) {
  const selected = selectedCitizen ? CITIZENS.find(c => c.id === selectedCitizen) : null

  return (
    <div className="glass rounded-lg border border-sidebar-border flex flex-col overflow-hidden h-full">
      {/* Header */}
      <div className="px-4 py-3 border-b border-sidebar-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Network className="w-4 h-4 text-primary" />
          <h3 className="text-sm font-semibold text-foreground">COGNITIVE GRAPH</h3>
        </div>
        <span className="text-xs text-muted-foreground">{CITIZENS.length} nodes</span>
      </div>

      {/* Graph Visualization (Simplified) */}
      <div className="flex-1 p-4 flex flex-col min-h-0">
        {/* Simple Node List */}
        <div className="flex-1 overflow-y-auto space-y-2 mb-4 scrollbar-thin scrollbar-thumb-primary/30 scrollbar-track-transparent">
          {CITIZENS.map((citizen) => (
            <button
              key={citizen.id}
              onClick={() => onSelectCitizen(citizen.id)}
              className={`w-full p-2.5 rounded border transition-all text-left group ${
                selectedCitizen === citizen.id
                  ? 'border-primary bg-primary/10 glow-cyan'
                  : 'border-sidebar-border bg-sidebar/40 hover:bg-sidebar/60'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-semibold text-foreground group-hover:text-primary transition-colors">
                  {citizen.name}
                </span>
                <div className={`w-2 h-2 rounded-full ${
                  citizen.stress > 70 ? 'bg-danger' :
                  citizen.stress > 50 ? 'bg-warning' :
                  'bg-success'
                }`} />
              </div>
              <p className="text-xs text-muted-foreground mb-1.5">{citizen.occupation}</p>
              <div className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground/70">Stress</span>
                  <div className="w-16 h-1.5 bg-sidebar rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-success to-danger transition-all"
                      style={{ width: `${citizen.stress}%` }}
                    />
                  </div>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground/70">Trust</span>
                  <div className="w-16 h-1.5 bg-sidebar rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary transition-all"
                      style={{ width: `${citizen.trust}%` }}
                    />
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>

        {/* Inspector Panel */}
        {selected && (
          <div className="border-t border-sidebar-border pt-3 space-y-2.5">
            <div className="text-xs">
              <div className="mb-2">
                <h4 className="font-semibold text-primary mb-1">Profile</h4>
                <div className="space-y-1">
                  <p className="text-muted-foreground"><span className="text-foreground/60">Name:</span> {selected.name}</p>
                  <p className="text-muted-foreground"><span className="text-foreground/60">Occupation:</span> {selected.occupation}</p>
                  <p className="text-muted-foreground"><span className="text-foreground/60">Emotion:</span> {selected.emotion}</p>
                </div>
              </div>

              <div className="mb-2">
                <h4 className="font-semibold text-primary mb-1">Current State</h4>
                <div className="flex items-center gap-2 text-muted-foreground mb-1">
                  <MapPinIcon className="w-3 h-3" />
                  {selected.location}
                </div>
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Zap className="w-3 h-3" />
                  {selected.goal}
                </div>
              </div>

              {selected.secrets && selected.secrets.length > 0 && (
                <div>
                  <h4 className="font-semibold text-warning mb-1 flex items-center gap-1">
                    <AlertCircle className="w-3 h-3" />
                    Secrets (Unlocked)
                  </h4>
                  <ul className="space-y-0.5">
                    {selected.secrets.map((secret, idx) => (
                      <li key={idx} className="text-xs text-warning/80">• {secret}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function MapPinIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  )
}
