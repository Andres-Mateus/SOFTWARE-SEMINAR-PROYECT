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

function formatPlate(raw) {
  const cleaned = (raw || '')
    .toUpperCase()
    .replace(/[^A-Z0-9]/g, '')
    .slice(0, 6)

  const letters = cleaned.slice(0, 3).replace(/[^A-Z]/g, '')
  const numbers = cleaned.slice(letters.length, 6).replace(/[^0-9]/g, '')
  const finalLetters = (letters + cleaned.slice(letters.length, 3)).slice(0, 3)
  const finalNumbers = numbers.slice(0, 3)

  if (finalLetters.length === 3 && finalNumbers.length) {
    return `${finalLetters}-${finalNumbers}`.slice(0, 7)
  }

  return (finalLetters + (finalNumbers ? `-${finalNumbers}` : '')).slice(0, 7)
}

function isValidPlate(plate) {
  return /^[A-Z]{3}-\d{3}$/.test(plate)
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
  if (vehiclePlateInput) {
    vehiclePlateInput.addEventListener('input', (e) => {
      e.target.value = formatPlate(e.target.value)
    })
  }

  vehicleForm.addEventListener('submit', async (e) => {
    e.preventDefault()
    vehicleMessage.textContent = ''

    const plate = formatPlate(vehiclePlateInput.value)
    const mode = [...vehicleForm.elements['mode']].find((r) => r.checked)
      .value

    if (!isValidPlate(plate)) {
      vehicleMessage.textContent = 'Formato inválido. Usa ABC-123.'
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
        showReceipt(res)
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

function showReceipt(data) {
  const receiptWindow = window.open('', '_blank', 'width=520,height=680')
  if (!receiptWindow) return

  const plate = data.plate || ''
  const slot = data.slot || data.slot_code || '-'
  const checkIn = formatDateTime(data.check_in_at || data.check_in)
  const checkOut = formatDateTime(data.check_out_at || data.check_out)
  const rateHour = Number(data.rate_per_hour || (data.rate_per_minute || 0) * 60)
  const amount = Number(data.amount || 0)

  const logo = '/images/favicon.svg'
  receiptWindow.document.write(`
    <html>
      <head>
        <title>Recibo de Salida</title>
        <style>
          body { font-family: 'Inter', Arial, sans-serif; margin: 24px; color: #1f2937; }
          .brand { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
          .brand .logo { width: 40px; height: 40px; border-radius: 50%; background: #2563eb; color: white; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; }
          .receipt { border: 1px solid #e5e7eb; padding: 16px; border-radius: 12px; box-shadow: 0 8px 30px rgba(0,0,0,0.06); }
          h1 { margin: 0 0 4px 0; font-size: 20px; }
          h2 { margin: 8px 0 12px 0; font-size: 16px; color: #4b5563; }
          .row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px dashed #e5e7eb; }
          .row:last-child { border-bottom: none; }
          .label { color: #6b7280; font-size: 13px; }
          .value { font-weight: 600; }
          .total { font-size: 18px; margin-top: 12px; }
          .btn-print { margin-top: 16px; padding: 10px 14px; background: #2563eb; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; }
          .btn-print:hover { background: #1d4ed8; }
        </style>
      </head>
      <body>
        <div class="brand">
          <div class="logo"><img src="${logo}" alt="Logo" onerror="this.parentElement.textContent='P'" style="width:100%;height:100%;object-fit:contain;border-radius:50%;" /></div>
          <div>
            <h1>Parqueadero Web</h1>
            <div style="color:#6b7280; font-size:13px;">Recibo de salida</div>
          </div>
        </div>
        <div class="receipt">
          <div class="row"><div class="label">Placa</div><div class="value">${plate}</div></div>
          <div class="row"><div class="label">Espacio</div><div class="value">${slot}</div></div>
          <div class="row"><div class="label">Entrada</div><div class="value">${checkIn}</div></div>
          <div class="row"><div class="label">Salida</div><div class="value">${checkOut}</div></div>
          <div class="row"><div class="label">Tarifa por hora</div><div class="value">$${rateHour.toFixed(2)}</div></div>
          <div class="row total"><div class="label">Total cobrado</div><div class="value">$${amount.toFixed(2)}</div></div>
          <button class="btn-print" onclick="window.print()">Generar Recibo</button>
        </div>
      </body>
    </html>
  `)
  receiptWindow.document.close()
}

// ---- ESTADO INICIAL ----
// Si ya hay token guardado, entrar directo a la app; si no, mostrar login.
if (isAuthenticated()) {
  showApp()
} else {
  showLogin()
}