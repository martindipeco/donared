const donaciones = [
    {
        img: "images/pesas1.jpg",        
        descripcion: "Pesa de un kilo", 
        fecha: "01/01/2025",       
        zona: "Caballito",
        nombre: "Pablo"
    },
    {
        img: "images/pantalon.jpg",       
        descripcion: "Pantalón talle 42",
        fecha: "05/02/2025",
        zona: "Palermo",
        nombre: "Lucia"
    },
    {
        img: "images/cocina_juguete.jpg",
        descripcion: "Cocina de juguetes",
        fecha: "15/03/2025",
        zona: "Once",
        nombre: "Ana"
    },
    {
        img: "images/buzo1.jpg",
        descripcion: "Buzo talle 2",
        fecha: "25/02/2025",
        zona: "Once",
        nombre: "Ignasio"
    },
    {
        img: "images/monopatin.jpg",
        descripcion: "Monopatín",
        fecha: "25/02/2025",
        zona: "San telmo",
        nombre: "Rocio"
    },
    {
        img: "images/mesa.jpg",
        descripcion: "Mesa de madera",
        fecha: "10/02/2025",
        zona: "San telmo",
        nombre: "Juan"
    }

 
   
    // Agrega más objetos para probar el "ver más"
];

let mostradas = 0;
const porPagina = 4;

function renderDonaciones() {
    const lista = document.getElementById('donaciones-lista');
    lista.innerHTML = '';
    for (let i = 0; i < mostradas && i < donaciones.length; i++) {
        const d = donaciones[i];
        lista.innerHTML += `
        <div class="donar">
            <div class="donar-card">
            <img src="${d.img}" alt="${d.descripcion}">            
            <h3>${d.descripcion}</h3>
            <p>Ubicación:${d.zona}</p>
            <p>Publicado:${d.fecha}</p>            
            <p>Publicado por:${d.nombre}</p>
            </div>
        </div>
        `;
    }
    // Oculta el botón si ya se mostraron todas
    if (mostradas >= donaciones.length) {
        document.getElementById('ver-mas-btn').style.display = 'none';
    } else {
        document.getElementById('ver-mas-btn').style.display = 'inline-block';
    }
}

function verMas() {
    mostradas += porPagina;
    renderDonaciones();
    if (mostradas >= donaciones.length) {
        document.getElementById('ver-mas-btn').style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    mostradas = porPagina;
    renderDonaciones();
    document.getElementById('ver-mas-btn').addEventListener('click', function(e) {
        e.preventDefault();
        verMas();
    });
});