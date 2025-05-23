export function createCard(product) {
    const card = document.createElement("div");
    card.classList.add("card-relationed");

    const image = document.createElement("img");
    image.src = product.image;
    image.alt = product.title;
    image.style.width = "100%";

    const title = document.createElement("h3");
    title.textContent = product.title;

    const location = document.createElement("p");
    location.textContent = `Ubicación: ${product.location}`;

    const createdAt = document.createElement("p");
    createdAt.textContent = `Publicado el: ${product.createdAt}`;

    const postedBy = document.createElement("p");
    postedBy.textContent = `Publicado por: ${product.postedBy}`;

    card.appendChild(image);
    card.appendChild(title);
    card.appendChild(location);
    card.appendChild(createdAt);
    card.appendChild(postedBy);

    return card;
}