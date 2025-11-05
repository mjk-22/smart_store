let cart = {};
const cartTable = document.getElementById("cart-table");


function renderCart() {
    cartTable.innerHTML = `
        <tr>
            <th>Name</th>
            <th>Quantity</th>
            <th>Price</th>
        </tr>
    `;

    Object.entries(cart).forEach(([productID, item]) => {
        cartTable.innerHTML += `
        <tr>
            <td>${item.name}</td>
            <td>${item.quantity}</td>
            <td>$${item.price}</td>
            <td>
                <button onclick="removeFromCart('${productID}')">
                    Remove From Cart
                </button>
            </td>
        </tr>
        `
    });
}

function addToCart(productID, name, price, stock) {
    if (!cart[productID] && stock > 0) {
        cart[productID] = {name, price, quantity: 1};
    } else {
        if (cart[productID].quantity != stock) {
        cart[productID].quantity += 1;
        }
    }
    renderCart();
}

function removeFromCart(productID) {
    if (cart[productID]) {
        cart[productID].quantity -= 1;
        if (cart[productID].quantity <= 0) {
            delete cart[productID];
        }
        renderCart();
    }
}