// DOM Elements
const previewContainer = document.getElementById('preview-container');
const downloadBtn = document.getElementById('download-btn');
const refreshBtn = document.getElementById('refresh-btn');
const characterSetSelect = document.getElementById('character-set');
const iphoneModelSelect = document.getElementById('iphone-model');
const characterIdInput = document.getElementById('character-id');

// Current state
let currentCharacterId = null;

// Build API URL with parameters
function buildApiUrl(outputType, useCurrentId = false) {
    const params = new URLSearchParams({
        output_type: outputType,
        character_list: characterSetSelect.value,
        iphone_model: iphoneModelSelect.value
    });

    const charId = characterIdInput.value.trim();
    if (charId !== '') {
        params.set('character_id', charId);
    } else if (useCurrentId && currentCharacterId !== null) {
        params.set('character_id', currentCharacterId);
    }

    return `/hanja-api/wallpaper?${params.toString()}`;
}

// Show loading state
function showLoading() {
    previewContainer.innerHTML = `
        <div class="loading-placeholder">
            <div class="spinner-border text-light" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
}

// Fetch and display SVG preview
async function fetchPreview() {
    showLoading();
    const url = buildApiUrl('svg');
    console.log('Fetching SVG from:', url);

    try {
        const response = await fetch(url);
        console.log('Response status:', response.status);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const svgText = await response.text();
        console.log('SVG length:', svgText.length);
        previewContainer.innerHTML = svgText;

        // Extract character ID from the response headers
        const contentDisposition = response.headers.get('Content-Disposition');
        if (contentDisposition) {
            const match = contentDisposition.match(/filename=wallpaper_\w+_(\d+)\.svg/);
            if (match) {
                currentCharacterId = parseInt(match[1], 10);
            }
        }
    } catch (error) {
        console.error('Error fetching preview:', error);
        previewContainer.innerHTML = `
            <div class="loading-placeholder text-danger">
                <span>Error loading preview</span>
            </div>
        `;
    }
}

// Download PNG
function downloadPng() {
    const url = buildApiUrl('png', true);
    const link = document.createElement('a');
    link.href = url;
    link.download = `wallpaper_${characterSetSelect.value}_${currentCharacterId || 'random'}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Event Listeners
downloadBtn.addEventListener('click', downloadPng);
refreshBtn.addEventListener('click', () => {
    currentCharacterId = null;
    fetchPreview();
});

characterSetSelect.addEventListener('change', () => {
    currentCharacterId = null;
    fetchPreview();
});

iphoneModelSelect.addEventListener('change', fetchPreview);

characterIdInput.addEventListener('change', () => {
    currentCharacterId = null;
    fetchPreview();
});

// Initialize Lucide icons and fetch initial preview
document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    fetchPreview();
});
