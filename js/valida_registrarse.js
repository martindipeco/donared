document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');

    form.addEventListener('submit', async (event) => {
        try {
            if (!(await validateForm())) {
                event.preventDefault(); 
                /*alert('Por favor, completa todos los campos correctamente.'); */
            } else {
                /*console.log('Formulario enviado correctamente.');*/
                logFormData(); 
            }
        } catch (error) {
            console.error('Error al validar el formulario:', error.message);
            event.preventDefault(); 
        }
    });

    const validateForm = async () => {
        let isValid = true;

        try {
            // Validar campos obligatorios
            isValid = await validateField('nombre', 'El nombre es obligatorio') && isValid;
            isValid = await validateField('apellido', 'El apellido es obligatorio') && isValid;
            isValid = await validateField('dni', 'El número de documento es obligatorio') && isValid;
            isValid = await validateField('fechaNac', 'La fecha de nacimiento es obligatoria') && isValid;
            isValid = await validateField('email', 'El correo electrónico es obligatorio') && isValid;
            isValid = await validateField('codigoArea', 'El código de área es obligatorio') && isValid;
            isValid = await validateField('celular', 'El número de celular es obligatorio') && isValid;
            isValid = await validateField('zonas', 'Seleccionar una zona') && isValid;
            isValid = await validateField('localidad', 'La localidad es obligatoria') && isValid;
            isValid = await validateField('codPostal', 'El código postal es obligatorio') && isValid;
            isValid = await validateField('password', 'La contraseña es obligatoria') && isValid;
            isValid = await validateField('repetirPassword', 'Debes repetir la contraseña') && isValid;

            // Validar formato del DNI (8 caracteres numéricos)
            isValid = await validatePattern('dni', /^\d{8}$/, 'El número de documento Debe tener 8 números') && isValid;

            // Validar formato del correo electrónico
            isValid = await validatePattern('email', /^[^\s@]+@[^\s@]+\.[^\s@]+$/, 'El correo electrónico no es válido') && isValid;

            // Validar formato del código de área (3 caracteres numéricos)
            isValid = await validatePattern('codigoArea', /^\d{3}$/, 'El código de área debe tener 3 números') && isValid;

            // Validar formato del celular (8 caracteres numéricos)
            isValid = await validatePattern('celular', /^\d{8}$/, 'El número de celular debe tener 8 números') && isValid;

            // Validar formato del código postal (4 caracteres numéricos)
            isValid = await validatePattern('codPostal', /^\d{4}$/, 'El código postal debe tener 4 números') && isValid;

            // Validar formato de la contraseña (mínimo 8 caracteres, al menos una mayúscula, una minúscula y un número)
            isValid = await validatePattern(
                'password',
                /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$/,
                'La contraseña debe tener al menos 8 caracteres, una letra mayúscula, una minúscula y un número'
            ) && isValid;

            // Validar que las contraseñas coincidan
            isValid = await validatePasswordsMatch('password', 'repetirPassword', 'Las contraseñas no coinciden') && isValid;

        } catch (error) {
            console.error('Error durante la validación:', error.message);
            isValid = false;
        }

        return isValid;
    };

    const validateField = async (fieldId, errorMessage) => {
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

    const validatePattern = async (fieldId, pattern, errorMessage) => {
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

    const validatePasswordsMatch = async (passwordId, repeatPasswordId, errorMessage) => {
        try {
            const password = document.getElementById(passwordId).value.trim();
            const repeatPassword = document.getElementById(repeatPasswordId).value.trim();
            if (password !== repeatPassword) {
                setErrorFor(document.getElementById(repeatPasswordId), errorMessage);
                return false;
            } else {
                setSuccessFor(document.getElementById(repeatPasswordId));
                return true;
            }
        } catch (error) {
            console.error('Error al validar las contraseñas:', error.message);
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
