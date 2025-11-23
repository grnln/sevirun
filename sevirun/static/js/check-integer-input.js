window.validateIntegerInput = function(elementId, defaultValue = 1, minValue = 1, allowEmpty = false) {
    const element = document.getElementById(elementId);
    
    if (!element) {
        console.error(`Elemento con ID "${elementId}" no encontrado`);
        return;
    }
    
    element.addEventListener('input', function(e) {
        this.value = this.value.replace(/[^0-9]/g, '');
        
        if (allowEmpty && this.value === '') {
            return;
        }
        
        if (!this.value || isNaN(this.value) || this.value === '') {
            this.value = defaultValue;
            return;
        }
        
        let intValue = Math.floor(parseInt(this.value));
        
        if (intValue < minValue) {
            this.value = minValue;
        } else {
            this.value = intValue;
        }
    });
    
    element.addEventListener('blur', function(e) {
        if (allowEmpty && this.value === '') {
            return;
        }
        
        if (!this.value || isNaN(this.value) || this.value < minValue) {
            this.value = defaultValue;
        }
    });
    
    const form = element.closest('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            if (allowEmpty && element.value === '') {
                return;
            }
            
            if (!element.value || isNaN(element.value) || element.value < minValue) {
                element.value = defaultValue;
            }
        });
    }
};