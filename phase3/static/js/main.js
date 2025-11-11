let cart = {};
const cartTable = document.getElementById("cart-table");
const serialButton = document.getElementById("serial-button");
var port;
var buffy = new ArrayBuffer(1);
var writer;
buffy[0]=10;

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

const connectSerialPort = async function () {
    const requestOptions = {
      // Filter on devices with the Arduino USB vendor ID.
      //filters: [{ vendorId: 0x2341 }],
    };

    // Request an Arduino from the user.
    port = await navigator.serial.requestPort(requestOptions);

    // Open and begin reading.
    await port.open({ baudrate: 9600 });
    //const reader = port.in.getReader();
    const reader = port.readable.getReader();
    writer = port.writable.getWriter();
    //const writer = port.writable.getWriter();
    //writer.write(buffy);
    while (true) {
      const {value, done} = await reader.read();
      if (done) break;
      console.log(data);
    }
} // end of function

serialButton.onclick = connectSerialPort();