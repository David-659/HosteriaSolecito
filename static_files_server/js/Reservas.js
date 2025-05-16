flatpickr("#fechas", {
  mode: "range",
  minDate: "today",
  dateFormat: "Y-m-d",
  locale: "es",
  showMonths: 2,
  onChange: function(selectedDates) {
    if (selectedDates.length === 2) {
      const noches = Math.floor((selectedDates[1] - selectedDates[0]) / (1000 * 60 * 60 * 24));
      document.getElementById('estancia').innerHTML = `Estancia de ${noches} noches`;
    }
  }
});

function changeCount(id, delta) {
  const input = document.getElementById(id);
  let value = parseInt(input.value) || 0;
  value += delta;

  if (value < 0) value = 0; 
  input.value = value;
}

function confirmar_eliminar(ruta){
  console.log(ruta);
  if(confirm("Está seguro de cancelar esta reserva? ")){
      location.href = ruta;
  }
}