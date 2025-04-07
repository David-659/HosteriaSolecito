function ponerFechaHora() {
    let ahora = new Date().toISOString().slice(0, 19).replace("T", " "); 
    document.getElementById("fecha_hora").value = ahora;
}