// js/app.js
// Maneja la lógica de UI: login, registro, vistas protegidas, llamadas a la API.

// ---- REFERENCIAS A ELEMENTOS DEL DOM ----
const loginSection = document.getElementById('login-section')
const registerSection = document.getElementById('register-section')
const appSection = document.getElementById('app-section')

const loginForm = document.getElementById('login-form')
const loginError = document.getElementById('login-error')

const registerForm = document.getElementById('register-form')
const registerError = document.getElementById('register-error')
const registerSuccess = document.getElementById('register-success')

const goRegisterLink = document.getElementById('go-register')
const goLoginLink = document.getElementById('go-login')

const loginNavBtn = document.getElementById('login-nav-btn')
const logoutBtn = document.getElementById('logout-btn')
const mainNav = document.getElementById('main-nav')
const navLinks = document.querySelectorAll('.nav-link')

const dashboardView = document.getElementById('dashboard-view')
const vehiclesView = document.getElementById('vehicles-view')

// KPIs Dashboard
const kpiOccupied = document.getElementById('kpi-occupied')
const kpiFree = document.getElementById('kpi-free')
const kpiRate = document.getElementById('kpi-rate')
const kpiActive = document.getElementById('kpi-active')
const occupancyBar = document.getElementById('occupancy-bar')
const occupancyLabel = document.getElementById('occupancy-label')
const recentActivity = document.getElementById('recent-activity')

// Vehículos
const vehicleForm = document.getElementById('vehicle-form')
const vehiclePlateInput = document.getElementById('vehicle-plate')
const vehicleMessage = document.getElementById('vehicle-message')
const recentActivityVehicles = document.getElementById(
  'recent-activity-vehicles'
)
const slotsTable = document.getElementById('slots-table')

// ---- HELPERS DE SESIÓN ----

// Guarda o limpia el token y usuario en localStorage
function setToken(token, user) {
  if (token) {
    localStorage.setItem('token', token)
    if (user) {
      localStorage.setItem('user', JSON.stringify(user))
    }
  } else {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
}

// Verifica si hay token
function isAuthenticated() {
  return !!localStorage.getItem('token')
}

function formatDateTime(value) {
  if (!value) return ''
  const date = new Date(value)
  return isNaN(date.getTime()) ? value : date.toLocaleString('es-ES')
}

// ---- CONTROL DE VISTAS ----

// Muestra login y oculta todo lo demás
function showLogin() {
  loginSection.classList.remove('hidden')
  registerSection.classList.add('hidden')
  appSection.classList.add('hidden')
  mainNav.classList.add('hidden')
  logoutBtn.classList.add('hidden')
  loginNavBtn.classList.remove('hidden')
  loginError.textContent = ''
}

// Muestra registro con código único
function showRegister() {
  loginSection.classList.add('hidden')
  registerSection.classList.remove('hidden')
  appSection.classList.add('hidden')
  mainNav.classList.add('hidden')
  logoutBtn.classList.add('hidden')
  loginNavBtn.classList.remove('hidden')
  registerError.textContent = ''
  registerSuccess.textContent = ''
}

// Muestra la app (dashboard/vehicles) cuando hay sesión
function showApp() {
  loginSection.classList.add('hidden')
  registerSection.classList.add('hidden')
  appSection.classList.remove('hidden')
  mainNav.classList.remove('hidden')
  logoutBtn.classList.remove('hidden')
  loginNavBtn.classList.add('hidden')
  switchView('dashboard')
  loadDashboard()
}

// Cambia entre vista "dashboard" y "vehicles"
function switchView(view) {
  if (view === 'dashboard') {
    dashboardView.classList.remove('hidden')
    vehiclesView.classList.add('hidden')
  } else {
    dashboardView.classList.add('hidden')
    vehiclesView.classList.remove('hidden')
    loadVehiclesData()
  }

  // Actualiza estado visual del menú
  navLinks.forEach((link) => {
    link.classList.toggle('active', link.dataset.view === view)
  })
}

// ---- EVENTOS DE NAVEGACIÓN ----

// Click en links del navbar (Panel / Vehículos)
navLinks.forEach((link) => {
  link.addEventListener('click', (e) => {
    e.preventDefault()
    switchView(link.dataset.view)
  })
})

// Botón "Iniciar Sesión" de la navbar
if (loginNavBtn) {
  loginNavBtn.addEventListener('click', (e) => {
    e.preventDefault()
    showLogin()
  })
}

// Cambiar de Login a Register
if (goRegisterLink) {
  goRegisterLink.addEventListener('click', (e) => {
    e.preventDefault()
    showRegister()
  })
}

// Cambiar de Register a Login
if (goLoginLink) {
  goLoginLink.addEventListener('click', (e) => {
    e.preventDefault()
    showLogin()
  })
}

// Botón "Cerrar Sesión"
if (logoutBtn) {
  logoutBtn.addEventListener('click', () => {
    setToken(null)
    showLogin()
  })
}

// ---- LOGIN ----

if (loginForm) {
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault()
    loginError.textContent = ''

    const email = document.getElementById('login-email').value.trim()
    const password = document
      .getElementById('login-password')
      .value.trim()

    try {
      const data = await loginRequest(email, password)
      setToken(data.access_token, data.user)
      showApp()
    } catch (err) {
      loginError.textContent =
        'Error de autenticación. Verifica credenciales o el estado del servidor.'
    }
  })
}

// ---- REGISTRO CON USUARIO ÚNICO ----

if (registerForm) {
  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault()
    registerError.textContent = ''
    registerSuccess.textContent = ''

    const username = document
      .getElementById('register-username')
      .value.trim()
    const email = document
      .getElementById('register-email')
      .value.trim()
    const password = document
      .getElementById('register-password')
      .value.trim()

    if (!username || !email || !password) {
      registerError.textContent = 'Todos los campos son obligatorios.'
      return
    }

    try {
      await registerRequest(username, email, password)
      registerSuccess.textContent =
        'Account created successfully. You can now sign in.'
      // Opcional: volver automáticamente al login
      setTimeout(() => {
        showLogin()
      }, 1500)
    } catch (err) {
      registerError.textContent =
        'Registration failed. Please verify your data or try again later.'
    }
  })
}

// ---- DASHBOARD: CARGA DE DATOS ----

async function loadDashboard() {
  try {
    const stats = await getOverviewStats()
    kpiOccupied.textContent = stats.occupied
    kpiFree.textContent = stats.free
    kpiRate.textContent =
      '$' + (stats.currentRatePerMinute || 0).toFixed(2) + '/min'
    kpiActive.textContent = stats.activeVehicles

    const occ = stats.occupancyPercent ?? 0
    const safe = Math.max(0, Math.min(100, occ))
    occupancyBar.style.width = `${safe}%`
    occupancyLabel.textContent = `${safe.toFixed(
      1
    )}% de ocupación promedio`

    const sessions = await getRecentSessions(5)
    renderRecentActivity(recentActivity, sessions)
  } catch (err) {
    kpiOccupied.textContent = '-'
    kpiFree.textContent = '-'
    kpiRate.textContent = '-'
    kpiActive.textContent = '-'
    occupancyBar.style.width = '0%'
    occupancyLabel.textContent =
      'No se pudieron cargar las estadísticas del core-service.'
    recentActivity.innerHTML =
      '<li class="muted">No se pudo obtener la actividad reciente.</li>'
  }
}

// ---- VEHÍCULOS: CARGA DE DATOS ----

async function loadVehiclesData() {
  try {
    const [slots, sessions] = await Promise.all([
      getSlots(),
      getRecentSessions(8)
    ])

    // Slots
    slotsTable.innerHTML = ''
    if (!slots.length) {
      slotsTable.innerHTML =
        '<div class="muted">No se encontraron slots. Configura slots en el backend.</div>'
    } else {
      slots.forEach((s) => {
        const row = document.createElement('div')
        row.className = 'slots-row'
        const statusClass = s.occupied ? 'status-bad' : 'status-ok'
        const statusText = s.occupied ? 'Ocupado' : 'Libre'
        row.innerHTML = `
          <span>${s.code}</span>
          <span class="${statusClass}">${statusText}</span>
          <span>${s.plate || '-'}</span>
        `
        slotsTable.appendChild(row)
      })
    }

    // Actividad reciente
    renderRecentActivity(recentActivityVehicles, sessions)
  } catch (err) {
    slotsTable.innerHTML =
      '<div class="muted">No se pudieron cargar los slots desde el core-service.</div>'
    recentActivityVehicles.innerHTML =
      '<li class="muted">No se pudo obtener la actividad reciente.</li>'
  }
}

// ---- REGISTRO ENTRADA / SALIDA ----

if (vehicleForm) {
  vehicleForm.addEventListener('submit', async (e) => {
    e.preventDefault()
    vehicleMessage.textContent = ''

    const plate = vehiclePlateInput.value.trim().toUpperCase()
    const mode = [...vehicleForm.elements['mode']].find((r) => r.checked)
      .value

    if (!plate) {
      vehicleMessage.textContent = 'Ingrese una placa válida.'
      return
    }

    try {
      let res
      if (mode === 'entry') {
        res = await registerEntry(plate)
        vehicleMessage.textContent = `Entrada registrada. Espacio: ${
          res.slot_code || 'asignado'
        } · Placa: ${res.plate || plate}.`
      } else {
        res = await registerExit(plate)
        const minutes =
          res.minutes !== undefined ? res.minutes : '-'
        const amount =
          res.amount !== undefined
            ? `$${res.amount.toFixed(2)}`
            : '$0.00'
        vehicleMessage.textContent = `Salida registrada. ${minutes} min · Total ${amount}.`
      }

      vehiclePlateInput.value = ''
      await loadVehiclesData()
      await loadDashboard()
    } catch (err) {
      vehicleMessage.textContent =
        err?.message ||
        'Error al registrar la operación. Verifica la placa o la conexión con el backend.'
    }
  })
}

function renderRecentActivity(listElement, sessions) {
  const items = Array.isArray(sessions)
    ? sessions
    : sessions?.items || sessions || []

  listElement.innerHTML = ''
  if (!items.length) {
    listElement.innerHTML = '<li class="muted">Sin movimientos recientes.</li>'
    return
  }

  items.forEach((s) => {
    const type = s.check_out_at ? 'Salida' : 'Entrada'
    const time = formatDateTime(s.check_out_at || s.check_in_at)
    const li = document.createElement('li')
    li.textContent = `${s.plate} · ${type} · ${time}`
    listElement.appendChild(li)
  })
}

// ---- ESTADO INICIAL ----
// Si ya hay token guardado, entrar directo a la app; si no, mostrar login.
if (isAuthenticated()) {
  showApp()
} else {
  showLogin()
}