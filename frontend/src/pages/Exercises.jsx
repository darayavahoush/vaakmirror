import { useEffect, useState } from 'react'
import { PlayCircle, CheckCircle2, Clock, RefreshCw, ServerCrash, Plus } from 'lucide-react'
import { getExerciseLibrary, getChildExercises, assignExercise, updateAssignmentStatus } from '../lib/api.js'

const STATUS_STYLE = {
  assigned: { label: 'Assigned', color: 'text-coral', icon: PlayCircle },
  in_progress: { label: 'In progress', color: 'text-gold', icon: Clock },
  completed: { label: 'Completed', color: 'text-mint-dark', icon: CheckCircle2 },
  not_started: { label: 'Not started', color: 'text-ink/35', icon: PlayCircle },
}

export default function Exercises() {
  const [library, setLibrary] = useState([])
  const [assignments, setAssignments] = useState([])
  const [status, setStatus] = useState('loading') // loading | ready | error
  const [busyId, setBusyId] = useState(null)

  function load() {
    setStatus('loading')
    Promise.all([getExerciseLibrary(), getChildExercises()])
      .then(([lib, assigns]) => {
        setLibrary(lib)
        setAssignments(assigns)
        setStatus('ready')
      })
      .catch(() => setStatus('error'))
  }

  useEffect(load, [])

  // Most recent assignment per exercise (assignments come back newest-first)
  const assignmentByExerciseId = {}
  for (const a of assignments) {
    if (!assignmentByExerciseId[a.exercise.id]) assignmentByExerciseId[a.exercise.id] = a
  }

  async function handleAssign(exerciseId) {
    setBusyId(exerciseId)
    try {
      await assignExercise(exerciseId)
      load()
    } catch {
      setBusyId(null)
    }
  }

  async function handleComplete(assignmentId, exerciseId) {
    setBusyId(exerciseId)
    try {
      await updateAssignmentStatus(assignmentId, 'completed')
      load()
    } catch {
      setBusyId(null)
    }
  }

  if (status === 'loading') {
    return (
      <div className="max-w-6xl mx-auto px-6 py-24 flex flex-col items-center gap-3 text-ink/50">
        <RefreshCw className="animate-spin" size={22} />
        <p className="text-sm">Loading exercise library…</p>
      </div>
    )
  }

  if (status === 'error') {
    return (
      <div className="max-w-lg mx-auto px-6 py-24 text-center">
        <ServerCrash size={28} className="mx-auto text-ink/30 mb-4" />
        <p className="font-display text-xl font-bold text-ink mb-2">Couldn't reach the API</p>
        <p className="text-ink/55 text-sm leading-relaxed mb-6">
          Make sure the backend is running (<code className="text-xs bg-ink/5 px-1.5 py-0.5 rounded">uvicorn app.main:app --reload --port 8000</code>) and try again.
        </p>
        <button onClick={load} className="px-5 py-2.5 rounded-full bg-ink text-paper text-sm font-semibold inline-flex items-center gap-2">
          <RefreshCw size={14} /> Retry
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-12">
      <p className="font-mono text-xs uppercase tracking-widest text-mint-dark mb-1">
        Oromotor exercise library
      </p>
      <h1 className="font-display text-3xl font-bold text-ink mb-3">Practice videos</h1>
      <p className="text-ink/55 max-w-xl mb-10">
        Short instructional videos the child watches and copies — mouth, tongue,
        lip, and cheek drills. Normally these get auto-assigned when the
        dashboard detects a pattern the games alone can't fix; you can also
        assign one manually below.
      </p>

      <div className="grid md:grid-cols-2 gap-5">
        {library.map((ex) => {
          const assignment = assignmentByExerciseId[ex.id]
          const s = assignment ? STATUS_STYLE[assignment.status] : null
          const Icon = s?.icon
          const isBusy = busyId === ex.id

          return (
            <div key={ex.id} className="rounded-2xl border border-ink/10 bg-white overflow-hidden flex">
              <div className="w-36 shrink-0 bg-ink flex items-center justify-center">
                <PlayCircle size={30} className="text-paper/70" />
              </div>
              <div className="p-5 flex-1">
                <div className="flex items-start justify-between gap-3 mb-2">
                  <p className="font-display font-bold text-ink leading-snug">{ex.title}</p>
                  <span className="text-xs text-ink/40 shrink-0">{ex.duration_label}</span>
                </div>
                <p className="text-ink/55 text-sm leading-relaxed mb-4">{ex.description}</p>
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div className="flex gap-1.5 flex-wrap">
                    {ex.target_categories.map((t) => (
                      <span
                        key={t}
                        className="font-mono text-[10px] uppercase tracking-wide px-2 py-1 rounded-full bg-ink/5 text-ink/60"
                      >
                        {t}
                      </span>
                    ))}
                  </div>

                  {!assignment && (
                    <button
                      onClick={() => handleAssign(ex.id)}
                      disabled={isBusy}
                      className="flex items-center gap-1.5 text-xs font-semibold text-ink/60 hover:text-ink disabled:opacity-50"
                    >
                      <Plus size={14} /> {isBusy ? 'Assigning…' : 'Assign'}
                    </button>
                  )}

                  {assignment && assignment.status !== 'completed' && (
                    <button
                      onClick={() => handleComplete(assignment.id, ex.id)}
                      disabled={isBusy}
                      className={`flex items-center gap-1.5 text-xs font-semibold ${s.color} hover:opacity-80 disabled:opacity-50`}
                    >
                      <Icon size={14} /> {isBusy ? 'Updating…' : `${s.label} \u2014 mark complete`}
                    </button>
                  )}

                  {assignment && assignment.status === 'completed' && (
                    <span className={`flex items-center gap-1.5 text-xs font-semibold ${s.color}`}>
                      <Icon size={14} /> {s.label}
                    </span>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
