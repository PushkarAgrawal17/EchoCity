'use client'

import { useState, useEffect } from 'react'
import { LogOut, Clock, Calendar, User } from 'lucide-react'

export default function TopBar({ onResetSetup }: { onResetSetup?: () => void }) {
  const [showProfileMenu, setShowProfileMenu] = useState(false)
  const [googleConnected, setGoogleConnected] = useState(false)
  const [username, setUsername] = useState('Observer')

  useEffect(() => {
    const stored = localStorage.getItem('echocity_username')
    if (stored) {
      setUsername(stored)
    }
    const isGoogle = localStorage.getItem('echocity_google_connected') === 'true'
    setGoogleConnected(isGoogle)
  }, [])

  return (
    <div className="h-14 border-b border-border/20 bg-background/40 flex items-center justify-between px-6 gap-6">
      {/* Left Section - Logo & Status */}
      <div className="flex items-center gap-6 min-w-max">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded bg-primary flex items-center justify-center text-xs font-bold text-primary-foreground">
            EC
          </div>
          <h1 className="text-sm font-bold text-foreground">EchoCity</h1>
        </div>

        <div className="flex items-center gap-4 text-xs text-muted-foreground">
          <span>Day 5</span>
          <span className="font-mono">14:32</span>
          <div className="flex items-center gap-1.5">
            <div className="w-1 h-1 rounded-full bg-green-500 animate-pulse" />
            <span>Active</span>
          </div>
        </div>
      </div>

      {/* Right Section - Controls */}
      <div className="flex items-center gap-4 min-w-max">
        {/* Google Connection Status */}
        {googleConnected ? (
          <span className="text-xs text-green-400 font-mono tracking-wider flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
            Google Sync Active
          </span>
        ) : (
          <span className="text-xs text-muted-foreground font-mono tracking-wider flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-yellow-600/80" />
            Offline Mode
          </span>
        )}

        {/* Player Profile - Avatar & Menu */}
        <div className="relative">
          <button
            onClick={() => setShowProfileMenu(!showProfileMenu)}
            className="flex items-center gap-2 hover:opacity-80 transition-opacity cursor-pointer py-1 px-2 border border-border/10 rounded bg-card/25"
          >
            <div className="w-5 h-5 rounded bg-primary flex items-center justify-center">
              <User className="w-3 h-3 text-primary-foreground" />
            </div>
            <span className="text-xs text-foreground font-semibold">{username}</span>
          </button>

          {/* Profile Dropdown */}
          {showProfileMenu && (
            <div className="absolute right-0 top-full mt-2 w-48 bg-card/95 border border-border/30 backdrop-blur-md z-50 overflow-hidden rounded-lg shadow-2xl animate-in fade-in duration-200">
              <div className="p-3 border-b border-border/20 text-xs">
                <p className="font-semibold text-foreground">Profile Controls</p>
                <p className="text-muted-foreground/80 mt-0.5 truncate">{username}</p>
              </div>
              <div className="p-1 space-y-0.5 text-xs">
                <button 
                  onClick={() => {
                    setShowProfileMenu(false)
                    onResetSetup?.()
                  }}
                  className="w-full text-left px-3 py-2 hover:bg-muted/40 text-foreground transition-colors cursor-pointer rounded"
                >
                  Observatory Config
                </button>
                <button className="w-full text-left px-3 py-2 hover:bg-muted/40 text-foreground transition-colors cursor-pointer rounded">
                  Help / Manual
                </button>
                <div className="border-t border-border/20 my-1" />
                <button 
                  onClick={() => {
                    setShowProfileMenu(false)
                    if (confirm("Are you sure you want to log out and clear all configurations?")) {
                      localStorage.clear()
                      onResetSetup?.()
                    }
                  }}
                  className="w-full flex items-center gap-2 px-3 py-2 hover:bg-destructive/20 text-destructive transition-colors text-xs cursor-pointer rounded"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  Clear & Logout
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
