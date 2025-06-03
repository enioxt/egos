/**
 * EGOS System - ATRiAN Module: Trust Visualization Component
 * Version: 1.0
 * Last Modified: 2025-05-27
 *
 * Purpose:
 * This module provides visualization components for displaying trust levels
 * and trust history for users interacting with the Windsurf IDE. It implements
 * the visual representation of the Reciprocal Trust principle.
 *
 * MQP Alignment:
 * - Reciprocal Trust (RT): Visualizes trust relationships
 * - Compassionate Temporality (CT): Shows trust evolution over time
 * - Universal Accessibility (UA): Ensures visualizations are accessible
 * - Integrated Ethics (IE/ETHIK): Links trust to ethical behavior
 *
 * Cross-references:
 * - @references {C:\EGOS\ATRiAN\atrian_windsurf_adapter.py}
 * - @references {C:\EGOS\ATRiAN\atrian_trust_weaver.py}
 * - @references {C:\EGOS\ATRiAN\ui\notification_panel.js}
 * - @references {C:\EGOS\run_tools.py}
 * - @references {C:\EGOS\scripts\system_health\core\validator.py}
 * --- 
 */

(function(window, document) {
    'use strict';

    // Configuration
    const CONFIG = {
        CONTAINER_ID: 'atrian-trust-visualization',
        INDICATOR_ID: 'atrian-trust-indicator',
        CHART_ID: 'atrian-trust-chart',
        STORAGE_KEY: 'atrian_trust_history',
        POLL_INTERVAL: 60000, // 1 minute
        COLORS: {
            HIGH: '#27ae60',   // Green
            MEDIUM: '#f39c12', // Orange
            LOW: '#e74c3c',    // Red
            CHART_LINE: '#3498db',
            CHART_FILL: 'rgba(52, 152, 219, 0.2)',
            CHART_EVENTS: {
                POSITIVE: 'rgba(46, 204, 113, 0.5)',
                NEGATIVE: 'rgba(231, 76, 60, 0.5)'
            }
        },
        TRUST_LEVELS: {
            HIGH: { min: 0.8, label: 'High Trust' },
            MEDIUM: { min: 0.5, label: 'Medium Trust' },
            LOW: { min: 0.0, label: 'Low Trust' }
        },
        MAX_HISTORY_POINTS: 100,
        MAX_HISTORY_DAYS: 30
    };

    // State
    const state = {
        initialized: false,
        container: null,
        indicator: null,
        chart: null,
        chartContext: null,
        chartInstance: null,
        currentTrust: 0.7, // Default starting trust
        trustHistory: [],
        eventHistory: [],
        pollInterval: null,
        adapter: null
    };

    /**
     * Initialize the trust visualization component.
     * @param {Object} options - Configuration options
     * @param {Element} options.container - Container element (optional)
     * @param {Object} options.adapter - ATRiANWindsurfAdapter instance (optional)
     */
    function initialize(options = {}) {
        if (state.initialized) return;
        
        // Store adapter reference if provided
        if (options.adapter) {
            state.adapter = options.adapter;
        }
        
        // Create or use container
        if (options.container) {
            state.container = options.container;
        } else if (!document.getElementById(CONFIG.CONTAINER_ID)) {
            state.container = document.createElement('div');
            state.container.id = CONFIG.CONTAINER_ID;
            document.body.appendChild(state.container);
        } else {
            state.container = document.getElementById(CONFIG.CONTAINER_ID);
        }
        
        // Load styles
        loadStyles();
        
        // Create components
        createTrustIndicator();
        createTrustChart();
        
        // Load history from storage
        loadTrustHistory();
        
        // Start polling for updates
        startPolling();
        
        state.initialized = true;
        console.log('ATRiAN Trust Visualization initialized');
    }

    /**
     * Load component styles.
     */
    function loadStyles() {
        const style = document.createElement('style');
        style.textContent = `
            #${CONFIG.CONTAINER_ID} {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                padding: 10px;
                background-color: #f9f9f9;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                margin-bottom: 15px;
            }
            
            #${CONFIG.INDICATOR_ID} {
                display: flex;
                align-items: center;
                margin-bottom: 15px;
            }
            
            .trust-level-label {
                font-weight: bold;
                margin-right: 10px;
            }
            
            .trust-progress-container {
                flex-grow: 1;
                height: 10px;
                background-color: #eee;
                border-radius: 5px;
                overflow: hidden;
                position: relative;
            }
            
            .trust-progress-bar {
                height: 100%;
                border-radius: 5px;
                transition: width 0.5s ease, background-color 0.5s ease;
            }
            
            .trust-progress-low {
                background-color: ${CONFIG.COLORS.LOW};
            }
            
            .trust-progress-medium {
                background-color: ${CONFIG.COLORS.MEDIUM};
            }
            
            .trust-progress-high {
                background-color: ${CONFIG.COLORS.HIGH};
            }
            
            .trust-value {
                margin-left: 10px;
                font-weight: bold;
                min-width: 45px;
                text-align: right;
            }
            
            #${CONFIG.CHART_ID}-container {
                position: relative;
                height: 150px;
                margin-top: 10px;
            }
            
            #${CONFIG.CHART_ID} {
                width: 100%;
                height: 100%;
            }
            
            .trust-chart-tooltip {
                background-color: rgba(0, 0, 0, 0.7);
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
                font-size: 12px;
                pointer-events: none;
                position: absolute;
                z-index: 10;
                white-space: nowrap;
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Create the trust indicator element.
     */
    function createTrustIndicator() {
        // Create indicator container
        const indicator = document.createElement('div');
        indicator.id = CONFIG.INDICATOR_ID;
        
        // Create label
        const label = document.createElement('div');
        label.className = 'trust-level-label';
        label.textContent = 'Trust Level:';
        indicator.appendChild(label);
        
        // Create progress bar container
        const progressContainer = document.createElement('div');
        progressContainer.className = 'trust-progress-container';
        
        // Create progress bar
        const progressBar = document.createElement('div');
        progressBar.className = 'trust-progress-bar';
        progressContainer.appendChild(progressBar);
        indicator.appendChild(progressContainer);
        
        // Create value display
        const value = document.createElement('div');
        value.className = 'trust-value';
        indicator.appendChild(value);
        
        // Add to container
        state.container.appendChild(indicator);
        state.indicator = indicator;
        
        // Update initial display
        updateTrustIndicator(state.currentTrust);
    }

    /**
     * Create the trust chart element.
     */
    function createTrustChart() {
        // Create chart container
        const chartContainer = document.createElement('div');
        chartContainer.id = `${CONFIG.CHART_ID}-container`;
        
        // Create canvas for chart
        const canvas = document.createElement('canvas');
        canvas.id = CONFIG.CHART_ID;
        chartContainer.appendChild(canvas);
        
        // Add to container
        state.container.appendChild(chartContainer);
        
        // Initialize chart if Chart.js is available
        if (window.Chart) {
            initializeChart(canvas);
        } else {
            // Load Chart.js if not already available
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js';
            script.onload = function() {
                initializeChart(canvas);
            };
            document.head.appendChild(script);
        }
    }

    /**
     * Initialize the chart with Chart.js.
     * @param {HTMLCanvasElement} canvas - Canvas element for the chart
     */
    function initializeChart(canvas) {
        state.chartContext = canvas.getContext('2d');
        
        const labels = state.trustHistory.map(point => {
            const date = new Date(point.timestamp);
            return `${date.getMonth()+1}/${date.getDate()} ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
        });
        
        const data = state.trustHistory.map(point => point.value);
        
        state.chartInstance = new Chart(state.chartContext, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Trust Score',
                    data: data,
                    borderColor: CONFIG.COLORS.CHART_LINE,
                    backgroundColor: CONFIG.COLORS.CHART_FILL,
                    tension: 0.3,
                    pointRadius: 3,
                    pointHoverRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        min: 0,
                        max: 1,
                        ticks: {
                            callback: function(value) {
                                return value.toFixed(1);
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const point = state.trustHistory[context.dataIndex];
                                let label = `Trust: ${point.value.toFixed(2)}`;
                                
                                // Add event information if available
                                if (point.event) {
                                    label += ` (${point.event.type}: ${point.event.description})`;
                                }
                                
                                return label;
                            }
                        }
                    }
                }
            }
        });
    }

    /**
     * Update the trust indicator with a new trust value.
     * @param {number} trustValue - Trust value (0.0 to 1.0)
     */
    function updateTrustIndicator(trustValue) {
        // Store the value
        state.currentTrust = trustValue;
        
        // Get the indicator elements
        const progressBar = state.indicator.querySelector('.trust-progress-bar');
        const valueDisplay = state.indicator.querySelector('.trust-value');
        
        // Update progress bar width
        progressBar.style.width = `${trustValue * 100}%`;
        
        // Update progress bar class based on trust level
        progressBar.classList.remove('trust-progress-low', 'trust-progress-medium', 'trust-progress-high');
        let levelClass, levelLabel;
        
        if (trustValue >= CONFIG.TRUST_LEVELS.HIGH.min) {
            levelClass = 'trust-progress-high';
            levelLabel = CONFIG.TRUST_LEVELS.HIGH.label;
        } else if (trustValue >= CONFIG.TRUST_LEVELS.MEDIUM.min) {
            levelClass = 'trust-progress-medium';
            levelLabel = CONFIG.TRUST_LEVELS.MEDIUM.label;
        } else {
            levelClass = 'trust-progress-low';
            levelLabel = CONFIG.TRUST_LEVELS.LOW.label;
        }
        
        progressBar.classList.add(levelClass);
        
        // Update value display
        valueDisplay.textContent = `${(trustValue * 100).toFixed(0)}% (${levelLabel})`;
        valueDisplay.style.color = progressBar.style.backgroundColor;
    }

    /**
     * Update the trust chart with new data.
     */
    function updateTrustChart() {
        if (!state.chartInstance) return;
        
        const labels = state.trustHistory.map(point => {
            const date = new Date(point.timestamp);
            return `${date.getMonth()+1}/${date.getDate()} ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
        });
        
        const data = state.trustHistory.map(point => point.value);
        
        // Update chart data
        state.chartInstance.data.labels = labels;
        state.chartInstance.data.datasets[0].data = data;
        
        // Add event annotations if needed
        // This would require Chart.js annotation plugin in a full implementation
        
        // Update chart
        state.chartInstance.update();
    }

    /**
     * Load trust history from storage.
     */
    function loadTrustHistory() {
        const history = localStorage.getItem(CONFIG.STORAGE_KEY);
        if (history) {
            try {
                state.trustHistory = JSON.parse(history);
                
                // Update current trust from most recent value
                if (state.trustHistory.length > 0) {
                    const latestPoint = state.trustHistory[state.trustHistory.length - 1];
                    updateTrustIndicator(latestPoint.value);
                }
                
                // Prune old history
                pruneTrustHistory();
            } catch (e) {
                console.error('Error parsing ATRiAN trust history:', e);
                state.trustHistory = [];
            }
        }
    }

    /**
     * Save trust history to storage.
     */
    function saveTrustHistory() {
        // Prune history before saving
        pruneTrustHistory();
        
        try {
            localStorage.setItem(CONFIG.STORAGE_KEY, JSON.stringify(state.trustHistory));
        } catch (e) {
            console.error('Error saving ATRiAN trust history:', e);
        }
    }

    /**
     * Prune trust history to stay within limits.
     */
    function pruneTrustHistory() {
        // Limit by number of points
        if (state.trustHistory.length > CONFIG.MAX_HISTORY_POINTS) {
            state.trustHistory = state.trustHistory.slice(-CONFIG.MAX_HISTORY_POINTS);
        }
        
        // Limit by age
        const oldestAllowed = Date.now() - (CONFIG.MAX_HISTORY_DAYS * 24 * 60 * 60 * 1000);
        state.trustHistory = state.trustHistory.filter(point => point.timestamp >= oldestAllowed);
    }

    /**
     * Add a new trust history point.
     * @param {number} value - Trust value
     * @param {Object} event - Associated event (optional)
     */
    function addTrustHistoryPoint(value, event = null) {
        const point = {
            value: value,
            timestamp: Date.now(),
            event: event
        };
        
        state.trustHistory.push(point);
        saveTrustHistory();
        
        // Update UI
        updateTrustIndicator(value);
        updateTrustChart();
    }

    /**
     * Start polling for trust updates.
     */
    function startPolling() {
        if (state.pollInterval) {
            clearInterval(state.pollInterval);
        }
        
        // Define poll function
        const pollTrustUpdate = async function() {
            try {
                // Try to get trust from adapter
                if (state.adapter && typeof state.adapter.retrieve_trust_score === 'function') {
                    const userId = window.windsurfIDE ? window.windsurfIDE.getCurrentUser() : 'DefaultUser';
                    const trustScore = await state.adapter.retrieve_trust_score(userId);
                    
                    // Only update if value changed significantly
                    if (Math.abs(trustScore - state.currentTrust) >= 0.01) {
                        addTrustHistoryPoint(trustScore);
                    }
                }
            } catch (e) {
                console.error('Error polling for trust updates:', e);
            }
        };
        
        // Poll immediately then at interval
        pollTrustUpdate();
        state.pollInterval = setInterval(pollTrustUpdate, CONFIG.POLL_INTERVAL);
    }

    /**
     * Stop polling for trust updates.
     */
    function stopPolling() {
        if (state.pollInterval) {
            clearInterval(state.pollInterval);
            state.pollInterval = null;
        }
    }

    /**
     * Manually update the trust value.
     * @param {number} value - New trust value
     * @param {Object} event - Associated event (optional)
     */
    function updateTrust(value, event = null) {
        // Validate trust value
        value = Math.max(0, Math.min(1, value));
        
        // Add history point
        addTrustHistoryPoint(value, event);
        
        // If adapter available, store value
        if (state.adapter && typeof state.adapter.store_trust_score === 'function') {
            const userId = window.windsurfIDE ? window.windsurfIDE.getCurrentUser() : 'DefaultUser';
            state.adapter.store_trust_score(userId, value);
        }
        
        return value;
    }

    /**
     * Get the current trust level category.
     * @returns {string} Trust level category (high, medium, low)
     */
    function getTrustLevel() {
        if (state.currentTrust >= CONFIG.TRUST_LEVELS.HIGH.min) {
            return 'high';
        } else if (state.currentTrust >= CONFIG.TRUST_LEVELS.MEDIUM.min) {
            return 'medium';
        } else {
            return 'low';
        }
    }

    // Public API
    window.ATRiANTrustVisualization = {
        initialize,
        updateTrust,
        getCurrentTrust: () => state.currentTrust,
        getTrustLevel,
        getTrustHistory: () => [...state.trustHistory],
        addTrustEvent: (eventType, description, impact) => {
            const event = {
                type: eventType,
                description: description,
                impact: impact,
                timestamp: Date.now()
            };
            
            // Calculate new trust based on impact
            const newTrust = Math.max(0, Math.min(1, state.currentTrust + impact));
            return updateTrust(newTrust, event);
        }
    };

    // Auto-initialize if document is already loaded
    if (document.readyState === 'complete') {
        initialize();
    } else {
        window.addEventListener('DOMContentLoaded', initialize);
    }

    // Connect with EGOS system health monitoring
    if (window.EGOS && window.EGOS.healthMonitor) {
        window.EGOS.healthMonitor.registerComponent('ATRiANTrustVisualization', {
            name: 'ATRiAN Trust Visualization',
            version: '1.0',
            status: function() {
                return {
                    status: 'active',
                    initialized: state.initialized,
                    currentTrust: state.currentTrust,
                    trustLevel: getTrustLevel(),
                    historyPoints: state.trustHistory.length
                };
            }
        });
    }

})(window, document);