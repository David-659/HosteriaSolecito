function ponerFechaHora() {
    const ahora = new Date();

    const year = ahora.getFullYear();
    const month = String(ahora.getMonth() + 1).padStart(2, '0');
    const day = String(ahora.getDate()).padStart(2, '0');
    const hours = String(ahora.getHours()).padStart(2, '0');
    const minutes = String(ahora.getMinutes()).padStart(2, '0');
    const segundos = String(ahora.getSeconds()).padStart(2, '0');

    const fechaHora = `${year}-${month}-${day} ${hours}:${minutes}:${segundos}`;
    document.getElementById('fecha_pago').value = fechaHora;
}

document.getElementById('metodo_pago_selector').addEventListener('change', function() {
    document.getElementById('metodo_pago_hidden').value = this.value;
});