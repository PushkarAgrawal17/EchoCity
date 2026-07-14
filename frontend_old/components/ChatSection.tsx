'use client'

import { useState, useEffect } from 'react'
import { MessageSquare, Globe, Send, WifiOff } from 'lucide-react'

interface Chat {
  id: string
  participants: string[]
  location: string
  timestamp: string
  preview: string
  emotion: 'curious' | 'neutral' | 'concerned' | 'determined'
}

const sampleChats: Chat[] = [
  {
    id: '1',
    participants: ['Emma', 'Thomas'],
    location: 'Café',
    timestamp: '14:28',
    preview: 'Emma: "The weather seems odd today..."',
    emotion: 'concerned'
  },
  {
    id: '2',
    participants: ['Noah', 'Sarah'],
    location: 'Library',
    timestamp: '14:15',
    preview: 'Noah: "Have you read the new scrolls?"',
    emotion: 'curious'
  },
  {
    id: '3',
    participants: ['Marcus', 'Emma'],
    location: 'Market',
    timestamp: '13:52',
    preview: 'Marcus: "These prices are ridiculous..."',
    emotion: 'determined'
  }
]

const emotionColors = {
  curious: 'text-blue-400',
  neutral: 'text-gray-400',
  concerned: 'text-red-400',
  determined: 'text-yellow-400'
}

export default function ChatSection() {
  const [activeTab, setActiveTab] = useState<'chats' | 'global'>('chats')
  const [googleConnected, setGoogleConnected] = useState(false)
  const [globalMessages, setGlobalMessages] = useState([
    { author: 'System', message: 'EchoCity simulation active', time: '10:00' },
    { author: 'Noah', message: 'Hello everyone!', time: '11:30' },
    { author: 'Emma', message: 'Good morning', time: '11:35' }
  ])
  const [messageInput, setMessageInput] = useState('')

  useEffect(() => {
    const isGoogle = localStorage.getItem('echocity_google_connected') === 'true'
    setGoogleConnected(isGoogle)
  }, [])

  const handleSendMessage = () => {
    if (messageInput.trim()) {
      setGlobalMessages([...globalMessages, { author: 'You', message: messageInput, time: '14:32' }])
      setMessageInput('')
    }
  }

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="px-5 py-3 border-b border-border/20">
        <h3 className="text-xs font-bold text-foreground uppercase tracking-wider">Conversations</h3>
      </div>

      {/* Tabs */}
      <div className="flex gap-6 border-b border-border/20 px-5">
        <button
          onClick={() => setActiveTab('chats')}
          className={`py-2.5 text-xs font-semibold tracking-wider uppercase transition-all duration-200 border-b-2 cursor-pointer ${
            activeTab === 'chats'
              ? 'text-primary border-primary drop-shadow-[0_0_8px_rgba(0,217,255,0.5)]'
              : 'text-muted-foreground border-transparent hover:text-foreground'
          }`}
        >
          Citizens
        </button>
        <button
          onClick={() => setActiveTab('global')}
          className={`py-2.5 text-xs font-semibold tracking-wider uppercase transition-all duration-200 border-b-2 cursor-pointer ${
            activeTab === 'global'
              ? 'text-primary border-primary drop-shadow-[0_0_8px_rgba(0,217,255,0.5)]'
              : 'text-muted-foreground border-transparent hover:text-foreground'
          }`}
        >
          Global
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden flex flex-col">
        {activeTab === 'chats' ? (
          // Citizen Chats
          <div className="flex-1 overflow-y-auto scrollbar-thin">
            <div className="space-y-4 p-5">
              {sampleChats.map((chat) => (
                <div
                  key={chat.id}
                  className="pb-4 border-b border-border/15 hover:border-border/40 transition-all cursor-pointer group last:border-0"
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <div className="flex items-center gap-2">
                      {chat.participants.map((p) => (
                        <span key={p} className="text-xs font-semibold text-foreground">
                          {p}
                        </span>
                      ))}
                    </div>
                    <span className="text-xs text-muted-foreground">{chat.timestamp}</span>
                  </div>
                  <p className={`text-xs mb-2 ${emotionColors[chat.emotion]}`}>{chat.location}</p>
                  <p className="text-xs text-muted-foreground/80 line-clamp-2 group-hover:text-muted-foreground transition-colors">{chat.preview}</p>
                </div>
              ))}
            </div>
          </div>
        ) : (
          // Global Chat
          <div className="flex-1 flex flex-col overflow-hidden">
            {!googleConnected ? (
              <div className="flex-1 flex flex-col items-center justify-center p-6 text-center space-y-4 animate-in fade-in duration-300">
                <div className="w-12 h-12 rounded-full bg-yellow-600/10 border border-yellow-600/30 flex items-center justify-center text-yellow-500 shadow-[0_0_15px_rgba(202,138,4,0.15)]">
                  <WifiOff className="w-5 h-5 animate-pulse" />
                </div>
                <div className="space-y-1.5 max-w-[200px]">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-foreground">Transmission Offline</h4>
                  <p className="text-[10px] text-muted-foreground leading-relaxed">
                    Global Chat transmissions require an active online sync socket. Please link your Google Account in the config deck to establish a socket.
                  </p>
                </div>
              </div>
            ) : (
              <div className="flex-1 overflow-y-auto scrollbar-thin">
                <div className="space-y-3 p-5">
                  {globalMessages.map((msg, idx) => (
                    <div key={idx} className="space-y-0.5">
                      <div className="flex items-center justify-between">
                        <p className="text-xs font-semibold text-primary">{msg.author}</p>
                        <p className="text-xs text-muted-foreground/60">{msg.time}</p>
                      </div>
                      <p className="text-sm text-foreground/90">
                        {msg.message}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Message Input */}
            <div className="p-4 border-t border-border/20 bg-black/10">
              <div className="flex gap-2">
                <input
                  type="text"
                  disabled={!googleConnected}
                  value={messageInput}
                  onChange={(e) => setMessageInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder={googleConnected ? "Message..." : "Transmitter Offline..."}
                  className="flex-1 px-3 py-1.5 text-xs bg-transparent border-b border-border/30 text-foreground placeholder-muted-foreground/40 focus:outline-none focus:border-primary/60 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                />
                <button
                  disabled={!googleConnected}
                  onClick={handleSendMessage}
                  className="px-2 py-1.5 text-primary hover:text-primary/80 transition-colors disabled:text-muted-foreground disabled:opacity-45 cursor-pointer disabled:cursor-not-allowed"
                >
                  <Send className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
