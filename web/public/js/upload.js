// API Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// DOM Elements
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const fileInfo = document.getElementById('file-info');
const uploadProgress = document.getElementById('upload-progress');
const uploadResult = document.getElementById('upload-result');
const errorMessage = document.getElementById('error-message');
const progressFill = document.getElementById('progress-fill');
const progressText = document.getElementById('progress-text');
const analyzeBtn = document.getElementById('analyze-btn');

let currentSessionId = null;

// File Input Change Event
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
});

// Drag and Drop Events
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    e.stopPropagation();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', (e) => {
    e.preventDefault();
    e.stopPropagation();
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    e.stopPropagation();
    uploadArea.classList.remove('dragover');

    console.log('Drop event triggered');
    const file = e.dataTransfer.files[0];
    console.log('File:', file);

    if (file) {
        handleFile(file);
    } else {
        console.error('No file found in drop event');
    }
});

// Click to Upload
uploadArea.addEventListener('click', (e) => {
    // Don't trigger if clicking on the button itself
    if (e.target.classList.contains('btn') || e.target.closest('.file-input-label')) {
        return;
    }
    fileInput.click();
});

// Handle File
async function handleFile(file) {
    // Validate file type
    const validTypes = ['application/vnd.openxmlformats-officedocument.presentationml.presentation', 'application/pdf'];
    const validExtensions = ['.pptx', '.pdf'];

    const hasValidExtension = validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));

    if (!hasValidExtension && !validTypes.includes(file.type)) {
        showError('Endast .pptx och .pdf filer är tillåtna');
        return;
    }

    // Show file info
    displayFileInfo(file);

    // Upload file
    await uploadFile(file);
}

// Display File Info
function displayFileInfo(file) {
    document.getElementById('filename').textContent = file.name;
    document.getElementById('filesize').textContent = formatFileSize(file.size);

    const extension = file.name.split('.').pop().toUpperCase();
    document.getElementById('filetype').textContent = extension;

    fileInfo.style.display = 'block';
    errorMessage.style.display = 'none';
    uploadResult.style.display = 'none';
}

// Upload File
async function uploadFile(file) {
    console.log('Starting upload for file:', file.name);

    const formData = new FormData();
    formData.append('file', file);

    // Show progress
    uploadProgress.style.display = 'block';
    progressFill.style.width = '0%';
    progressText.textContent = 'Laddar upp...';

    try {
        // Simulate progress
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += 10;
            if (progress <= 90) {
                progressFill.style.width = progress + '%';
            }
        }, 100);

        console.log('Sending request to:', `${API_BASE_URL}/upload`);

        // Upload
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData,
        });

        clearInterval(progressInterval);
        progressFill.style.width = '100%';

        console.log('Response status:', response.status);

        if (!response.ok) {
            const error = await response.json();
            console.error('Upload error:', error);
            throw new Error(error.detail || 'Upload failed');
        }

        const result = await response.json();
        console.log('Upload successful:', result);
        currentSessionId = result.session_id;

        // Show success
        progressText.textContent = 'Uppladdning slutförd!';
        setTimeout(() => {
            uploadProgress.style.display = 'none';
            showSuccess(result);
        }, 500);

    } catch (error) {
        console.error('Upload exception:', error);
        uploadProgress.style.display = 'none';
        showError(`Uppladdning misslyckades: ${error.message}`);
    }
}

// Show Success
function showSuccess(result) {
    document.getElementById('session-id').textContent = result.session_id;
    uploadResult.style.display = 'block';
}

// Show Error
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    uploadProgress.style.display = 'none';
    uploadResult.style.display = 'none';
}

// Format File Size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Analyze Button Click
analyzeBtn.addEventListener('click', async () => {
    if (currentSessionId) {
        await startAnalysis();
    }
});

// Get Selected Rules
function getSelectedRules() {
    const checkboxes = document.querySelectorAll('.rule-checkbox input[type="checkbox"]:checked');
    return Array.from(checkboxes).map(cb => cb.dataset.rule);
}

// Start Analysis
async function startAnalysis() {
    console.log('Starting analysis for session:', currentSessionId);

    // Hide upload result, show analysis section
    uploadResult.style.display = 'none';
    document.getElementById('analysis-section').style.display = 'block';
    document.getElementById('results-section').style.display = 'none';

    // Get selected rules
    const enabledRules = getSelectedRules();
    console.log('Enabled rules:', enabledRules);

    // Simulate progress
    const progressFill = document.getElementById('analysis-progress-fill');
    const statusText = document.getElementById('analysis-status');

    progressFill.style.width = '10%';
    statusText.textContent = 'Analyserar presentation...';

    try {
        // Send analysis request
        const response = await fetch(`${API_BASE_URL}/analysis/${currentSessionId}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                enabled_rules: enabledRules,
                config: {}
            }),
        });

        progressFill.style.width = '50%';

        if (!response.ok) {
            const error = await response.json();
            console.error('Analysis error:', error);
            throw new Error(error.detail || 'Analysis failed');
        }

        const result = await response.json();
        console.log('Analysis complete:', result);

        progressFill.style.width = '100%';
        statusText.textContent = 'Analys slutförd!';

        // Show results after a brief delay
        setTimeout(() => {
            displayResults(result);
        }, 500);

    } catch (error) {
        console.error('Analysis exception:', error);
        document.getElementById('analysis-section').style.display = 'none';
        showError(`Analys misslyckades: ${error.message}`);
    }
}

// Display Analysis Results
function displayResults(result) {
    console.log('Displaying results:', result);

    // Hide analysis progress
    document.getElementById('analysis-section').style.display = 'none';

    // Show results section
    const resultsSection = document.getElementById('results-section');
    resultsSection.style.display = 'block';

    // Display scores
    const scores = result.scores;
    document.getElementById('overall-score').textContent = scores.overall_score;
    document.getElementById('grade').textContent = scores.grade;
    document.getElementById('total-findings').textContent = scores.total_issues;
    document.getElementById('findings-per-slide').textContent = scores.issues_per_slide;

    // Display severity counts
    const severityCounts = result.findings_by_severity;
    document.getElementById('count-critical').textContent = severityCounts.critical || 0;
    document.getElementById('count-high').textContent = severityCounts.high || 0;
    document.getElementById('count-medium').textContent = severityCounts.medium || 0;
    document.getElementById('count-low').textContent = severityCounts.low || 0;
    document.getElementById('count-info').textContent = severityCounts.info || 0;

    // Add color coding to score circle based on grade
    const scoreCircle = document.querySelector('.score-circle');
    scoreCircle.className = 'score-circle grade-' + scores.grade.toLowerCase();

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// New Analysis Button
document.getElementById('new-analysis-btn').addEventListener('click', () => {
    location.reload();
});

// View Findings Button
document.getElementById('view-findings-btn').addEventListener('click', async () => {
    if (currentSessionId) {
        alert('Detaljerad fyndgranskning kommer i nästa fas!\n\nDu kommer att kunna:\n- Se alla fynd slide för slide\n- Godkänna/avvisa varje förslag\n- Regenerera AI alt-texter\n- Exportera rapport');
        // TODO: Implement findings review in next phase
    }
});
