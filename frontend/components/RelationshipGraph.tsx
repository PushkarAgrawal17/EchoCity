'use client'

import { useState } from 'react'
import { Heart, Shield, Skull, MapPin, Briefcase, Package } from 'lucide-react'

interface Citizen {
  id: string
  name: string
  role: string
  location: string
  emotion: string
  stress: number
  trust: Record<string, number>
  inventory: string[]
  recentActivities: string[]
  secrets: string[]
}

const citizens: Citizen[] = [
  {
    id: '1',
    name: 'Emma',
    role: 'Healer',
    location: 'The Clinic',
    emotion: 'Concerned',
    stress: 72,
    trust: { Noah: 85, Thomas: 45, Sarah: 92, Marcus: 65 },
    inventory: ['Medical herbs', 'Healing salts', 'Ancient tome'],
    recentActivities: ['Treated a patient', 'Argued with Thomas', 'Consulted the library'],
    secrets: ['Knows the true cause of illness', 'Has doubts about the council']
  },
  {
    id: '2',
    name: 'Noah',
    role: 'Wanderer',
    location: 'The Tavern',
    emotion: 'Curious',
    stress: 48,
    trust: { Emma: 88, Thomas: 72, Sarah: 78, Marcus: 55 },
    inventory: ['Travel map', 'Rare artifacts', 'Journal'],
    recentActivities: ['Traveled to the forest', 'Met with Sarah', 'Discovered new path'],
    secrets: ['Found evidence of the weather anomaly', 'Has a hidden map']
  },
  {
    id: '3',
    name: 'Thomas',
    role: 'Builder',
    location: 'The Construction Site',
    emotion: 'Determined',
    stress: 65,
    trust: { Emma: 42, Noah: 75, Sarah: 68, Marcus: 78 },
    inventory: ['Building plans', 'Tools', 'Materials list'],
    recentActivities: ['Started new building', 'Argued with Emma', 'Worked with Marcus'],
    secrets: ['Discovered structural weakness', 'Planning something big']
  },
  {
    id: '4',
    name: 'Sarah',
    role: 'Philosopher',
    location: 'The Library',
    emotion: 'Thoughtful',
    stress: 58,
    trust: { Emma: 95, Noah: 89, Thomas: 70, Marcus: 62 },
    inventory: ['Ancient books', 'Scrolls', 'Writing supplies'],
    recentActivities: ['Researched history', 'Discussed theories', 'Found clues'],
    secrets: ['Knows about the cycles', 'Uncovered a pattern']
  },
  {
    id: '5',
    name: 'Marcus',
    role: 'Merchant',
    location: 'The Market',
    emotion: 'Concerned',
    stress: 82,
    trust: { Emma: 70, Noah: 60, Thomas: 82, Sarah: 65 },
    inventory: ['Fine silk', 'Spices', 'Gold coins'],
    recentActivities: ['Dealt with theft', 'Met with Thomas', 'Negotiated prices'],
    secrets: ['Knows who stole the goods', 'Has debts to repay']
  }
]

export default function RelationshipGraph({ onSelectCitizen, selectedCitizen }: { 
  onSelectCitizen: (id: string) => void
  selectedCitizen: string | null 
}) {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({})

  const selectedCitizenData = selectedCitizen ? citizens.find(c => c.id === selectedCitizen) : null

  const toggleExpand = (section: string) => {
    setExpanded(prev => ({ ...prev, [section]: !prev[section] }))
  }

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-border/20">
        <h2 className="text-xs font-bold text-foreground uppercase tracking-wider">Citizens</h2>
        <p className="text-xs text-muted-foreground/70 mt-2">Network & Profiles</p>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        {/* Citizens Grid */}
        <div className="px-5 py-5 border-b border-border/20 space-y-2.5">
          {citizens.map((citizen) => (
            <button
              key={citizen.id}
              onClick={() => onSelectCitizen(citizen.id)}
              className={`w-full p-3 transition-all text-left border-b border-border/10 hover:border-border/40 pb-3 last:border-0 ${
                selectedCitizen === citizen.id
                  ? 'text-primary'
                  : 'text-foreground hover:text-primary/80'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <p className="text-xs font-semibold">{citizen.name}</p>
                <p className="text-xs text-muted-foreground/60 font-mono">{citizen.stress}%</p>
              </div>
              <p className="text-xs text-muted-foreground/70">{citizen.role}</p>
            </button>
          ))}
        </div>

        {/* Inspector Panel */}
        {selectedCitizenData && (
          <div className="px-5 py-5 space-y-6">
            {/* Basic Info */}
            <div className="space-y-3">
              <div>
                <h3 className="text-sm font-bold text-primary">{selectedCitizenData.name}</h3>
                <p className="text-xs text-muted-foreground/70 mt-1">{selectedCitizenData.role}</p>
              </div>

              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground/70">Location</span>
                  <span className="text-foreground font-mono">{selectedCitizenData.location}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground/70">Emotion</span>
                  <span className="text-foreground">{selectedCitizenData.emotion}</span>
                </div>
                <div className="h-0.5 bg-border/20 mt-2" />
              </div>
            </div>

            {/* Relationships */}
            <div className="space-y-2.5">
              <button
                onClick={() => toggleExpand('relationships')}
                className="flex items-center justify-between w-full text-xs font-semibold text-foreground hover:text-primary/80 transition-colors"
              >
                <span>Relations</span>
                <span className="text-muted-foreground">{expanded.relationships ? '−' : '+'}</span>
              </button>
              {expanded.relationships && (
                <div className="space-y-1.5 pl-0">
                  {Object.entries(selectedCitizenData.trust).map(([name, trust]) => (
                    <div key={name} className="text-xs flex items-center justify-between">
                      <span className="text-muted-foreground/80">{name}</span>
                      <span className={trust > 75 ? 'text-green-400' : trust > 50 ? 'text-yellow-400' : 'text-red-400'}>
                        {trust}%
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Inventory */}
            <div className="space-y-2.5">
              <button
                onClick={() => toggleExpand('inventory')}
                className="flex items-center justify-between w-full text-xs font-semibold text-foreground hover:text-primary/80 transition-colors"
              >
                <span>Inventory</span>
                <span className="text-muted-foreground">{expanded.inventory ? '−' : '+'}</span>
              </button>
              {expanded.inventory && (
                <div className="space-y-1 pl-0">
                  {selectedCitizenData.inventory.map((item, idx) => (
                    <p key={idx} className="text-xs text-muted-foreground/80">• {item}</p>
                  ))}
                </div>
              )}
            </div>

            {/* Activities */}
            <div className="space-y-2.5">
              <button
                onClick={() => toggleExpand('activities')}
                className="flex items-center justify-between w-full text-xs font-semibold text-foreground hover:text-primary/80 transition-colors"
              >
                <span>Activities</span>
                <span className="text-muted-foreground">{expanded.activities ? '−' : '+'}</span>
              </button>
              {expanded.activities && (
                <div className="space-y-1 pl-0">
                  {selectedCitizenData.recentActivities.map((activity, idx) => (
                    <p key={idx} className="text-xs text-muted-foreground/80">• {activity}</p>
                  ))}
                </div>
              )}
            </div>

            {/* Secrets */}
            {selectedCitizenData.secrets.length > 0 && (
              <div className="space-y-2.5">
                <button
                  onClick={() => toggleExpand('secrets')}
                  className="flex items-center justify-between w-full text-xs font-semibold text-red-400 hover:text-red-300 transition-colors"
                >
                  <span>Secrets</span>
                  <span className="text-muted-foreground">{expanded.secrets ? '−' : '+'}</span>
                </button>
                {expanded.secrets && (
                  <div className="space-y-1 pl-0">
                    {selectedCitizenData.secrets.map((secret, idx) => (
                      <p key={idx} className="text-xs text-red-300/80">• {secret}</p>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {!selectedCitizenData && (
          <div className="p-6 text-center">
            <p className="text-xs text-muted-foreground/50">Select a citizen</p>
          </div>
        )}
      </div>
    </div>
  )
}
