'use client'

import { useState, useRef, useEffect } from 'react'

interface TerminalLine {
  id: string
  type: 'input' | 'output' | 'error'
  content: string
}

const COMMANDS = {
  'help': 'Show available commands',
  'ls': 'List entries in the current location',
  'cd [location]': 'Move to a location ("cd .." or "cd /" to go back)',
  'pwd': 'Show current path',
  'tree': 'Show the full virtual map',
  'observe [location]': 'List agents present at a location',
  'question [agent]': 'Ask an agent what they remember',
  'collect [agent] [memory_index]': 'Collect a memory as evidence',
  'case': 'Show all evidence in the case file',
  'remove [index]': 'Remove evidence from the case file',
  'clear': 'Clear the terminal screen',
  'clear-case': 'Clear all evidence from the case file',
  'accuse [agent]': 'Accuse an agent of the crime',
  'submit': 'Submit the case file to the Court for evaluation',
  'suggest [agent]': 'Suggest a thought to an agent',
  'warn [agent]': 'Warn an agent of danger',
  'comfort [agent]': 'Comfort an agent',
  'encourage [agent]': 'Encourage an agent',
  'remember [agent] [memory_index]': 'Make an agent remember a detail',
  'coincidence [agent] [memory_index]': 'Influence agent connection'
}

export default function TerminalSection({ onClose }: { onClose: () => void }) {
  const [lines, setLines] = useState<TerminalLine[]>([
    { id: '0', type: 'output', content: 'EchoShell Terminal - Type "help" for commands' }
  ])
  const [input, setInput] = useState('')
  const [path, setPath] = useState<string[]>([])
  const [history, setHistory] = useState<string[]>([])
  const [historyIndex, setHistoryIndex] = useState<number | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [lines])

  const getPromptPrefix = (currentPath: string[]) => {
    const pathSegment = currentPath.length > 0 ? '/' + currentPath.join('/') : ''
    return `root@echo ~${pathSegment} $ `
  }

  const handleCommand = async (command: string) => {
    const trimmed = command.trim()
    if (!trimmed) return

    // Intercept client-side screen clearing
    if (trimmed.toLowerCase() === 'clear') {
      setLines([])
      setHistory(prev => [...prev, command])
      setHistoryIndex(null)
      return
    }

    // Prepend path prefix to input line history
    const prefix = getPromptPrefix(path)
    setLines(prev => [...prev, { id: `${Date.now()}-${Math.random()}`, type: 'input', content: prefix + command }])
    setHistory(prev => [...prev, command])
    setHistoryIndex(null)

    // Call backend FastAPI endpoint
    try {
      const response = await fetch('http://127.0.0.1:8000/api/command', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ command })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      
      // Update shell directory path
      setPath(result.path)

      // Split multi-line outputs and append
      const outputLines = result.output.split('\n')
      outputLines.forEach((outLine: string) => {
        setLines(prev => [...prev, { 
          id: `${Date.now()}-${Math.random()}`, 
          type: result.error ? 'error' : 'output', 
          content: outLine 
        }])
      })

    } catch (err: any) {
      setLines(prev => [...prev, { 
        id: `${Date.now()}-${Math.random()}`, 
        type: 'error', 
        content: `Error connecting to EchoShell API: ${err.message || err}` 
      }])
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleCommand(input)
      setInput('')
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      const newIndex = historyIndex === null ? history.length - 1 : Math.max(0, historyIndex - 1)
      setHistoryIndex(newIndex)
      setInput(history[newIndex] || '')
    } else if (e.key === 'ArrowDown') {
      e.preventDefault()
      if (historyIndex === null) return
      const newIndex = historyIndex + 1
      if (newIndex >= history.length) {
        setHistoryIndex(null)
        setInput('')
      } else {
        setHistoryIndex(newIndex)
        setInput(history[newIndex])
      }
    } else if (e.key === 'Tab') {
      e.preventDefault()
      // Autocomplete command matching prefix
      const commands = Object.keys(COMMANDS)
      const matching = commands.find(c => c.startsWith(input))
      if (matching) {
        setInput(matching.split(' ')[0]) // Match only the base command
      }
    }
  }

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="px-6 py-3 border-b border-border/20">
        <h2 className="text-xs font-bold text-green-400 uppercase tracking-wider font-mono">$ echocity-terminal</h2>
      </div>

      {/* Terminal Output */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto scrollbar-thin"
      >
        <div className="space-y-0 p-5 font-mono text-xs bg-black/20">
          {lines.map((line) => (
            <div 
              key={line.id} 
              className={`${
                line.type === 'input' ? 'text-green-400 font-medium' :
                line.type === 'error' ? 'text-red-400' :
                'text-green-300/75'
              } whitespace-pre-wrap`}
            >
              {line.content}
            </div>
          ))}
        </div>
      </div>

      {/* Input Section */}
      <div className="px-6 py-3 border-t border-border/20 bg-black/30">
        <div className="flex items-center gap-1 font-mono text-xs">
          <span className="text-green-500 font-bold">{getPromptPrefix(path)}</span>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="observe"
            className="flex-1 bg-transparent text-green-400 placeholder-green-900/60 focus:outline-none ml-1"
            autoFocus
          />
        </div>
      </div>
    </div>
  )
}
