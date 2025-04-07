document.getElementById("reservaForm").addEventListener("submit", function(event) {
    event.preventDefault();
    let nombre = document.getElementById("nombre").value;
    let habitacion = document.getElementById("habitacion").value;
    let dias = document.getElementById("dias").value;
    let costo = document.getElementById("costo").value;
    
    let reserva = { nombre, habitacion, dias, costo };
    let reservas = JSON.parse(localStorage.getItem("reservas")) || [];
    reservas.push(reserva);
    localStorage.setItem("reservas", JSON.stringify(reservas));
    mostrarReservas();
});

function mostrarReservas() {
    let reservas = JSON.parse(localStorage.getItem("reservas")) || [];
    let tabla = document.getElementById("reservasTable");
    tabla.innerHTML = "";
    reservas.forEach((reserva, index) => {
        let row = `<tr>
            <td>${reserva.nombre}</td>
            <td>${reserva.habitacion}</td>
            <td>${reserva.dias}</td>
            <td>${reserva.costo}</td>
            <td><button onclick="eliminarReserva(${index})">Eliminar</button></td>
        </tr>`;
        tabla.innerHTML += row;
    });
}

function eliminarReserva(index) {
    let reservas = JSON.parse(localStorage.getItem("reservas")) || [];
    reservas.splice(index, 1);
    localStorage.setItem("reservas", JSON.stringify(reservas));
    mostrarReservas();
}

mostrarReservas();


function confirmar_eliminar(ruta){
    console.log(ruta);
    if(confirm("Está seguro? ")){
        location.href = ruta;
    }
}