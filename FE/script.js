// Constants
const API_BASE_URL = process.env.API_BASE_URL || 'https://coworkingspace-backend.vercel.app/secure'; // Ensure API_BASE_URL is set in .env

// DOM Elements
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const dashboard = document.getElementById('dashboard');
const loginLink = document.getElementById('loginLink');
const registerLink = document.getElementById('registerLink');
const dashboardLink = document.getElementById('dashboardLink');
const logoutLink = document.getElementById('logoutLink');
const reservationDate = document.getElementById('reservationDate');
const seatGrid = document.getElementById('seatGrid');

// Navigation Event Listeners
loginLink.addEventListener('click', () => showSection('loginForm'));
registerLink.addEventListener('click', () => showSection('registerForm'));
logoutLink.addEventListener('click', handleLogout);

// Show/Hide Sections
function showSection(sectionId) {
    loginForm.style.display = 'none';
    registerForm.style.display = 'none';
    dashboard.style.display = 'none';
    document.getElementById(sectionId).style.display = 'block';
}

// Handle Login
async function handleLogin(event) {
    event.preventDefault();
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });

        const data = await response.json();
        if (response.ok) {
            localStorage.setItem('token', data.access_token);
            showDashboard();
        } else {
            alert(data.detail || 'Login failed.');
        }
    } catch (error) {
        alert('An error occurred during login.');
    }
}

// Handle Register
async function handleRegister(event) {
    event.preventDefault();
    const username = document.getElementById('registerUsername').value;
    const password = document.getElementById('registerPassword').value;

    try {
        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });

        const data = await response.json();
        if (response.ok) {
            alert('Registration successful! Please login.');
            showSection('loginForm');
        } else {
            alert(data.detail || 'Registration failed.');
        }
    } catch (error) {
        alert('An error occurred during registration.');
    }
}

// Initialize Seats
function initializeSeats() {
    seatGrid.innerHTML = '';
    for (let i = 1; i <= 20; i++) {
        const seat = document.createElement('div');
        seat.className = 'seat available';
        seat.id = `seat-${i}`;
        seat.innerHTML = `Seat ${i}`;
        seat.onclick = () => handleSeatClick(i);
        seatGrid.appendChild(seat);
    }
}

// Check Seat Availability
async function checkAvailability() {
    const date = reservationDate.value;
    if (!date) return;

    try {
        const response = await fetch(`${API_BASE_URL}/reservations/check-availability?reservation_date=${date}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
            },
        });

        const data = await response.json();
        updateSeatDisplay(data);
    } catch (error) {
        console.error('Error checking availability:', error);
    }
}

// Update Seat Display
function updateSeatDisplay(seatData) {
    seatData.forEach(({ seat_number, available }) => {
        const seat = document.getElementById(`seat-${seat_number}`);
        if (seat) {
            seat.className = available ? 'seat available' : 'seat occupied';
        }
    });
}

// Handle Seat Click
async function handleSeatClick(seatNumber) {
    const date = reservationDate.value;
    if (!date) {
        alert('Please select a date first.');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/reservations`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
            },
            body: JSON.stringify({ seat_number: seatNumber, reservation_date: date }),
        });

        if (response.ok) {
            alert('Seat reserved successfully.');
            checkAvailability();
        } else {
            const data = await response.json();
            alert(data.detail || 'Reservation failed.');
        }
    } catch (error) {
        alert('An error occurred while reserving the seat.');
    }
}

// Handle Logout
function handleLogout() {
    localStorage.removeItem('token');
    showSection('loginForm');
}

// Show Dashboard
function showDashboard() {
    showSection('dashboard');
    initializeSeats();
}

// On Window Load
window.onload = () => {
    const token = localStorage.getItem('token');
    if (token) {
        showDashboard();
    } else {
        showSection('loginForm');
    }
};
