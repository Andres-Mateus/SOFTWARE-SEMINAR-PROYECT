// Handles UI flow for authentication, dashboard rendering and vehicle data management.

// DOM references
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

// Dashboard metrics
const kpiOccupied = document.getElementById('kpi-occupied')
const kpiFree = document.getElementById('kpi-free')
const kpiRate = document.getElementById('kpi-rate')
const kpiActive = document.getElementById('kpi-active')
const occupancyBar = document.getElementById('occupancy-bar')
const occupancyLabel = document.getElementById('occupancy-label')
const recentActivity = document.getElementById('recent-activity')

// Vehicle view
const vehicleForm = document.getElementById('vehicle-form')
const vehiclePlateInput = document.getElementById('vehicle-plate')
const vehicleTypeInput = document.getElementById('vehicle-type')
const vehicleDateInput = document.getElementById('vehicle-date')
const vehicleMessage = document.getElementById('vehicle-message')
const recentActivityVehicles = document.getElementById('recent-activity-vehicles')
const slotsTable = document.getElementById('slots-table')

function isAuthenticated() {
  return !!localStorage.getItem('token')
}

function showLogin() {
  loginSection.classList.remove('hidden')
  registerSection.classList.add('hidden')
  appSection.classList.add('hidden')
  mainNav.classList.add('hidden')
  logoutBtn.classList.add('hidden')
  loginNavBtn.classList.remove('hidden')
  loginError.textContent = ''
}

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

function switchView(view) {
  if (view === 'dashboard') {
    dashboardView.classList.remove('hidden')
    vehiclesView.classList.add('hidden')
    loadDashboard()
  } else {
    dashboardView.classList.add('hidden')
    vehiclesView.classList.remove('hidden')
    loadVehiclesData()
  }

  navLinks.forEach((link) => {
    link.classList.toggle('active', link.dataset.view === view)
  })
}

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

if (loginForm) {
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault()
    loginError.textContent = ''

    const username = document.getElementById('login-username').value.trim()
    const password = document.getElementById('login-password').value.trim()

    try {
      const data = await loginRequest(username, password)
      setToken(data.token, { username })
      showApp()
    } catch (err) {
      loginError.textContent =
        'Authentication failed. Verify your credentials or the backend status.'
    }
  })
}

if (registerForm) {
  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault()
    registerError.textContent = ''
    registerSuccess.textContent = ''

    const username = document.getElementById('register-username').value.trim()
    const email = document.getElementById('register-email').value.trim()
    const password = document.getElementById('register-password').value.trim()
    const code = document.getElementById('register-code').value.trim()

    try {
      await registerRequest(username, email, password, code)
      registerSuccess.textContent = 'Account created successfully. You can now sign in.'
    } catch (err) {
      registerError.textContent = err.message || 'Registration failed.'
    }
  })
}

async function loadDashboard() {
  if (!isAuthenticated()) {
    return
  }

  try {
    const [tickets, lotSpaces, vehicles, fees] = await Promise.all([
      fetchTickets(),
      fetchLotSpaces(),
      fetchVehicles(),
      fetchFees()
    ])

    const activeTickets = tickets.filter((ticket) => !ticket.exit)
    const occupied = activeTickets.length
    const totalSpaces = lotSpaces.reduce((total, lot) => total + (lot.totalSpace || 0), 0)
    const freeSpaces = Math.max(totalSpaces - occupied, 0)
    const fee = fees.length ? fees[0].priceFee : null

    kpiOccupied.textContent = occupied
    kpiFree.textContent = freeSpaces
    kpiRate.textContent = fee ? `$${fee.toFixed(2)}` : 'N/A'
    kpiActive.textContent = new Set(activeTickets.map((ticket) => ticket.licenseplate)).size

    const occupancyPercent = totalSpaces > 0 ? Math.min((occupied / totalSpaces) * 100, 100) : 0
    occupancyBar.style.width = `${occupancyPercent}%`
    occupancyLabel.textContent = totalSpaces
      ? `${occupied} / ${totalSpaces} spaces used`
      : 'Add lot spaces to track capacity'

    renderTicketActivity(tickets)
  } catch (error) {
    kpiOccupied.textContent = '-'
    kpiFree.textContent = '-'
    kpiRate.textContent = '-'
    kpiActive.textContent = '-'
    occupancyBar.style.width = '0%'
    occupancyLabel.textContent = 'Unable to load dashboard data'
    recentActivity.innerHTML = '<li class="muted">No data available.</li>'
  }
}

function renderTicketActivity(tickets) {
  recentActivity.innerHTML = ''
  if (!tickets.length) {
    recentActivity.innerHTML = '<li class="muted">No ticket activity yet.</li>'
    return
  }

  const sorted = [...tickets].sort(
    (a, b) => new Date(b.entry).getTime() - new Date(a.entry).getTime()
  )

  sorted.slice(0, 5).forEach((ticket) => {
    const li = document.createElement('li')
    const status = ticket.exit ? 'Closed' : 'Active'
    li.textContent = `${ticket.licenseplate} • ${formatDate(ticket.entry)} • ${status}`
    recentActivity.appendChild(li)
  })
}

async function loadVehiclesData() {
  if (!isAuthenticated()) {
    return
  }

  try {
    const [vehicles, lotSpaces] = await Promise.all([
      fetchVehicles(),
      fetchLotSpaces()
    ])

    renderVehicleActivity(vehicles)
    renderLotSpaces(lotSpaces)
    if (vehicleDateInput && !vehicleDateInput.value) {
      vehicleDateInput.value = new Date().toISOString().split('T')[0]
    }
  } catch (error) {
    vehicleMessage.textContent = 'Unable to load vehicle information.'
    recentActivityVehicles.innerHTML = '<li class="muted">No data available.</li>'
    slotsTable.innerHTML = '<div class="muted">No data available.</div>'
  }
}

function renderVehicleActivity(vehicles) {
  recentActivityVehicles.innerHTML = ''
  if (!vehicles.length) {
    recentActivityVehicles.innerHTML = '<li class="muted">No vehicles stored yet.</li>'
    return
  }

  const sorted = [...vehicles].sort(
    (a, b) => new Date(b.dateregistered).getTime() - new Date(a.dateregistered).getTime()
  )

  sorted.slice(0, 5).forEach((vehicle) => {
    const li = document.createElement('li')
    li.textContent = `${vehicle.licenseplate} • ${vehicle.type} • ${formatDate(
      vehicle.dateregistered
    )}`
    recentActivityVehicles.appendChild(li)
  })
}

function renderLotSpaces(lotSpaces) {
  slotsTable.innerHTML = ''
  if (!lotSpaces.length) {
    slotsTable.innerHTML = '<div class="muted">No lot spaces configured yet.</div>'
    return
  }

  lotSpaces.forEach((lot) => {
    const row = document.createElement('div')
    row.classList.add('slot-row')

    const idCol = document.createElement('span')
    idCol.textContent = lot.idLotSpace

    const typeCol = document.createElement('span')
    typeCol.textContent = lot.type

    const totalCol = document.createElement('span')
    totalCol.textContent = lot.totalSpace

    row.appendChild(idCol)
    row.appendChild(typeCol)
    row.appendChild(totalCol)

    slotsTable.appendChild(row)
  })
}

if (vehicleForm) {
  vehicleForm.addEventListener('submit', async (e) => {
    e.preventDefault()
    vehicleMessage.textContent = ''

    const vehicle = {
      licenseplate: vehiclePlateInput.value.trim(),
      type: vehicleTypeInput.value,
      dateregistered: vehicleDateInput.value
    }

    try {
      await createVehicle(vehicle)
      vehicleMessage.textContent = 'Vehicle saved successfully.'
      vehiclePlateInput.value = ''
      vehicleDateInput.value = new Date().toISOString().split('T')[0]
      loadVehiclesData()
    } catch (error) {
      vehicleMessage.textContent = error.message || 'Unable to save vehicle.'
    }
  })
}

if (isAuthenticated()) {
  showApp()
} else {
  showLogin()
}
