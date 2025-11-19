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

    if (cart != null) {
        cartTable.innerHTML += `
        <tr>
            <button onclick="checkout()">
                Checkout
            </button>
        </tr>
        `
    }
}

function addToCart(product) {
    const productID = product.id;
    if (!cart[productID] && stock > 0) {
        cart[productID] = {name: product.name,
            price: product.price,
            quantity: 1,
            stock: product.stock};
    } else {
        if (cart[productID].quantity != stock) {
        cart[productID].quantity += 1;
        }
    }
    renderCart();
}

function searchEPC() {
    const epc = document.getElementById("code_search").value;

    fetch("", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify({
            action: "epc_search",
            epc: epc
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            addToCart(data);
        } else {
            alert("Product not found");
        }
    });
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

function checkout() {
    fetch("", {
        method: "POST",
        headers: {
            "Content-Type":"application/json",
            "X-CSRFToken":getCSRFToken()
        },
        body: JSON.stringify({
            action: "checkout",
            cart: cart
        })
    })
    .then(response => response.json())
    .then(data => {
    if (data.success) {
        window.location.href = data.redirect_url;
    } else {
        alert(data.error);
    }
})
}


function getCSRFToken() {
    const name = "csrftoken=";
    const decoded = decodeURIComponent(document.cookie);
    const cookies = decoded.split("; ");
    for (let c of cookies) {
        if (c.startsWith(name)) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}