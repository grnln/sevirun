(() => {
window.updateQuantity = function(itemId, action) {
    fetch(`/cart/update-ajax/${itemId}/${action}/`)
        .then(response => response.json())
        .then(data => {
            if (data.deleted) {
                document.getElementById(`item-${itemId}`).remove();
                document.getElementById("cart-subtotal").innerText = 
                    data.subtotal.toLocaleString('es-ES', { minimumFractionDigits: 2 }) + "€";
                
                if (data.subtotal === 0) {
                    document.querySelector('.products-section').innerHTML = 
                        '<div><span>No hay productos en el carrito.</span></div>' +
                        '<a class="btn btn-primary" style="width: 15%; margin: auto auto 0 auto;" href="/products/">Ver tienda</a>';
                    document.querySelector('.cart-summary').remove();
                }
                return;
            }
            document.getElementById(`qty-${itemId}`).innerText = data.quantity;
            document.getElementById(`subtotal-${itemId}`).innerText =
                "x" + data.quantity + " = " + data.item_total.toLocaleString('es-ES', { minimumFractionDigits: 2 }) + "€";
            document.getElementById("cart-subtotal").innerText =
                data.subtotal.toLocaleString('es-ES', { minimumFractionDigits: 2 }) + "€";
        });
};})()