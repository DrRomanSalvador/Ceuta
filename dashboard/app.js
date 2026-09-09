/**
 * Dashboard del Sistema Ceuta
 * Se conecta a la API para mostrar datos en tiempo real
 */

const API_BASE = 'http://localhost:8000';

// Estado global
let currentRisk = null;
let updateInterval = null;

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    fetchInitialData();
    startAutoRefresh();
});

async function fetchInitialData() {
    try {
        await Promise.all([
            fetchRiskData(),
            fetchSources(),
            fetchAlerts()
        ]);
    } catch (error) {
        console.error('Error fetching initial data:', error);
        showError('Error conectando con la API');
    }
}

async function fetchRiskData() {
    const response = await fetch(`${API_BASE}/risk/current`);
    const data = await response.json();
    
    currentRisk = data;
    updateRiskDisplay(data);
    updateComponents(data.component_scores);
    updateAuditInfo(data);
}

async function fetchSources() {
    const response = await fetch(`${API_BASE}/sources`);
    const sources = await response.json();
    
    const container = document.getElementById('sources-list');
    container.innerHTML = sources.map(source => `
        <div class="source-item">
            <strong>${source.name}</strong>
            <div class="source-meta">
                <span>Verificado: ${source.last_verified}</span>
                <span>Actualización: cada ${source.update_frequency_hours}h</span>
            </div>
        </div>
    `).join('');
}

async function fetchAlerts() {
    const response = await fetch(`${API_BASE}/alerts?limit=5`);
    const alerts = await response.json();
    
    const container = document.getElementById('alert-history');
    if (alerts.length === 0) {
        container.innerHTML = '<p>No hay alertas recientes</p>';
        return;
    }
    
    container.innerHTML = alerts.map(alert => `
        <div class="alert-item ${alert.level.toLowerCase()}">
            <span class="alert-level">${alert.level}</span>
            <span class="alert-message">${alert.message}</span>
            <span class="alert-time">${new Date(alert.timestamp).toLocaleString()}</span>
        </div>
    `).join('');
}

function updateRiskDisplay(data) {
    const valueEl = document.getElementById('risk-value');
    const levelEl = document.getElementById('risk-level');
    const ciEl = document.getElementById('ci-range');
    
    valueEl.textContent = data.risk_score.toFixed(4);
    levelEl.textContent = data.alert_level;
    levelEl.className = `risk-level ${data.alert_level.toLowerCase()}`;
    
    ciEl.textContent = `[${data.confidence_interval[0].toFixed(4)}, ${data.confidence_interval[1].toFixed(4)}]`;
    
    // Actualizar último update
    document.getElementById('last-update').textContent = 
        `Última actualización: ${new Date(data.calculation_timestamp).toLocaleString()}`;
}

function updateComponents(components) {
    const container = document.getElementById('components-chart');
    
    const labels = {
        'capability_growth': 'Crecimiento de Capacidades',
        'incident_count': 'Incidentes Reportados',
        'governance_gap': 'Brecha de Gobernanza',
        'awareness_level': 'Conciencia Pública',
        'international_cooperation': 'Cooperación Internacional'
    };
    
    container.innerHTML = Object.entries(components).map(([key, value]) => `
        <div class="component-bar">
            <div class="component-label">${labels[key] || key}</div>
            <div class="component-progress">
                <div class="component-fill" style="width: ${value * 100}%"></div>
            </div>
            <div class="component-value">${value.toFixed(3)}</div>
        </div>
    `).join('');
}

function updateAuditInfo(data) {
    document.getElementById('audit-hash').textContent = data.audit_hash;
    document.getElementById('config-version').textContent = '1.0.0';
    document.getElementById('source-count').textContent = data.data_sources.length;
}

function startAutoRefresh() {
    // Actualizar cada 5 minutos
    updateInterval = setInterval(async () => {
        try {
            await fetchRiskData();
            await fetchAlerts();
        } catch (error) {
            console.error('Error auto-refresh:', error);
        }
    }, 5 * 60 * 1000);
}

function showError(message) {
    // Implementar UI de error
    console.error(message);
}

// Cleanup
window.addEventListener('unload', () => {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
});
