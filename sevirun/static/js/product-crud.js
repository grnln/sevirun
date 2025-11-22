// Handle tab activation from URL query parameter
document.addEventListener("DOMContentLoaded", function () {
    const params = new URLSearchParams(window.location.search);
    const tab = params.get('tab');
    
    if (tab) {
        document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('show', 'active'));
        
        const tabButton = document.getElementById(`${tab}-tab`);
        const tabPane = document.getElementById(tab);
        
        if (tabButton && tabPane) {
            tabButton.classList.add('active');
            tabPane.classList.add('show', 'active');
        }
    }
    
    setFormActions();
});

function setFormActions() {
    const forms = [
        { id: 'brandForm', tab: 'brands' },
        { id: 'modelForm', tab: 'models' },
        { id: 'typeForm', tab: 'types' },
        { id: 'materialForm', tab: 'materials' },
        { id: 'sizeForm', tab: 'sizes' },
        { id: 'colourForm', tab: 'colours' }
    ];
    
    forms.forEach(({ id, tab }) => {
        const form = document.getElementById(id);
        if (form) {
            form.addEventListener('submit', function (e) {
                e.preventDefault();
                const url = form.dataset.createUrl + `?tab=${tab}`;
                form.action = url;
                form.method = 'POST';
                form.submit();
            });
        }
    });
}