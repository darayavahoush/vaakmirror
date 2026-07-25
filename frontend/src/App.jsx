import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar.jsx'
import Landing from './pages/Landing.jsx'
import MirrorMirror from './pages/MirrorMirror.jsx'
import TongueTamer from './pages/TongueTamer.jsx'
import LipSyncHero from './pages/LipSyncHero.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Exercises from './pages/Exercises.jsx'

export default function App() {
  return (
    <div className="min-h-screen bg-paper">
      <Navbar />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/games/mirror-mirror" element={<MirrorMirror />} />
        <Route path="/games/tongue-tamer" element={<TongueTamer />} />
        <Route path="/games/lip-sync-hero" element={<LipSyncHero />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/exercises" element={<Exercises />} />
      </Routes>
    </div>
  )
}
