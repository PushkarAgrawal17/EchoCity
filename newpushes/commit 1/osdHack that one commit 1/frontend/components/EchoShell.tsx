'use client'

import { useState, useRef, useEffect } from 'react'
import { Terminal as TerminalIcon, ChevronRight } from 'lucide-react'

const EXAMPLE_COMMANDS = [
  'observe noah',
  'inspect judge',
  'cat ava/diary',
  'trace bank',
  'tail world/events',
  'suggest judge "The witness appears frightened."',
  'question emma',
  'watch court'
]

interface TerminalLine {
  type: 'command' | 'output' | 'error'
  content: string
}

export default function EchoShell() {
  const [lines, setLines] = useState<TerminalLine[]>([
    { type: 'output', content: 'EchoCity Operating System v1.0' },
    { type: 'output', content: 'Type "help" for available commands' },
    { type: 'output', content: '' }
  ])
  const [input, setInput] = useState('')
  const [history, setHistory] = useState<string[]>([])
  const [historyIndex, setHistoryIndex] = useState(-1)
  const containerRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }, [lines])

  const handleCommand = (cmd: string) => {
    const trimmed = cmd.trim()
    if (!trimmed) return

    // Add command to display
    setLines(prev => [...prev, { type: 'command', content: `echocity > ${trimmed}` }])

    // Add to history
    setHistory(prev => [...prev, trimmed])
    setHistoryIndex(-1)

    // Simulate command execution
    setTimeout(() => {
      let response = ''
      if (trimmed === 'help') {
        response = `Available commands:\n  observe <citizen>\n  inspect <location>\n  cat <path>\n  trace <subject>\n  tail <log>\n  suggest <target> "<message>"\n  question <citizen>\n  watch <location>`
      } else if (trimmed.startsWith('observe')) {
        const citizen = trimmed.replace('observe', '').trim()
        response = `[${new Date().toLocaleTimeString()}] Observing ${citizen || 'environment'}...\n${citizen}: Currently at Bank, Stress: 65%, Trust: 42%`
      } else if (trimmed.startsWith('inspect')) {
        response = `[INSPECT] Analyzing target...\nLocation metadata loaded\nRelationship graph updated`
      } else if (trimmed === 'clear' || trimmed === 'cls') {
        setLines([{ type: 'output', content: '' }])
        setInput('')
        return
      } else {
        response = `Command executed: ${trimmed}\n[Process complete]`
      }

      setLines(prev => [
        ...prev,
        { type: 'output', content: response },
        { type: 'output', content: '' }
      ])
    }, 300)

    setInput('')
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      if (!e.nativeEvent.isComposing) {
        handleCommand(input)
      }
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      if (history.length > 0) {
        const newIndex = historyIndex + 1
        if (newIndex < history.length) {
          setHistoryIndex(newIndex)
          setInput(history[history.length - 1 - newIndex])
        }
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault()
      if (historyIndex > 0) {
        const newIndex = historyIndex - 1
        setHistoryIndex(newIndex)
        setInput(history[history.length - 1 - newIndex])
      } else if (historyIndex === 0) {
        setHistoryIndex(-1)
        setInput('')
      }
    } else if (e.key === 'Tab') {
      e.preventDefault()
      // Simple autocomplete
      const matching = EXAMPLE_COMMANDS.find(cmd => cmd.startsWith(input))
      if (matching) {
        setInput(matching)
      }
    }
  }

  return (
    <div className="glass rounded-lg border border-sidebar-border flex flex-col overflow-hidden h-full">
      {/* Header */}
      <div className="px-4 py-3 border-b border-sidebar-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <TerminalIcon className="w-4 h-4 text-primary" />
          <h3 className="text-sm font-semibold text-foreground">ECHOSHELL</h3>
        </div>
        <span className="text-xs text-muted-foreground">v1.0</span>
      </div>

      {/* Terminal Content */}
      <div
        ref={containerRef}
        className="flex-1 overflow-y-auto p-4 space-y-1 font-mono text-xs bg-black/30 scrollbar-thin scrollbar-thumb-primary/30 scrollbar-track-transparent"
      >
        {lines.map((line, idx) => (
          <div
            key={idx}
            className={`leading-relaxed ${
              line.type === 'command'
                ? 'text-primary'
                : line.type === 'error'
                ? 'text-danger'
                : 'text-secondary'
            }`}
          >
            {line.content.split('\n').map((subline, subIdx) => (
              <div key={subIdx}>{subline || '\u00A0'}</div>
            ))}
          </div>
        ))}
      </div>

      {/* Input Line */}
      <div className="px-4 py-3 border-t border-sidebar-border flex items-center gap-2 bg-black/40">
        <ChevronRight className="w-4 h-4 text-primary flex-shrink-0" />
        <span className="text-primary font-mono text-xs">echocity</span>
        <span className="text-muted-foreground text-xs">{'>'}</span>
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => inputRef.current?.focus()}
          placeholder="Type a command..."
          className="flex-1 bg-transparent text-foreground font-mono text-xs outline-none placeholder-muted-foreground/50"
          autoComplete="off"
          spellCheck="false"
        />
        <div className="text-muted-foreground/40 text-xs animate-pulse">▋</div>
      </div>
    </div>
  )
}
