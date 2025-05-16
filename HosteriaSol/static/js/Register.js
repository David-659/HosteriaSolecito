function validarArchivoImagen(input) {
    const archivo = input.files[0];
    const alertaError = document.getElementById('alertaError');
    
    if (archivo) {
        if (!archivo.type.startsWith('image/')) {
            alertaError.style.display = 'block';
            input.value = '';
        } else {
            alertaError.style.display = 'none';
        }
    }
}