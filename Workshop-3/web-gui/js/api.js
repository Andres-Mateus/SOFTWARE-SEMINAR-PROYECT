// js/api.js
// Centraliza las URLs de los servicios y helpers para llamadas con JWT.

// URL del servicio de autenticación (Spring Boot)
const AUTH_API_URL = 'http://localhost:8080/api/auth'

// URL del servicio core (FastAPI)
const CORE_API_URL = 'http://localhost:8000/api/core'

// Obtiene el token guardado en localStorage
function getToken() {
  return localStorage.getItem('token') || ''
}

// Helper genérico para llamar al core-service con Authorization si hay token
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

// Login against auth-service
async function loginRequest(email, password) {
  const res = await fetch(`${AUTH_API_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  })

  if (!res.ok) {
    throw new Error('Login failed')
  }

  // Expected: { accessToken, user: { email, role, roles } }
  return res.json()
}

// Registro de usuario con código de acceso único
async function registerRequest(email, password, accessCode) {
  const username = email.split('@')[0]
  const res = await fetch(`${AUTH_API_URL}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email,
      password,
      accessCode,
      username
    })
  })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || 'Registration failed')
  }

  return res.json()
}

// Obtiene estadísticas generales para el dashboard
async function getOverviewStats() {
  const res = await apiFetch(`${CORE_API_URL}/stats/overview`)
  if (!res.ok) {
    throw new Error('Error fetching stats')
  }
  return res.json()
}

// Obtiene sesiones recientes (para actividad)
async function getRecentSessions(limit = 5) {
  const res = await apiFetch(
    `${CORE_API_URL}/sessions?limit=${limit}&order=desc`
  )
  if (!res.ok) {
    throw new Error('Error fetching sessions')
  }
  return res.json()
}

// Obtiene estado de slots
async function getSlots() {
  const res = await apiFetch(`${CORE_API_URL}/slots`)
  if (!res.ok) {
    throw new Error('Error fetching slots')
  }
  return res.json()
}

// Registra entrada de vehículo
async function registerEntry(plate) {
  const res = await apiFetch(`${CORE_API_URL}/entries`, {
    method: 'POST',
    body: JSON.stringify({ plate })
  })
  if (!res.ok) {
    throw new Error('Error registering entry')
  }
  return res.json()
}

// Registra salida de vehículo
async function registerExit(plate) {
  const res = await apiFetch(`${CORE_API_URL}/exits`, {
    method: 'POST',
    body: JSON.stringify({ plate })
  })
  if (!res.ok) {
    throw new Error('Error registering exit')
  }
  return res.json()
}