/**
 * EGOS System - ATRiAN Module: Notification Panel Component
 * Version: 1.0
 * Last Modified: 2025-05-27
 *
 * Purpose:
 * This module provides a notification panel component for displaying ethical
 * guidance and trust-related notifications from the ATRiAN system within the
 * Windsurf IDE interface.
 *
 * MQP Alignment:
 * - Sacred Privacy (SP): Provides privacy-aware notifications
 * - Integrated Ethics (IE/ETHIK): Displays ethical guidance
 * - Reciprocal Trust (RT): Shows trust-related information
 * - Universal Accessibility (UA): Ensures notifications are accessible
 *
 * Cross-references:
 * - @references {C:\EGOS\ATRiAN\atrian_windsurf_adapter.py}
 * - @references {C:\EGOS\ATRiAN\docs\windsurf_integration_guide.md}
 * - @references {C:\EGOS\.windsurfrules_atrian_section}
 * - @references {C:\EGOS\run_tools.py}
 * - @references {C:\EGOS\scripts\system_health\core\validator.py}
 * --- 
 */

(function(window, document) {
    'use strict';

    // Configuration Constants
    const CONFIG = {
        CONTAINER_ID: 'atrian-notification-container',
        NOTIFICATION_CLASS: 'atrian-notification',
        NOTIFICATION_TYPES: {
            INFO: 'info',
            WARNING: 'warning',
            CRITICAL: 'critical'
        },
        ANIMATION_DURATION: 300, // ms
        AUTO_DISMISS_DELAY: {
            INFO: 8000,      // 8 seconds
            WARNING: 15000,  // 15 seconds
            CRITICAL: 0      // Don't auto-dismiss critical
        },
        MAX_NOTIFICATIONS: 5,
        STORAGE_KEY: 'atrian_notification_history'
    };

    // Track notification state
    const state = {
        notifications: [],
        container: null,
        initialized: false
    };

    /**
     * Initialize the notification panel.
     * Creates the container and attaches it to the DOM.
     */
    function initialize() {
        if (state.initialized) return;

        // Create container if it doesn't exist
        if (!document.getElementById(CONFIG.CONTAINER_ID)) {
            state.container = document.createElement('div');
            state.container.id = CONFIG.CONTAINER_ID;
            document.body.appendChild(state.container);
            
            // Load notification styles
            loadStyles();
        } else {
            state.container = document.getElementById(CONFIG.CONTAINER_ID);
        }

        // Load notification history from storage
        const history = localStorage.getItem(CONFIG.STORAGE_KEY);
        if (history) {
            try {
                state.notifications = JSON.parse(history);
                // Don't show old notifications on startup, just maintain history
            } catch (e) {
                console.error('Error parsing ATRiAN notification history:', e);
                state.notifications = [];
            }
        }

        state.initialized = true;
        console.log('ATRiAN Notification Panel initialized');
    }

    /**
     * Load styles for the notification panel.
     */
    function loadStyles() {
        const style = document.createElement('style');
        style.textContent = `
            #${CONFIG.CONTAINER_ID} {
                position: fixed;
                bottom: 20px;
                right: 20px;
                max-width: 400px;
                z-index: 9999;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            .${CONFIG.NOTIFICATION_CLASS} {
                margin-top: 10px;
                padding: 15px;
                border-radius: 5px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                animation: atrian-notification-slide-in ${CONFIG.ANIMATION_DURATION}ms ease-out;
                transition: opacity ${CONFIG.ANIMATION_DURATION}ms, transform ${CONFIG.ANIMATION_DURATION}ms;
                opacity: 0;
                transform: translateX(50px);
                background-color: #fff;
                border-left: 5px solid #ccc;
                display: flex;
                flex-direction: column;
                position: relative;
            }
            
            .${CONFIG.NOTIFICATION_CLASS}.visible {
                opacity: 1;
                transform: translateX(0);
            }
            
            .${CONFIG.NOTIFICATION_CLASS}.fade-out {
                opacity: 0;
                transform: translateY(20px);
            }
            
            .${CONFIG.NOTIFICATION_CLASS}-info {
                border-left-color: #3498db;
            }
            
            .${CONFIG.NOTIFICATION_CLASS}-warning {
                border-left-color: #f39c12;
            }
            
            .${CONFIG.NOTIFICATION_CLASS}-critical {
                border-left-color: #e74c3c;
            }
            
            .${CONFIG.NOTIFICATION_CLASS}-title {
                font-weight: bold;
                margin-bottom: 5px;
                padding-right: 20px;
                color: #333;
            }
            
            .${CONFIG.NOTIFICATION_CLASS}-info .${CONFIG.NOTIFICATION_CLASS}-title::before {
                content: "ℹ️ ";
            }
            
            .${CONFIG.NOTIFICATION_CLASS}-warning .${CONFIG.NOTIFICATION_CLASS}-title::before {
                content: "⚠️ ";
            }
            
            .${CONFIG.NOTIFICATION_CLASS}-critical .${CONFIG.NOTIFICATION_CLASS}-title::before {
                content: "🛑 ";
            }
            
            .${CONFIG.NOTIFICATION_CLASS}-message {
                font-size: 0.9em;
                color: #555;
            }
            
            .${CONFIG.NOTIFICATION_CLASS}-close {
                position: absolute;
                top: 5px;
                right: 5px;
                cursor: pointer;
                font-size: 16px;
                color: #999;
                border: none;
                background: transparent;
                padding: 0;
                width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
            }
            
            .${CONFIG.NOTIFICATION_CLASS}-close:hover {
                background-color: rgba(0, 0, 0, 0.1);
                color: #333;
            }
            
            .${CONFIG.NOTIFICATION_CLASS}-actions {
                display: flex;
                justify-content: flex-end;
                margin-top: 10px;
            }
            
            .${CONFIG.NOTIFICATION_CLASS}-action {
                background: transparent;
                border: 1px solid #ddd;
                border-radius: 3px;
                padding: 5px 10px;
                margin-left: 5px;
                cursor: pointer;
                font-size: 0.8em;
                transition: background-color 0.2s, color 0.2s;
            }
            
            .${CONFIG.NOTIFICATION_CLASS}-action:hover {
                background-color: #f5f5f5;
            }
            
            .${CONFIG.NOTIFICATION_CLASS}-action.primary {
                background-color: #3498db;
                color: white;
                border-color: #3498db;
            }
            
            .${CONFIG.NOTIFICATION_CLASS}-action.primary:hover {
                background-color: #2980b9;
            }
            
            @keyframes atrian-notification-slide-in {
                from {
                    transform: translateX(50px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Show a notification in the panel.
     * 
     * @param {Object} notification - The notification data
     * @param {string} notification.id - Unique ID for the notification
     * @param {string} notification.type - Type of notification (info, warning, critical)
     * @param {string} notification.title - Title text
     * @param {string} notification.message - Message text
     * @param {Array} [notification.actions] - Optional action buttons
     * @param {Function} [notification.onDismiss] - Optional callback on dismiss
     * @returns {string} The ID of the created notification
     */
    function showNotification(notification) {
        if (!state.initialized) {
            initialize();
        }

        // Ensure notification has a valid ID
        notification.id = notification.id || 'atrian-notification-' + Date.now();
        
        // Validate notification type
        const validTypes = Object.values(CONFIG.NOTIFICATION_TYPES);
        if (!validTypes.includes(notification.type)) {
            notification.type = CONFIG.NOTIFICATION_TYPES.INFO;
        }
        
        // Create notification element
        const notificationEl = document.createElement('div');
        notificationEl.className = `${CONFIG.NOTIFICATION_CLASS} ${CONFIG.NOTIFICATION_CLASS}-${notification.type}`;
        notificationEl.dataset.id = notification.id;
        
        // Create title
        const titleEl = document.createElement('div');
        titleEl.className = `${CONFIG.NOTIFICATION_CLASS}-title`;
        titleEl.textContent = notification.title;
        notificationEl.appendChild(titleEl);
        
        // Create message
        const messageEl = document.createElement('div');
        messageEl.className = `${CONFIG.NOTIFICATION_CLASS}-message`;
        messageEl.textContent = notification.message;
        notificationEl.appendChild(messageEl);
        
        // Create close button
        const closeButton = document.createElement('button');
        closeButton.className = `${CONFIG.NOTIFICATION_CLASS}-close`;
        closeButton.innerHTML = '&times;';
        closeButton.setAttribute('aria-label', 'Dismiss notification');
        closeButton.addEventListener('click', function() {
            dismissNotification(notification.id);
        });
        notificationEl.appendChild(closeButton);
        
        // Add actions if provided
        if (notification.actions && notification.actions.length > 0) {
            const actionsContainer = document.createElement('div');
            actionsContainer.className = `${CONFIG.NOTIFICATION_CLASS}-actions`;
            
            notification.actions.forEach(action => {
                const actionButton = document.createElement('button');
                actionButton.className = `${CONFIG.NOTIFICATION_CLASS}-action`;
                if (action.primary) {
                    actionButton.classList.add('primary');
                }
                actionButton.textContent = action.label;
                actionButton.addEventListener('click', function() {
                    if (typeof action.callback === 'function') {
                        action.callback(notification);
                    }
                    if (action.dismiss !== false) {
                        dismissNotification(notification.id);
                    }
                });
                actionsContainer.appendChild(actionButton);
            });
            
            notificationEl.appendChild(actionsContainer);
        }
        
        // Add to container
        state.container.appendChild(notificationEl);
        
        // Store in state
        notification.timestamp = Date.now();
        state.notifications.push(notification);
        saveNotificationHistory();
        
        // Limit the number of visible notifications
        const visibleNotifications = state.container.querySelectorAll(`.${CONFIG.NOTIFICATION_CLASS}`);
        if (visibleNotifications.length > CONFIG.MAX_NOTIFICATIONS) {
            const oldestNotification = visibleNotifications[0];
            dismissNotification(oldestNotification.dataset.id);
        }
        
        // Make visible after a small delay (for animation)
        setTimeout(() => {
            notificationEl.classList.add('visible');
        }, 10);
        
        // Auto-dismiss if configured
        const autoDismissDelay = CONFIG.AUTO_DISMISS_DELAY[notification.type.toUpperCase()];
        if (autoDismissDelay > 0) {
            setTimeout(() => {
                dismissNotification(notification.id);
            }, autoDismissDelay);
        }
        
        // Return notification ID
        return notification.id;
    }

    /**
     * Dismiss a notification by ID.
     * 
     * @param {string} id - The notification ID to dismiss
     * @returns {boolean} True if notification was found and dismissed
     */
    function dismissNotification(id) {
        const notificationEl = state.container.querySelector(`.${CONFIG.NOTIFICATION_CLASS}[data-id="${id}"]`);
        if (!notificationEl) return false;
        
        // Add fade-out class for animation
        notificationEl.classList.add('fade-out');
        
        // Remove after animation completes
        setTimeout(() => {
            if (notificationEl.parentNode) {
                notificationEl.parentNode.removeChild(notificationEl);
            }
            
            // Call onDismiss callback if exists
            const notification = state.notifications.find(n => n.id === id);
            if (notification && typeof notification.onDismiss === 'function') {
                notification.onDismiss(notification);
            }
        }, CONFIG.ANIMATION_DURATION);
        
        return true;
    }

    /**
     * Clear all notifications from the panel.
     */
    function clearAllNotifications() {
        const notifications = state.container.querySelectorAll(`.${CONFIG.NOTIFICATION_CLASS}`);
        notifications.forEach(notification => {
            dismissNotification(notification.dataset.id);
        });
    }

    /**
     * Save notification history to local storage.
     * Only stores essential information for history tracking.
     */
    function saveNotificationHistory() {
        // Only keep the last 50 notifications in history
        const historyLimit = 50;
        if (state.notifications.length > historyLimit) {
            state.notifications = state.notifications.slice(-historyLimit);
        }
        
        // Create simplified objects for storage
        const storageData = state.notifications.map(notification => ({
            id: notification.id,
            type: notification.type,
            title: notification.title,
            message: notification.message,
            timestamp: notification.timestamp,
            operationId: notification.operationId
        }));
        
        // Save to local storage
        try {
            localStorage.setItem(CONFIG.STORAGE_KEY, JSON.stringify(storageData));
        } catch (e) {
            console.error('Error saving ATRiAN notification history:', e);
        }
    }

    /**
     * Get notification history.
     * 
     * @returns {Array} Array of notification history objects
     */
    function getNotificationHistory() {
        return [...state.notifications].sort((a, b) => b.timestamp - a.timestamp);
    }

    /**
     * Show ATRiAN guidance notification based on adapter output.
     * 
     * @param {Object} notificationData - The notification data from ATRiANWindsurfAdapter
     * @returns {string} The ID of the created notification
     */
    function showATRiANGuidance(notificationData) {
        // Map ATRiAN notification type to UI type
        const typeMap = {
            'info': CONFIG.NOTIFICATION_TYPES.INFO,
            'warning': CONFIG.NOTIFICATION_TYPES.WARNING,
            'critical': CONFIG.NOTIFICATION_TYPES.CRITICAL
        };
        
        const notification = {
            id: notificationData.notification_id,
            type: typeMap[notificationData.type] || CONFIG.NOTIFICATION_TYPES.INFO,
            title: notificationData.title,
            message: notificationData.message,
            operationId: notificationData.operation_id,
            actions: []
        };
        
        // Add standard "Learn More" action
        notification.actions.push({
            label: 'Learn More',
            callback: function() {
                // Open documentation or detailed view
                console.log('Learn more about: ', notificationData);
                if (window.windsurfIDE && window.windsurfIDE.openDocument) {
                    window.windsurfIDE.openDocument('C:\\EGOS\\ATRiAN\\docs\\atrian_guidance_interpretation.md');
                }
            },
            dismiss: false
        });
        
        // Add "Acknowledge" action for critical notifications
        if (notification.type === CONFIG.NOTIFICATION_TYPES.CRITICAL) {
            notification.actions.push({
                label: 'Acknowledge',
                primary: true,
                callback: function() {
                    console.log('User acknowledged notification:', notificationData);
                    // Send acknowledgment to adapter if API available
                    if (window.atrian && window.atrian.acknowledgeNotification) {
                        window.atrian.acknowledgeNotification(notificationData.notification_id);
                    }
                }
            });
        }
        
        return showNotification(notification);
    }

    // Public API
    window.ATRiANNotifications = {
        initialize,
        show: showNotification,
        dismiss: dismissNotification,
        clear: clearAllNotifications,
        showGuidance: showATRiANGuidance,
        getHistory: getNotificationHistory
    };

    // Auto-initialize if document is already loaded
    if (document.readyState === 'complete') {
        initialize();
    } else {
        window.addEventListener('DOMContentLoaded', initialize);
    }

})(window, document);

// Connect with EGOS system health monitoring
if (window.EGOS && window.EGOS.healthMonitor) {
    window.EGOS.healthMonitor.registerComponent('ATRiANNotifications', {
        name: 'ATRiAN Notification Panel',
        version: '1.0',
        status: function() {
            return {
                status: 'active',
                initialized: window.ATRiANNotifications && window.ATRiANNotifications.initialized,
                notifications: window.ATRiANNotifications ? 
                    window.ATRiANNotifications.getHistory().length : 0
            };
        }
    });
}