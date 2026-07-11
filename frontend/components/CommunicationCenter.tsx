'use client'

import { useState } from 'react'
import { MessageCircle, Globe } from 'lucide-react'

interface Message {
  id: string
  speaker: string
  content: string
  location: string
  emotion: 'happy' | 'neutral' | 'sad' | 'angry'
  timestamp: string
}

const SAMPLE_MESSAGES: Message[] = [
  {
    id: '1',
    speaker: 'Sophia',
    content: 'Did you hear Noah was acting strangely at the bank?',
    location: 'Cafe',
    emotion: 'curious',
    timestamp: '10:42'
  },
  {
    id: '2',
    speaker: 'Emma',
    content: 'I don\'t think we should judge him yet.',
    location: 'Cafe',
    emotion: 'neutral',
    timestamp: '10:43'
  },
  {
    id: '3',
    speaker: 'Victor',
    content: 'Something is definitely off. I noticed it too.',
    location: 'Street',
    emotion: 'concerned',
    timestamp: '10:44'
  },
  {
    id: '4',
    speaker: 'Maya',
    content: 'We should talk to him directly about this.',
    location: 'Park',
    emotion: 'determined',
    timestamp: '10:45'
  }
]

const emotionColors: Record<string, string> = {
  happy: 'text-success',
  neutral: 'text-muted-foreground',
  sad: 'text-warning',
  angry: 'text-danger',
  curious: 'text-secondary',
  concerned: 'text-warning',
  determined: 'text-primary'
}

export default function CommunicationCenter() {
  const [activeTab, setActiveTab] = useState<'conversations' | 'global'>('conversations')

  return (
    <div className="h-80 glass rounded-lg border border-sidebar-border flex flex-col overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-sidebar-border flex items-center justify-between">
        <h3 className="text-sm font-semibold text-foreground">COMMUNICATION CENTER</h3>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-sidebar-border px-4">
        <button
          onClick={() => setActiveTab('conversations')}
          className={`px-3 py-2 text-xs font-medium border-b-2 transition-colors ${
            activeTab === 'conversations'
              ? 'text-primary border-primary'
              : 'text-muted-foreground border-transparent hover:text-foreground'
          }`}
        >
          <MessageCircle className="w-3 h-3 inline mr-1.5" />
          Conversations
        </button>
        <button
          onClick={() => setActiveTab('global')}
          className={`px-3 py-2 text-xs font-medium border-b-2 transition-colors ${
            activeTab === 'global'
              ? 'text-primary border-primary'
              : 'text-muted-foreground border-transparent hover:text-foreground'
          }`}
        >
          <Globe className="w-3 h-3 inline mr-1.5" />
          Global
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto space-y-2 p-3">
        {activeTab === 'conversations' ? (
          SAMPLE_MESSAGES.map((msg) => (
            <div
              key={msg.id}
              className="p-2.5 rounded border border-sidebar-border bg-sidebar/40 hover:bg-sidebar/60 transition-colors cursor-pointer group"
            >
              <div className="flex items-start justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold text-foreground group-hover:text-primary transition-colors">
                    {msg.speaker}
                  </span>
                  <span className={`text-xs font-medium ${emotionColors[msg.emotion]}`}>
                    {msg.emotion}
                  </span>
                </div>
                <span className="text-xs text-muted-foreground">{msg.timestamp}</span>
              </div>
              <p className="text-xs text-muted-foreground leading-snug mb-1.5 line-clamp-2">
                {msg.content}
              </p>
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground/60">{msg.location}</span>
              </div>
            </div>
          ))
        ) : (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <Globe className="w-8 h-8 text-muted-foreground/40 mx-auto mb-2" />
              <p className="text-xs text-muted-foreground">Global chat coming soon</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
