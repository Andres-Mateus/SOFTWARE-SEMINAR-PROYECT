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

async function handleResponse(response, fallbackMessage = 'Request failed') {
  const raw = await response.text()
  let data = null

  if (raw) {
    try {
      data = JSON.parse(raw)
    } catch (_) {
      data = raw
    }
  }

  if (!response.ok) {
    const detail =
      (data && typeof data === 'object'
        ? data.detail || data.message || data.error
        : null) || (typeof data === 'string' ? data : null)

    const error = new Error(detail || fallbackMessage)
    error.status = response.status
    throw error
  }

  return data
}

// Login contra auth-service
async function loginRequest(email, password) {
  const res = await fetch(`${AUTH_API_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  })

  // Se espera: { access_token, user: { id, username, email } }
  return handleResponse(res, 'Login failed')
  if (!res.ok) {
    throw new Error('Login failed')
  }

  // Se espera: { access_token, user: { id, username, email } }
  return res.json()
}

// Registro de usuario
async function registerRequest(username, email, password) {
  const res = await fetch(`${AUTH_API_URL}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password })
  })

  return handleResponse(res, 'Registration failed')
}

// Obtiene estadísticas generales para el dashboard
async function getOverviewStats() {
  const res = await apiFetch(`${CORE_API_URL}/stats/overview`)
  return handleResponse(res, 'Error fetching stats')
}

// Obtiene sesiones recientes (para actividad)
async function getRecentSessions(limit = 5) {
  const res = await apiFetch(
    `${CORE_API_URL}/sessions?limit=${limit}&order=desc`
  )
  return handleResponse(res, 'Error fetching sessions')
}

// Obtiene estado de slots
async function getSlots() {
  const res = await apiFetch(`${CORE_API_URL}/slots`)
  return handleResponse(res, 'Error fetching slots')
}

// Registra entrada de vehículo
async function registerEntry(plate) {
  const res = await apiFetch(`${CORE_API_URL}/entries`, {
    method: 'POST',
    body: JSON.stringify({ plate })
  })
  return handleResponse(res, 'Error registering entry')
}

// Registra salida de vehículo
async function registerExit(plate) {
  const res = await apiFetch(`${CORE_API_URL}/exits`, {
    method: 'POST',
    body: JSON.stringify({ plate })
  })
  return handleResponse(res, 'Error registering exit')
  if (!res.ok) {
    throw new Error('Error registering exit')
  }
  return res.json()
}
