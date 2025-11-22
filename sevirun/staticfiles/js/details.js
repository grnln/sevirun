const homeDelivery = document.getElementById('home_delivery');
const storePickup = document.getElementById('store_pickup');
const shippingInput = document.getElementById('shipping_address');
const shippingCosts = document.getElementById('shipping_costs');
const totalPrice = document.getElementById('total_price');
const subtotalPrice = document.getElementById('subtotal');
const taxElement = document.getElementById('tax'); // Renombrado para evitar conflicto
const discountElement = document.getElementById('discount'); // Renombrado para evitar conflicto

const shippingSection = shippingInput.closest('.mb-3');

function cleanAndParse(element) {
    if (!element || !element.innerText) return 0;
    const text = element.innerText
      .replace(/[€%]/g, '')
      .replace('.', '')
      .replace(',', '.')
      .trim();

    return parseFloat(text) || 0;
}

function calculateTotal(shippingFee) {
    const subtotal = cleanAndParse(subtotalPrice);
    const taxPercentage = cleanAndParse(taxElement);
    const discountAmount = cleanAndParse(discountElement);

    const baseTotal = subtotal + shippingFee - discountAmount;

    const taxMultiplier = 1 + (taxPercentage / 100);

    let finalTotal = baseTotal * taxMultiplier;

    totalPrice.innerText = finalTotal.toFixed(2) + '€';
}


function toggleShippingAddress() {
    const DELIVERY_COST = 5.00;

    if (homeDelivery && storePickup) {
        if (homeDelivery.checked) {
            console.log('Home Delivery');
            console.log()
            shippingCosts.innerText = DELIVERY_COST.toFixed(2) + '€';
            shippingSection.style.display = 'block';
            shippingInput.required = true;

            calculateTotal(DELIVERY_COST); // Recalcula con 5.00€

        } else if (storePickup.checked) {
            shippingSection.style.display = 'none';
            shippingInput.required = false;
            shippingInput.value = '';
            shippingCosts.innerText  = '0.00€';

            calculateTotal(0.00); // Recalcula con 0.00€
        }
    }
}

if (homeDelivery && storePickup) {
    homeDelivery.addEventListener('change', toggleShippingAddress);
    storePickup.addEventListener('change', toggleShippingAddress);

    toggleShippingAddress();
}