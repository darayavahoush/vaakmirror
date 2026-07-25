import { NavLink } from 'react-router-dom'
import { Sparkles } from 'lucide-react'

const links = [
  { to: '/', label: 'Games', end: true },
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/exercises', label: 'Exercises' },
]

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 bg-ink/95 backdrop-blur border-b border-white/10">
      <nav className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <NavLink to="/" className="flex items-center gap-2 text-paper">
          <span className="w-8 h-8 rounded-blob bg-coral flex items-center justify-center shrink-0">
            <Sparkles size={16} className="text-paper" />
          </span>
          <span className="font-display text-xl font-bold tracking-tight">VaakMirror</span>
        </NavLink>
        <div className="flex items-center gap-1">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.end}
              className={({ isActive }) =>
                `px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                  isActive ? 'bg-mint text-ink-deep' : 'text-paper/70 hover:text-paper hover:bg-white/5'
                }`
              }
            >
              {l.label}
            </NavLink>
          ))}
        </div>
      </nav>
    </header>
  )
}
