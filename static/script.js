document.addEventListener('DOMContentLoaded', () => {
    const knobs = document.querySelectorAll('.knob');

    knobs.forEach(knob => {
        // --- Identificadores específicos para esta perilla ---
        const effectName = knob.dataset.effect; // Ej: 'dist', 'chorus', etc.
        const valueDisplay = document.getElementById(`${effectName}-value`); // Ej: 'dist-value'
        const hiddenInput = document.getElementById(`${effectName}-hidden-input`); // Ej: 'dist-hidden-input'
        
        // --- Estado inicial y rango (igual que antes) ---
        let currentAngle = -135; // Ángulo inicial (0%)
        const minAngle = -135;
        const maxAngle = 135;
        const angleRange = maxAngle - minAngle;
        let isDragging = false;
        let startRotationAngle = 0; // Para calcular el offset del drag

        // --- Función para actualizar todo ---
        function updateKnobVisuals(angle) {
            angle = Math.max(minAngle, Math.min(maxAngle, angle));
            const value = (angle - minAngle) / angleRange;
            const percentage = Math.round(value * 100);

            knob.style.transform = `rotate(${angle}deg)`;
            
            // --- Actualizar elementos específicos ---
            if (valueDisplay) {
                valueDisplay.textContent = `${percentage}%`;
            }
            if (hiddenInput) {
                hiddenInput.value = value.toFixed(2); // Guardar valor 0.00 a 1.00
            }
            knob.dataset.value = value.toFixed(2); 
            currentAngle = angle;
        }

        // --- Eventos del Mouse ---
        knob.addEventListener('mousedown', (e) => {
            isDragging = true;
            // Calcular el ángulo inicial del clic relativo al ángulo actual de la perilla
            const rect = knob.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;
            const clickAngle = Math.atan2(e.clientY - centerY, e.clientX - centerX) * (180 / Math.PI);
            startRotationAngle = clickAngle - currentAngle; 
            
            knob.style.cursor = 'grabbing';
            e.preventDefault(); // Evitar seleccionar texto mientras se arrastra
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;

            const rect = knob.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;
            // Calcular el ángulo actual del mouse relativo al centro
            const currentMouseAngle = Math.atan2(e.clientY - centerY, e.clientX - centerX) * (180 / Math.PI);
            // El nuevo ángulo de la perilla es el ángulo del mouse menos el offset inicial
            let newAngle = currentMouseAngle - startRotationAngle;

            // --- Normalización (opcional pero recomendada para evitar saltos) ---
            // Si el ángulo salta de >180 a <-180 o viceversa (cruzando el límite -180/180)
            const angleDiff = newAngle - currentAngle;
            if (Math.abs(angleDiff) > 180) {
                 // Ajustar sumando/restando 360 grados para suavizar el salto
                 newAngle += (angleDiff > 0 ? -360 : 360);
            }
           
            updateKnobVisuals(newAngle);
        });

        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                knob.style.cursor = 'pointer';
            }
        });
        
        // --- Inicializar la perilla en 0% ---
        // Asegurarse de que el valor inicial del input oculto sea 0 si no lo es ya
        if (hiddenInput && hiddenInput.value !== "0.00") {
             hiddenInput.value = "0.00";
        }
        updateKnobVisuals(minAngle); 
    });
});
