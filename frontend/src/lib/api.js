// Talks to the FastAPI backend in /vaakmirror-backend. Base URL is
// configurable via VITE_API_URL for when this eventually points at a
// deployed backend instead of localhost.
//
// There's no child-picker UI yet, so everything here is scoped to the demo
// child the backend's seed script creates (id 1). Swap DEMO_CHILD_ID (or
// wire up real child selection) once there's an actual UI for it.

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
export const DEMO_CHILD_ID = 1

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const body = await res.text().catch(() => '')
    throw new Error(`API ${res.status} on ${path}: ${body}`)
  }
  if (res.status === 204) return null
  return res.json()
}

export function getDashboard(childId = DEMO_CHILD_ID) {
  return request(`/children/${childId}/dashboard`)
}

export function getExerciseLibrary() {
  return request('/exercises')
}

export function getChildExercises(childId = DEMO_CHILD_ID) {
  return request(`/children/${childId}/exercises`)
}

export function assignExercise(exerciseId, childId = DEMO_CHILD_ID) {
  return request(`/children/${childId}/exercises/${exerciseId}/assign`, { method: 'POST' })
}

export function updateAssignmentStatus(assignmentId, status) {
  return request(`/exercise-assignments/${assignmentId}`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  })
}

export function createGameSession(game, childId = DEMO_CHILD_ID) {
  return request(`/children/${childId}/sessions`, {
    method: 'POST',
    body: JSON.stringify({ game }),
  })
}

export function logAttempt(sessionId, attempt) {
  return request(`/sessions/${sessionId}/attempts`, {
    method: 'POST',
    body: JSON.stringify(attempt),
  })
}

export function endGameSession(sessionId) {
  return request(`/sessions/${sessionId}/end`, { method: 'PATCH' })
}
