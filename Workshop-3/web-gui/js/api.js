// API helpers centralize how the Web UI talks to the backends.

const AUTH_API_URL = 'http://localhost:8080/api/auth'
const CORE_API_URL = 'http://localhost:8000/api/core'

function getToken() {
  return localStorage.getItem('token') || ''
}

async function apiFetch(url, options = {}) {
  const headers = options.headers || {}
  const token = getToken()

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...headers
    }
  })

  return response
}

async function loginRequest(username, password) {
  const res = await fetch(`${AUTH_API_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  })

  if (!res.ok) {
    throw new Error(await res.text())
  }

  return res.json()
}

async function registerRequest(username, email, password, accessCode) {
  const res = await fetch(`${AUTH_API_URL}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password, accessCode })
  })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || 'Registration failed')
  }

  return res.text()
}

async function fetchUsers() {
  const res = await apiFetch(`${CORE_API_URL}/users`)
  if (!res.ok) {
    throw new Error('Unable to load users')
  }
  return res.json()
}

async function fetchVehicles() {
  const res = await apiFetch(`${CORE_API_URL}/vehicles`)
  if (!res.ok) {
    throw new Error('Unable to load vehicles')
  }
  return res.json()
}

async function createVehicle(vehicle) {
  const res = await apiFetch(`${CORE_API_URL}/vehicles`, {
    method: 'POST',
    body: JSON.stringify(vehicle)
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || 'Unable to create vehicle')
  }
  return res.json()
}

async function fetchTickets() {
  const res = await apiFetch(`${CORE_API_URL}/tickets`)
  if (!res.ok) {
    throw new Error('Unable to load tickets')
  }
  return res.json()
}

async function fetchLotSpaces() {
  const res = await apiFetch(`${CORE_API_URL}/lotspaces`)
  if (!res.ok) {
    throw new Error('Unable to load lot space data')
  }
  return res.json()
}

async function fetchFees() {
  const res = await apiFetch(`${CORE_API_URL}/fees`)
  if (!res.ok) {
    throw new Error('Unable to load fee data')
  }
  return res.json()
}

function setToken(token, user) {
  if (token) {
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user || {}))
  } else {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
}

function formatDate(date) {
  const parsed = new Date(date)
  if (Number.isNaN(parsed.getTime())) {
    return '-'
  }
  return parsed.toLocaleDateString()
}
