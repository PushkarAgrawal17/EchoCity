'use client'

import { useState, useEffect } from 'react'
import TopBar from '@/components/TopBar'
import ChatSection from '@/components/ChatSection'
import WorldFeed from '@/components/WorldFeed'
import RelationshipGraph from '@/components/RelationshipGraph'
import TerminalSection from '@/components/TerminalSection'
import SetupScreen from '@/components/SetupScreen'

export default function Page() {
  const [isSetupComplete, setIsSetupComplete] = useState<boolean>(false)
  const [isMounted, setIsMounted] = useState(false)
  const [selectedCitizen, setSelectedCitizen] = useState<string | null>(null)

  useEffect(() => {
    setIsMounted(true)
    const setupStatus = localStorage.getItem('echocity_setup_complete')
    if (setupStatus === 'true') {
      setIsSetupComplete(true)
    }
  }, [])

  const handleSetupComplete = () => {
    setIsSetupComplete(true)
  }

  const handleResetSetup = () => {
    setIsSetupComplete(false)
  }

  // Prevent hydration mismatches
  if (!isMounted) {
    return <div className="h-screen w-screen bg-[#06090d]" />
  }

  if (!isSetupComplete) {
    return <SetupScreen onSetupComplete={handleSetupComplete} />
  }

  return (
    <div className="h-screen w-screen flex flex-col bg-background overflow-hidden animate-in fade-in duration-500">
      {/* Top Navigation Bar */}
      <TopBar onResetSetup={handleResetSetup} />

      {/* Main Content Area - 3 Column Layout */}
      <div className="flex-1 flex gap-3 overflow-hidden p-4">
        {/* Column 1 - Chat Section (20% width) */}
        <div className="w-1/5 min-w-[260px] flex flex-col overflow-hidden border border-border/10 rounded-lg bg-card/10 backdrop-blur-md hover:border-primary/20 transition-all duration-300">
          <ChatSection />
        </div>

        {/* Column 2 - Center Stack: World Feed (60% height) & Terminal Section (40% height) */}
        <div className="flex-1 min-w-[450px] flex flex-col gap-3 overflow-hidden">
          {/* World Feed */}
          <div className="flex-[0.6] flex flex-col overflow-hidden border border-border/10 rounded-lg bg-card/10 backdrop-blur-md hover:border-primary/20 transition-all duration-300">
            <WorldFeed />
          </div>
          
          {/* Terminal Section */}
          <div className="flex-[0.4] flex flex-col overflow-hidden border border-border/10 rounded-lg bg-card/10 backdrop-blur-md hover:border-primary/20 transition-all duration-300 font-mono">
            <TerminalSection onClose={() => {}} />
          </div>
        </div>

        {/* Column 3 - Relationship Graph & Character Inspector (25% width) */}
        <div className="w-1/4 min-w-[320px] flex flex-col overflow-hidden border border-border/10 rounded-lg bg-card/10 backdrop-blur-md hover:border-primary/20 transition-all duration-300">
          <RelationshipGraph onSelectCitizen={setSelectedCitizen} selectedCitizen={selectedCitizen} />
        </div>
      </div>
    </div>
  )
}
