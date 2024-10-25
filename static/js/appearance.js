document.addEventListener('DOMContentLoaded', function() {
    // Color picker functionality
    document.querySelectorAll('input[type="color"]').forEach(colorPicker => {
        ['input', 'change'].forEach(eventType => {
            colorPicker.addEventListener(eventType, function() {
                const textInput = document.querySelector(`input[data-color-input="${this.id}"]`);
                if (textInput) {
                    textInput.value = this.value.toUpperCase();
                }
            });
        });
    });

    // Reset functionality
    const form = document.getElementById('appearanceForm');
    if (form) {
        const initialValues = {};
        
        // Store initial values
        document.querySelectorAll('input[type="color"]').forEach(colorPicker => {
            initialValues[colorPicker.id] = colorPicker.value;
        });
        const fontFamilySelect = document.getElementById('font_family');
        if (fontFamilySelect) {
            initialValues['font_family'] = fontFamilySelect.value;
        }
        
        // Handle reset
        form.addEventListener('reset', function(e) {
            setTimeout(() => {
                document.querySelectorAll('input[type="color"]').forEach(colorPicker => {
                    colorPicker.value = initialValues[colorPicker.id];
                    const textInput = document.querySelector(`input[data-color-input="${colorPicker.id}"]`);
                    if (textInput) {
                        textInput.value = initialValues[colorPicker.id].toUpperCase();
                    }
                });
                if (fontFamilySelect) {
                    fontFamilySelect.value = initialValues['font_family'];
                }
            }, 0);
        });
    }
});
