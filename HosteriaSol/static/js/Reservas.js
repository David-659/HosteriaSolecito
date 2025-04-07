// Variables globales
let currentMonthIndex = new Date().getMonth();
let currentYear = new Date().getFullYear();
let selectedDays = [];
const costoBasePorPersona = 130.0;

const months = [
  "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
];

const unavailableDaysByMonth = {};

function daysInMonth(month, year) {
  return new Date(year, month + 1, 0).getDate();
}

function updateCalendar() {
  const daysContainer = document.querySelector(".days");
  daysContainer.innerHTML = "";

  document.getElementById("month-label").innerText = `${months[currentMonthIndex]} ${currentYear}`;

  const totalDays = daysInMonth(currentMonthIndex, currentYear);
  const unavailableDays = unavailableDaysByMonth[currentMonthIndex] || [];

  const firstDayOfMonth = new Date(currentYear, currentMonthIndex, 1).getDay();

  for (let i = 0; i < firstDayOfMonth; i++) {
    const emptyCell = document.createElement("div");
    emptyCell.className = "empty";
    daysContainer.appendChild(emptyCell);
  }

  const today = new Date();
  const currentDay = today.getDate();
  const currentMonth = today.getMonth();
  const currentFullYear = today.getFullYear();

  for (let day = 1; day <= totalDays; day++) {
    const dayElement = document.createElement("div");

    const isPastDay =
      currentYear < currentFullYear ||
      (currentYear === currentFullYear && currentMonthIndex < currentMonth) ||
      (currentYear === currentFullYear && currentMonthIndex === currentMonth && day < currentDay);

    if (unavailableDays.includes(day) || isPastDay) {
      dayElement.className = "day unavailable";
    } else {
      dayElement.className = "day available";
      dayElement.onclick = () => selectDate(dayElement, day);
    }

    if (currentYear === currentFullYear && currentMonthIndex === currentMonth && day === currentDay) {
      dayElement.classList.add("today");
    }

    dayElement.innerText = day;
    daysContainer.appendChild(dayElement);
  }
}

function nextMonth() {
  currentMonthIndex++;
  if (currentMonthIndex > 11) {
    currentMonthIndex = 0;
    currentYear++;
  }
  resetCalendar();
  updateCalendar();
}

function prevMonth() {
  currentMonthIndex--;
  if (currentMonthIndex < 0) {
    currentMonthIndex = 11;
    currentYear--;
  }
  resetCalendar();
  updateCalendar();
}

function selectDate(dayElement, day) {
  const reserveButton = document.getElementById("reserve-button");
  const errorMessage = document.querySelector(".error-message");

  if (dayElement.classList.contains("unavailable")) return;

  if (selectedDays.length === 2) {
    resetCalendar();
  }

  selectedDays.push(day);
  selectedDays.sort((a, b) => a - b);

  const allDays = document.querySelectorAll(".day.available");
  if (selectedDays.length === 2) {
    const [start, end] = selectedDays;
    if (start === end) {
      errorMessage.innerText = "Los días de inicio y fin deben ser diferentes.";
      errorMessage.style.display = "block";
      reserveButton.disabled = true;
      return;
    }
    allDays.forEach((dayEl) => {
      const dayNumber = parseInt(dayEl.innerText, 10);
      if (dayNumber >= start && dayNumber <= end) {
        dayEl.classList.add("selected");
      }
    });

    const startDate = new Date(currentYear, currentMonthIndex, start);
    const endDate = new Date(currentYear, currentMonthIndex, end);

    const startFormatted = startDate.toISOString().split('T')[0];
    const endFormatted = endDate.toISOString().split('T')[0];

    if (document.getElementById('startInput')) {
      document.getElementById('startInput').value = startFormatted;
    }
    if (document.getElementById('endInput')) {
      document.getElementById('endInput').value = endFormatted;
    }
  } else {
    dayElement.classList.add("selected");
  }

  reserveButton.disabled = selectedDays.length !== 2;

  if (selectedDays.length !== 2) {
    document.getElementById('contenido_oculto').style.display = 'none';
  }
}

function resetCalendar() {
  const days = document.querySelectorAll(".day");
  days.forEach((day) => day.classList.remove("selected"));
  selectedDays = [];
  document.querySelector(".error-message").style.display = "none";
  document.getElementById('contenido_oculto').style.display = 'none';
}

function reserve() {
  if (selectedDays.length !== 2) {
    const errorMessage = document.querySelector(".error-message");
    errorMessage.innerText = "Por favor, seleccione dos días.";
    errorMessage.style.display = "block";
    return;
  }

  document.querySelector(".error-message").style.display = "none";
  document.getElementById('contenido_oculto').style.display = 'block';
  document.getElementById("reservation-modal").style.display = "block";
}

function closeModal() {
  document.getElementById('contenido_oculto').style.display = 'none';
}

function updateRoomCards() {
  const selectedRoomTypeId = document.getElementById("tipo-habitacion").value;
  const cards = document.querySelectorAll(".card");

  cards.forEach(card => {
    if (card.getAttribute("data-id") === selectedRoomTypeId) {
      card.style.display = "block";
    } else {
      card.style.display = "none";
    }
  });
}

document.addEventListener("DOMContentLoaded", function () {
  updateCalendar();
  updateRoomCards();
  document.getElementById("tipo-habitacion").addEventListener("change", updateRoomCards);
});

