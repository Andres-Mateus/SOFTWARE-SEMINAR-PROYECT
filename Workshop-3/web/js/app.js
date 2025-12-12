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
const recentActivityVehicles = document.getElementById('recent-activity-vehicles')
const slotsTable = document.getElementById('slots-table')

// Modal Recibo (debe existir en index.html)
const receiptModal = document.getElementById('receipt-modal')
const receiptCloseBtn = document.getElementById('receipt-close-btn')

// ---- FORMATTERS ----
const COP = new Intl.NumberFormat('es-CO', {
  style: 'currency',
  currency: 'COP',
  maximumFractionDigits: 0
})

// ---- HELPERS DE SESIÓN ----

// Guarda o limpia el token y usuario en localStorage
function setToken(token, user) {
  if (token) {
    localStorage.setItem('token', token)
    if (user) localStorage.setItem('user', JSON.stringify(user))
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
  return isNaN(date.getTime()) ? String(value) : date.toLocaleString('es-CO')
}

// Formatea input a ABC-123 mientras escribe
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

function safeText(el, value) {
  if (el) el.textContent = value
}

// Fallback por si el backend no envía minutes:
// cobra por minuto completo (ceil), mínimo 1
function computeMinutesFallback(checkInRaw, checkOutRaw) {
  try {
    const checkIn = new Date(checkInRaw)
    const checkOut = new Date(checkOutRaw)
    if (isNaN(checkIn.getTime()) || isNaN(checkOut.getTime())) return 1
    const diffMs = Math.max(0, checkOut.getTime() - checkIn.getTime())
    const minutes = Math.ceil(diffMs / 60000)
    return Math.max(1, minutes)
  } catch (_) {
    return 1
  }
}

// ---- CONTROL DE VISTAS ----

// Muestra login y oculta todo lo demás
function showLogin() {
  loginSection.classList.remove('hidden')
  registerSection.classList.add('hidden')
  appSection.classList.add('hidden')

  mainNav.classList.add('hidden')

  // ✅ visibilidad correcta de botones del banner
  if (logoutBtn) logoutBtn.classList.add('hidden')
  if (loginNavBtn) loginNavBtn.classList.remove('hidden')

  if (loginError) loginError.textContent = ''
}

// Muestra registro
function showRegister() {
  loginSection.classList.add('hidden')
  registerSection.classList.remove('hidden')
  appSection.classList.add('hidden')

  mainNav.classList.add('hidden')

  if (logoutBtn) logoutBtn.classList.add('hidden')
  if (loginNavBtn) loginNavBtn.classList.remove('hidden')

  if (registerError) registerError.textContent = ''
  if (registerSuccess) registerSuccess.textContent = ''
}

// Muestra la app (dashboard/vehicles) cuando hay sesión
function showApp() {
  loginSection.classList.add('hidden')
  registerSection.classList.add('hidden')
  appSection.classList.remove('hidden')

  mainNav.classList.remove('hidden')

  if (logoutBtn) logoutBtn.classList.remove('hidden')
  if (loginNavBtn) loginNavBtn.classList.add('hidden')

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

navLinks.forEach((link) => {
  link.addEventListener('click', (e) => {
    e.preventDefault()
    switchView(link.dataset.view)
  })
})

if (loginNavBtn) {
  loginNavBtn.addEventListener('click', (e) => {
    e.preventDefault()
    showLogin()
  })
}

if (goRegisterLink) {
  goRegisterLink.addEventListener('click', (e) => {
    e.preventDefault()
    showRegister()
  })
}

if (goLoginLink) {
  goLoginLink.addEventListener('click', (e) => {
    e.preventDefault()
    showLogin()
  })
}

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
    if (loginError) loginError.textContent = ''

    const email = document.getElementById('login-email').value.trim()
    const password = document.getElementById('login-password').value.trim()

    try {
      const data = await loginRequest(email, password)
      setToken(data.access_token, data.user)
      showApp()
    } catch (_) {
      if (loginError) {
        loginError.textContent =
          'Error de autenticación. Verifica credenciales o el estado del servidor.'
      }
    }
  })
}

// ---- REGISTRO ----

if (registerForm) {
  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault()
    if (registerError) registerError.textContent = ''
    if (registerSuccess) registerSuccess.textContent = ''

    const username = document.getElementById('register-username').value.trim()
    const email = document.getElementById('register-email').value.trim()
    const password = document.getElementById('register-password').value.trim()

    if (!username || !email || !password) {
      if (registerError) registerError.textContent = 'Todos los campos son obligatorios.'
      return
    }

    try {
      await registerRequest(username, email, password)
      if (registerSuccess) {
        registerSuccess.textContent = 'Cuenta creada con éxito. Ya puedes iniciar sesión.'
      }
      setTimeout(() => showLogin(), 1500)
    } catch (err) {
      if (registerError) {
        registerError.textContent =
          err?.message || 'No se pudo registrar. Verifica tus datos o intenta más tarde.'
      }
    }
  })
}

// ---- DASHBOARD: CARGA DE DATOS ----

async function loadDashboard() {
  try {
    const stats = await getOverviewStats()

    safeText(kpiOccupied, stats.occupied ?? '-')
    safeText(kpiFree, stats.free ?? '-')

    const rateMin = Number(
      stats.currentRatePerMinute ?? stats.rate_per_minute ?? 0
    )
    safeText(kpiRate, rateMin ? `${COP.format(rateMin)} / min` : '-')

    safeText(kpiActive, stats.activeVehicles ?? stats.active_sessions ?? '-')

    const occ = Number(stats.occupancyPercent ?? stats.occupancy_percent ?? 0)
    const safe = Math.max(0, Math.min(100, occ))

    occupancyBar.style.width = `${safe}%`
    occupancyLabel.textContent = `${safe.toFixed(1)}% de ocupación promedio`

    const sessions = await getRecentSessions(5)
    renderRecentActivity(recentActivity, sessions)
  } catch (_) {
    safeText(kpiOccupied, '-')
    safeText(kpiFree, '-')
    safeText(kpiRate, '-')
    safeText(kpiActive, '-')

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

    slotsTable.innerHTML = ''
    if (!slots.length) {
      slotsTable.innerHTML =
        '<div class="muted">No se encontraron espacios. Configura slots en el backend.</div>'
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

    renderRecentActivity(recentActivityVehicles, sessions)
  } catch (_) {
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
    vehiclePlateInput.addEventListener('blur', (e) => {
      e.target.value = formatPlate(e.target.value)
    })
  }

  vehicleForm.addEventListener('submit', async (e) => {
    e.preventDefault()
    if (vehicleMessage) vehicleMessage.textContent = ''

    const plate = formatPlate(vehiclePlateInput.value)
    const modeEl = [...vehicleForm.elements['mode']].find((r) => r.checked)
    const mode = modeEl?.value

    if (!mode) {
      if (vehicleMessage) vehicleMessage.textContent = 'Selecciona Entrada o Salida.'
      return
    }

    if (!isValidPlate(plate)) {
      if (vehicleMessage) vehicleMessage.textContent = 'Formato inválido. Usa ABC-123.'
      return
    }

    try {
      let res

      if (mode === 'entry') {
        res = await registerEntry(plate)
        vehicleMessage.textContent =
          `Entrada registrada. Espacio: ${res.slot_code || res.slot || 'asignado'} · Placa: ${res.plate || plate}.`
      } else {
        res = await registerExit(plate)

        // aseguramos minutos para UI (backend debe mandar minutes)
        const minutes =
          res.minutes ?? computeMinutesFallback(res.check_in_at || res.check_in, res.check_out_at || res.check_out)

        const amount = Number(res.amount ?? (minutes * (res.rate_per_minute ?? 0)))

        vehicleMessage.textContent =
          `Salida registrada. ${minutes} min · Total ${COP.format(amount)}.`

        // ✅ Mostramos recibo en MODAL (más estable que popup)
        showReceiptModal({
          ...res,
          minutes,
          amount
        })
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

// ---- RENDER ACTIVIDAD ----

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

// ---- MODAL RECIBO ----

function showReceiptModal(data) {
  if (!receiptModal) {
    // Fallback mínimo si no existe el modal en HTML
    alert(
      `Salida registrada\n` +
      `Placa: ${data.plate || '-'}\n` +
      `Entrada: ${formatDateTime(data.check_in_at || data.check_in) || '-'}\n` +
      `Salida: ${formatDateTime(data.check_out_at || data.check_out) || '-'}\n` +
      `Minutos: ${data.minutes ?? '-'}\n` +
      `Total: ${COP.format(Number(data.amount || 0))}`
    )
    return
  }

  const rPlate = document.getElementById('r-plate')
  const rSlot = document.getElementById('r-slot')
  const rCheckin = document.getElementById('r-checkin')
  const rCheckout = document.getElementById('r-checkout')
  const rMinutes = document.getElementById('r-minutes')
  const rAmount = document.getElementById('r-amount')

  const plate = data.plate || '-'
  const slot = data.slot || data.slot_code || '-'
  const checkIn = formatDateTime(data.check_in_at || data.check_in)
  const checkOut = formatDateTime(data.check_out_at || data.check_out)
  const minutes = data.minutes ?? '-'
  const amount = Number(data.amount || 0)

  safeText(rPlate, plate)
  safeText(rSlot, slot)
  safeText(rCheckin, checkIn || '-')
  safeText(rCheckout, checkOut || '-')
  safeText(rMinutes, String(minutes))
  safeText(rAmount, COP.format(amount))

  receiptModal.classList.remove('hidden')
}

// Cerrar modal por botón
if (receiptCloseBtn && receiptModal) {
  receiptCloseBtn.addEventListener('click', () => {
    receiptModal.classList.add('hidden')
  })
}

// Cerrar modal por click fuera de la tarjeta
if (receiptModal) {
  receiptModal.addEventListener('click', (e) => {
    if (e.target && e.target.classList.contains('modal-backdrop')) {
      receiptModal.classList.add('hidden')
    }
  })

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !receiptModal.classList.contains('hidden')) {
      receiptModal.classList.add('hidden')
    }
  })
}

// ---- ESTADO INICIAL ----
if (isAuthenticated()) {
  showApp()
} else {
  showLogin()
}