document.addEventListener('DOMContentLoaded', () => {
    console.log('WildlifeID Ready!');

    // Smooth Page Entry
    document.body.classList.add('fade-in');

    // Prediction Form Handler
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', handlePrediction);
    }

    // Image Input Handler
    const imageInput = document.getElementById('imageInput');
    if (imageInput) {
        imageInput.addEventListener('change', previewImage);
    }

    // Drag and Drop Handler
    const dropZone = document.getElementById('dropZone');
    if (dropZone) {
        ['dragover', 'dragleave', 'drop'].forEach(evt => {
            dropZone.addEventListener(evt, e => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        dropZone.addEventListener('drop', e => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                imageInput.files = files;
                previewImage({ target: { files: files } });
            }
        });
    }
});

/**
 * Handle image prediction via AJAX
 */
async function handlePrediction(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const resultDiv = document.getElementById('prediction-result');
    const submitBtn = form.querySelector('button[type="submit"]');

    // Show loading state
    setLoading(true, submitBtn);

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            showToast('error', data.error);
        } else {
            showPrediction(data);
            showToast('success', 'Prediction Successful!');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('error', 'Something went wrong. Please try again.');
    } finally {
        setLoading(false, submitBtn);
    }
}

/**
 * Update UI with prediction results
 */
function showPrediction(data) {
    const resultDiv = document.getElementById('prediction-result');
    if (!resultDiv) return;

    resultDiv.innerHTML = `
        <div class="card border-0 shadow-md slide-up overflow-hidden">
            <div class="row g-0">
                <div class="col-md-5">
                    <img src="${data.reference_image}" class="img-fluid h-100 object-fit-cover" 
                         alt="${data.prediction}" style="min-height: 250px;">
                </div>
                <div class="col-md-7">
                    <div class="card-body p-4 d-flex flex-column justify-content-center">
                        <div class="mb-2">
                            <span class="badge bg-success bg-opacity-10 text-success rounded-pill px-3">Identified Species</span>
                        </div>
                        <h2 class="display-6 fw-bold mb-1">${data.prediction}</h2>
                        <div class="text-muted mb-4">
                            Matching Confidence: <strong>${(data.confidence * 100).toFixed(1)}%</strong>
                        </div>
                        
                        <div class="progress mb-4" style="height: 8px;">
                            <div class="progress-bar bg-success" style="width: ${data.confidence * 100}%"></div>
                        </div>
                        
                        <div class="d-flex gap-2 mt-auto">
                            <button class="btn btn-primary px-4 py-2" onclick="window.location.reload()">
                                <i class="fas fa-redo me-2"></i> New Discovery
                            </button>
                            <a href="/history" class="btn btn-outline-secondary px-4 py-2">
                                Track Logs
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    resultDiv.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Preview image before upload
 */
function previewImage(e) {
    const file = e.target.files[0];
    const preview = document.getElementById('imagePreview');
    const placeholder = document.getElementById('uploadPlaceholder');
    const predictBtn = document.getElementById('predictBtn');

    if (!file || !preview) return;

    const reader = new FileReader();
    reader.onload = (event) => {
        preview.src = event.target.result;
        preview.classList.remove('d-none');
        if (placeholder) placeholder.classList.add('d-none');
        if (predictBtn) predictBtn.disabled = false;
    };
    reader.readAsDataURL(file);
}

/**
 * UI State Helpers
 */
function setLoading(isLoading, btn) {
    if (isLoading) {
        btn.disabled = true;
        btn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span> Identifying...`;
        document.body.style.cursor = 'wait';
    } else {
        btn.disabled = false;
        btn.innerHTML = `<i class="fas fa-paw me-2"></i> Identify Now`;
        document.body.style.cursor = 'default';
    }
}

function showToast(type, message) {
    // Using standard alert if no toast system matches
    // But we'll implement a simple one or use existing bootstrap alerts
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'error' ? 'danger' : 'success'} alert-dismissible fade show slide-up`;
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 500);
    }, 5000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.style.position = 'fixed';
    container.style.top = '20px';
    container.style.right = '20px';
    container.style.zIndex = '9999';
    container.style.width = '300px';
    document.body.appendChild(container);
    return container;
}

/**
 * Animal Info Utility
 */
const animalInfo = {
    "Lion": { habitat: "Savannah", threat_status: "Vulnerable" },
    "Tiger": { habitat: "Jungle", threat_status: "Endangered" },
    // Will be populated based on model classes
};
