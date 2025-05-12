document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');

    form.addEventListener('submit', async (event) => {
        try {
            if (!await validateForm()) {
                event.preventDefault(); // Evita el envío del formulario si hay errores
                alert('Por favor, completa todos los campos correctamente.'); // Alerta en rojo
            } else {
                console.log('Formulario enviado correctamente.');
                logFormData(); // Muestra los datos en la consola
            }
        } catch (error) {
            console.error('Error al validar el formulario:', error.message);
            event.preventDefault(); // Evita el envío si ocurre un error inesperado
        }
    });

    const validateForm = async () => {
        let isValid = true;

        try {
            // Validar cada campo
            isValid = validateField('email', 'El correo electrónico es obligatorio') && isValid;
            isValid = validatePattern('email', /^[^\s@]+@[^\s@]+\.[^\s@]+$/, 'El correo electrónico no es válido') && isValid;

            isValid = validateField('password', 'La contraseña es obligatoria') && isValid;

        } catch (error) {
            console.error('Error durante la validación:', error.message);
            isValid = false;
        }

        return isValid;
    };

    const validateField = (fieldId, errorMessage) => {
        try {
            const field = document.getElementById(fieldId);
            const value = field.value.trim();
            if (value === '') {
                setErrorFor(field, errorMessage);
                return false;
            } else {
                setSuccessFor(field);
                return true;
            }
        } catch (error) {
            console.error(`Error al validar el campo ${fieldId}:`, error.message);
            throw error;
        }
    };

    const validatePattern = (fieldId, pattern, errorMessage) => {
        try {
            const field = document.getElementById(fieldId);
            const value = field.value.trim();
            if (!pattern.test(value)) {
                setErrorFor(field, errorMessage);
                return false;
            } else {
                setSuccessFor(field);
                return true;
            }
        } catch (error) {
            console.error(`Error al validar el patrón del campo ${fieldId}:`, error.message);
            throw error;
        }
    };

    const setErrorFor = (input, message) => {
        const formControl = input.closest('div');
        const errorText = formControl.querySelector('.error-text');
        errorText.innerText = message;
        errorText.style.color = 'red'; // Mensaje en rojo
        input.style.borderColor = 'red'; // Borde del campo en rojo
    };

    const setSuccessFor = (input) => {
        const formControl = input.closest('div');
        const errorText = formControl.querySelector('.error-text');
        errorText.innerText = ''; // Limpia el mensaje de error
        input.style.borderColor = '#ccc'; // Restaura el borde del campo
    };

    const logFormData = () => {
        try {
            const formData = new FormData(form);
            formData.forEach((value, key) => {
                console.log(`${key}: ${value}`);
            });
        } catch (error) {
            console.error('Error al registrar los datos del formulario:', error.message);
        }
    };
});