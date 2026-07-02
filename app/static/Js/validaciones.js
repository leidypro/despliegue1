document.addEventListener('input', function (e) {
	if (e.target.id === "id_descripcion"){
		const error = document.getElementById("error_Descripcion")
		error.innerText = ""
		if (e.target.value.length < 10) {
			error.innerText = "la descripción es demasiado muy corta"
			error.classList.add('text-danger')
		}
		if (e.target.value.length > 200) {
			error.innerText = "La descripción no puede superar los 200 caracteres"
			error.classList.add('text-danger')
		}
		if (e.target.value.length == 0) {
			error.innerText = "la descripción no puede estar vacia"
			error.classList.add('text-danger')
		}


	}

	// TÍTULO

	if (e.target.id === "id_titulo"){
		const error = document.getElementById("error_Titulo")
		error.innerText = ""

		if (/^\d+$/.test(e.target.value)){
			error.innerText = "El título no puede contener solo números"
			error.classList.add('text-danger')
		}

		if (!/^[a-zA-ZÁÉÍÓÚáéíóúÑñ0-9 ]+$/.test(e.target.value)){
			error.innerText = "El título no puede contener caracteres especiales"
			error.classList.add('text-danger')
		}
		if (e.target.value.length < 5) {
			error.innerText = "título muy corto"
			error.classList.add('text-danger')
		}
		if (e.target.value.length > 20) {
			error.innerText = "el título no puede superar los 20 caracteres"
			error.classList.add('text-danger')
		}
		if (e.target.value.length == 0) {
			error.innerText = "el título no puede estar vacio"
			error.classList.add('text-danger')
		}
	}


	// FECHA INICIO

	if (e.target.id === "id_fecha_inicio"){
		const error = document.getElementById("error_Fecha inicio")
		error.innerText = ""

		if (e.target.value){
			const fechaInicio = new Date(e.target.value)
			const ahora = new Date()

			if (fechaInicio < ahora){
				error.innerText = "La fecha de inicio no puede ser una fecha pasada"
				error.classList.add('text-danger')
			}
		}
	}

	// VALIDACIÓN FECHA FIN
    if (e.target.id === "id_fecha_fin") {
        const error = document.getElementById("error_Fecha fin");
        error.innerText = "";

        const fechaInicio = document.getElementById("id_fecha_inicio").value;
        const fechaFin = e.target.value;

        if (fechaInicio && fechaFin) {
            if (new Date(fechaFin) <= new Date(fechaInicio)) {
                error.innerText = "La fecha de fin debe ser mayor que la fecha de inicio";
				error.classList.add('text-danger')
            }
        }
    }

});

