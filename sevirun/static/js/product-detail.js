(function () {
    function qs(id) { return document.getElementById(id); }

    document.addEventListener('DOMContentLoaded', function () {
        const stockScript = document.getElementById('product-stock-data');
        const availScript = document.getElementById('product-available');
        let stockList = [];
        let productAvailable = true;

        if (stockScript) {
            try { stockList = JSON.parse(stockScript.textContent || '[]'); } catch (e) { stockList = []; }
        }
        if (availScript) {
            try { productAvailable = JSON.parse(availScript.textContent); } catch (e) { productAvailable = true; }
        }

        // Build dict: sizeid_colourid -> stock
        const stockMap = {};
        stockList.forEach(function (it) {
            const key = (it.size_id || '') + '_' + (it.colour_id || '');
            stockMap[key] = (it.stock || 0);
        });

        const sizeSelect = qs('size-select');
        const colorSelect = qs('color-select');
        const cartButton = document.querySelector('button[aria-label="Añadir al carrito"]');

        function updateColorsForSize() {
            const sizeId = sizeSelect ? sizeSelect.value : '';
            Array.from(colorSelect.options).forEach(function (opt) {
                if (!opt.value) { opt.disabled = false; return; }
                let disabled = true;
                if (!sizeId) {
                    const total = parseInt(opt.getAttribute('data-stock') || '0');
                    disabled = (total === 0) || (!productAvailable);
                    opt.disabled = disabled;

                    const base = opt.getAttribute('data-original-text') || opt.textContent.replace(/\s*\(Agotado\)\s*$/i, '');
                    opt.text = base + (disabled ? ' (Agotado)' : '');
                } else {
                    const key = sizeId + '_' + opt.value;
                    const s = stockMap[key] || 0;
                    disabled = (s === 0);
                }

                opt.disabled = disabled;
                const base = opt.getAttribute('data-original-text') || opt.textContent.replace(/\s*\(Agotado\)\s*$/i, '');
                opt.text = base + (disabled ? ' (Agotado)' : '');
            });
        }

        function updateSizesForColor() {
            const colourId = colorSelect ? colorSelect.value : '';
            Array.from(sizeSelect.options).forEach(function (opt) {
                if (!opt.value) { opt.disabled = false; return; }
                let unavailable = false;
                if (!colourId) {
                    const tot = parseInt(opt.getAttribute('data-stock') || '0', 10);
                    unavailable = (tot === 0) || (!productAvailable);
                } else {
                    const key = opt.value + '_' + colourId;
                    const s = stockMap[key] || 0;
                    unavailable = (s === 0);
                    opt.disabled = false;
                }
                const base = opt.getAttribute('data-original-text') || opt.textContent.replace(/\s*\(Agotado\)\s*$/i, '');
                opt.text = base + (unavailable ? ' (Agotado)' : '');
            });
        }

        function updateAddButton() {
            if (!productAvailable) { cartButton.disabled = true; return; }
            const sizeOk = (sizeSelect.value && sizeSelect.value !== '');
            const colorOk = (colorSelect.value && colorSelect.value !== '');
            cartButton.disabled = !(sizeOk && colorOk);
        }

        // Reseter for colors when size changes and color not available for new size
        if (sizeSelect) sizeSelect.addEventListener('change', function(){
            updateColorsForSize();
            if (colorSelect && colorSelect.value) {
                const selOpt = colorSelect.querySelector('option[value="' + CSS.escape(colorSelect.value) + '"]');
                if (selOpt && selOpt.disabled) {
                    colorSelect.value = '';
                    updateSizesForColor();
                }
            }
            updateAddButton();
        });

        // Update sizes when color changes
        if (colorSelect) colorSelect.addEventListener('change', function(){
            updateSizesForColor();
            updateAddButton();
        });

        // Init
        updateColorsForSize();
        updateSizesForColor();
        updateAddButton();
    });
})();
