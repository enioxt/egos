/**
 * EGOS Cross-Reference Network Visualization
 * Interactive graph visualization using Sigma.js and Graphology
 */

// Initialize when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const sigmaContainer = document.getElementById('sigma-container');
    const loadingOverlay = document.getElementById('loading-overlay');
    const nodeDetails = document.getElementById('node-details');
    const nodeContent = document.getElementById('node-content');
    const searchInput = document.getElementById('search-input');
    const contextMenu = document.getElementById('context-menu');
    const toggleSidebarBtn = document.getElementById('toggle-sidebar');
    const toggleThemeBtn = document.getElementById('toggle-theme');
    const toggleFullscreenBtn = document.getElementById('toggle-fullscreen');
    const minReferencesSlider = document.getElementById('min-references');
    const minReferencesValue = document.getElementById('min-references-value');
    const topReferencedFilesList = document.getElementById('top-referenced-files');
    
    // State variables
    let renderer = null;
    let hoveredNode = null;
    let selectedNode = null;
    let highlightedNodes = new Set();
    let highlightedEdges = new Set();
    let isFullscreen = false;
    let isDarkTheme = true;
    let minReferences = 0;
    
    // Initialize graph
    initGraph();
    
    // Event listeners for UI controls
    setupEventListeners();
    
    /**
     * Initialize the graph visualization
     */
    function initGraph() {
        // Show loading overlay
        loadingOverlay.style.display = 'flex';
        
        // Create a new graph instance
        const graph = new graphology.Graph();
        
        // Process nodes
        graphData.nodes.forEach(node => {
            graph.addNode(node.id, {
                x: Math.random(),  // Initial random position
                y: Math.random(),
                size: calculateNodeSize(node.references || 0),
                color: getNodeColor(node.type),
                label: node.label || node.id,
                type: node.type,
                path: node.path,
                references: node.references || 0,
                referenced_by: node.referenced_by || 0,
                last_modified: node.last_modified,
                has_mqp: node.has_mqp || false,
                has_roadmap: node.has_roadmap || false,
                is_core: node.is_core || false
            });
        });
        
        // Process edges
        graphData.edges.forEach(edge => {
            if (graph.hasNode(edge.source) && graph.hasNode(edge.target)) {
                graph.addEdge(edge.source, edge.target, {
                    size: edge.weight || 1,
                    color: 'rgba(255, 255, 255, 0.1)',
                    type: edge.type || 'default'
                });
            }
        });
        
        // Apply force-directed layout with error handling
        console.log('ForceAtlas2 available?', !!window.forceAtlas2);
        console.log('Graphology object:', graphology);
        if (graphology.layouts) console.log('Graphology layouts:', Object.keys(graphology.layouts));
        
        let layout;
        try {
            // Try multiple ways to access ForceAtlas2
            if (window.forceAtlas2) {
                console.log('Using global forceAtlas2');
                layout = window.forceAtlas2(graph, {
                    settings: {
                        gravity: 1,
                        scalingRatio: 10,
                        strongGravityMode: true,
                        slowDown: 10
                    },
                    iterations: 100
                });
            } else if (typeof graphologyLayoutForceAtlas2 !== 'undefined') {
                console.log('Using graphologyLayoutForceAtlas2');
                layout = graphologyLayoutForceAtlas2(graph, {
                    settings: {
                        gravity: 1,
                        scalingRatio: 10,
                        strongGravityMode: true,
                        slowDown: 10
                    },
                    iterations: 100
                });
            } else if (graphology && graphology.layouts && graphology.layouts.forceAtlas2) {
                console.log('Using graphology.layouts.forceAtlas2');
                layout = graphology.layouts.forceAtlas2(graph, {
                    settings: {
                        gravity: 1,
                        scalingRatio: 10,
                        strongGravityMode: true,
                        slowDown: 10
                    },
                    iterations: 100
                });
            } else {
                // If no ForceAtlas2 implementation is available, use random positions
                console.warn('ForceAtlas2 not available. Using random positions instead.');
                layout = {};
                graph.forEachNode((node) => {
                    layout[node] = {
                        x: Math.random() * 10,
                        y: Math.random() * 10
                    };
                });
            }
        } catch (error) {
            console.error('Error applying layout:', error);
            // Fallback to random layout
            layout = {};
            graph.forEachNode((node) => {
                layout[node] = {
                    x: Math.random() * 10 - 5, 
                    y: Math.random() * 10 - 5
                };
            });
        }
        
        // Assign positions from layout
        graph.forEachNode((node, attributes) => {
            const position = layout[node];
            if (position) {
                graph.setNodeAttribute(node, 'x', position.x);
                graph.setNodeAttribute(node, 'y', position.y);
            } else {
                // Fallback if position is undefined
                graph.setNodeAttribute(node, 'x', Math.random() * 10 - 5);
                graph.setNodeAttribute(node, 'y', Math.random() * 10 - 5);
            }
        });
        
        // Create renderer with proper error handling
        console.log('Creating Sigma renderer, Sigma available:', typeof Sigma !== 'undefined', 'SigmaClass available:', typeof window.SigmaClass !== 'undefined');
        
        try {
            // Try to access Sigma through different possible global variables
            const SigmaConstructor = Sigma || window.Sigma || window.SigmaClass || sigma;
            renderer = new SigmaConstructor(graph, sigmaContainer, {
            renderEdgeLabels: false,
            labelRenderedSizeThreshold: 1,
            labelFont: 'Inter, sans-serif',
            labelSize: 12,
            labelWeight: 'normal',
            labelColor: {
                color: '#e5e7eb'
            },
            nodeReducer: (node, data) => {
                // Filter nodes based on minimum references
                if (data.references < minReferences) {
                    return { ...data, hidden: true };
                }
                
                // Apply type filters
                const nodeType = data.type || 'other';
                const typeCheckbox = document.querySelector(`input[data-filter="${nodeType}"]`);
                if (typeCheckbox && !typeCheckbox.checked) {
                    return { ...data, hidden: true };
                }
                
                // Apply status filters
                const isOrphaned = data.referenced_by === 0;
                const orphanedCheckbox = document.querySelector('input[data-status="orphaned"]');
                const referencedCheckbox = document.querySelector('input[data-status="referenced"]');
                const coreCheckbox = document.querySelector('input[data-status="core"]');
                
                if (data.is_core && (!coreCheckbox || !coreCheckbox.checked)) {
                    return { ...data, hidden: true };
                } else if (isOrphaned && (!orphanedCheckbox || !orphanedCheckbox.checked)) {
                    return { ...data, hidden: true };
                } else if (!isOrphaned && !data.is_core && (!referencedCheckbox || !referencedCheckbox.checked)) {
                    return { ...data, hidden: true };
                }
                
                // Apply search filter
                const searchTerm = searchInput.value.toLowerCase();
                if (searchTerm && !data.label.toLowerCase().includes(searchTerm)) {
                    return { ...data, hidden: true };
                }
                
                // Highlight selected node and its connections
                if (selectedNode) {
                    if (node === selectedNode || highlightedNodes.has(node)) {
                        return { 
                            ...data, 
                            highlighted: true,
                            color: data.color,
                            size: data.size * 1.5
                        };
                    } else {
                        return { 
                            ...data, 
                            color: 'rgba(255, 255, 255, 0.2)',
                            size: data.size * 0.8
                        };
                    }
                }
                
                // Highlight hovered node
                if (hoveredNode === node) {
                    return { 
                        ...data, 
                        highlighted: true,
                        color: data.color,
                        size: data.size * 1.3
                    };
                }
                
                return data;
            },
            edgeReducer: (edge, data) => {
                // Hide edges connected to hidden nodes
                const sourceData = graph.getNodeAttributes(graph.source(edge));
                const targetData = graph.getNodeAttributes(graph.target(edge));
                
                if (sourceData.hidden || targetData.hidden) {
                    return { ...data, hidden: true };
                }
                
                // Highlight edges connected to selected node
                if (selectedNode) {
                    if (highlightedEdges.has(edge)) {
                        return { 
                            ...data, 
                            color: 'rgba(59, 130, 246, 0.8)',
                            size: data.size * 2
                        };
                    } else {
                        return { 
                            ...data, 
                            color: 'rgba(255, 255, 255, 0.05)',
                            size: data.size * 0.5
                        };
                    }
                }
                
                // Highlight edges connected to hovered node
                if (hoveredNode === graph.source(edge) || hoveredNode === graph.target(edge)) {
                    return { 
                        ...data, 
                        color: 'rgba(59, 130, 246, 0.6)',
                        size: data.size * 1.5
                    };
                }
                
                return data;
            }
        });
        
        // Populate top referenced files list
        populateTopReferencedFiles(graph);
        
        // Hide loading overlay when successful
        loadingOverlay.style.display = 'none';
        } catch (error) {
            console.error('Error creating Sigma renderer:', error);
            // Show error message in loading overlay
            const loadingText = document.querySelector('.loading-text');
            if (loadingText) {
                loadingText.textContent = 'Error loading visualization: ' + error.message;
            }
        }
    }
    
    /**
     * Set up event listeners for graph and UI controls
     */
    function setupEventListeners() {
        // Graph hover events
        if (renderer) {
            // Node hover
            renderer.on('enterNode', ({ node }) => {
                hoveredNode = node;
                document.body.style.cursor = 'pointer';
                renderer.refresh();
            });
            
            renderer.on('leaveNode', () => {
                hoveredNode = null;
                document.body.style.cursor = 'default';
                renderer.refresh();
            });
            
            // Node click
            renderer.on('clickNode', ({ node }) => {
                selectNode(node);
            });
            
            // Stage click (background)
            renderer.on('clickStage', () => {
                if (selectedNode) {
                    deselectNode();
                }
                hideContextMenu();
            });
            
            // Right-click on node
            renderer.getMouseCaptor().on('rightClickNode', (event) => {
                event.preventDefault();
                const node = event.node;
                selectNode(node);
                showContextMenu(event.event.clientX, event.event.clientY, node);
            });
        }
        
        // Search input
        searchInput.addEventListener('input', () => {
            if (renderer) renderer.refresh();
        });
        
        // Filter checkboxes
        document.querySelectorAll('.filter-option input').forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                if (renderer) renderer.refresh();
            });
        });
        
        // Min references slider
        minReferencesSlider.addEventListener('input', () => {
            minReferences = parseInt(minReferencesSlider.value);
            minReferencesValue.textContent = minReferences;
            if (renderer) renderer.refresh();
        });
        
        // Context menu options
        document.querySelectorAll('.context-menu-option').forEach(option => {
            option.addEventListener('click', () => {
                const action = option.getAttribute('data-action');
                handleContextMenuAction(action, selectedNode);
                hideContextMenu();
            });
        });
        
        // Toggle sidebar
        toggleSidebarBtn.addEventListener('click', () => {
            document.body.classList.toggle('sidebar-collapsed');
            if (renderer) renderer.refresh();
        });
        
        // Toggle theme
        toggleThemeBtn.addEventListener('click', () => {
            isDarkTheme = !isDarkTheme;
            document.body.classList.toggle('light-theme', !isDarkTheme);
            toggleThemeBtn.textContent = isDarkTheme ? '☾' : '☀';
            if (renderer) renderer.refresh();
        });
        
        // Toggle fullscreen
        toggleFullscreenBtn.addEventListener('click', () => {
            toggleFullscreen();
        });
        
        // Action buttons
        document.getElementById('export-csv').addEventListener('click', exportCsv);
        document.getElementById('reset-view').addEventListener('click', resetView);
        document.getElementById('refresh-data').addEventListener('click', refreshData);
        
        // Hide context menu on document click
        document.addEventListener('click', () => {
            hideContextMenu();
        });
        
        // Handle window resize
        window.addEventListener('resize', () => {
            if (renderer) renderer.refresh();
        });
    }
    
    /**
     * Select a node and show its details
     */
    function selectNode(node) {
        selectedNode = node;
        highlightedNodes.clear();
        highlightedEdges.clear();
        
        const graph = renderer.getGraph();
        
        // Find connected nodes and edges
        graph.forEachEdge((edge, attributes, source, target) => {
            if (source === node) {
                highlightedNodes.add(target);
                highlightedEdges.add(edge);
            } else if (target === node) {
                highlightedNodes.add(source);
                highlightedEdges.add(edge);
            }
        });
        
        // Show node details
        showNodeDetails(node);
        
        // Refresh the renderer
        renderer.refresh();
    }
    
    /**
     * Deselect the current node
     */
    function deselectNode() {
        selectedNode = null;
        highlightedNodes.clear();
        highlightedEdges.clear();
        
        // Hide node details
        nodeDetails.parentElement.style.display = 'none';
        
        // Refresh the renderer
        renderer.refresh();
    }
    
    /**
     * Show node details in the overlay
     */
    function showNodeDetails(nodeId) {
        const graph = renderer.getGraph();
        const attributes = graph.getNodeAttributes(nodeId);
        
        // Set node title
        document.getElementById('node-title').textContent = attributes.label;
        
        // Create details content
        let content = '<dl>';
        content += `<dt>Path:</dt><dd>${attributes.path || 'N/A'}</dd>`;
        content += `<dt>Type:</dt><dd>${attributes.type || 'Unknown'}</dd>`;
        content += `<dt>References:</dt><dd>${attributes.references || 0}</dd>`;
        content += `<dt>Referenced by:</dt><dd>${attributes.referenced_by || 0}</dd>`;
        content += `<dt>Last Modified:</dt><dd>${attributes.last_modified || 'Unknown'}</dd>`;
        content += `<dt>MQP Reference:</dt><dd>${attributes.has_mqp ? 'Yes' : 'No'}</dd>`;
        content += `<dt>ROADMAP Reference:</dt><dd>${attributes.has_roadmap ? 'Yes' : 'No'}</dd>`;
        content += `<dt>Core Document:</dt><dd>${attributes.is_core ? 'Yes' : 'No'}</dd>`;
        content += '</dl>';
        
        // Set content and show overlay
        nodeContent.innerHTML = content;
        nodeDetails.parentElement.style.display = 'block';
    }
    
    /**
     * Show context menu at the specified position
     */
    function showContextMenu(x, y, nodeId) {
        contextMenu.style.display = 'block';
        contextMenu.style.left = `${x}px`;
        contextMenu.style.top = `${y}px`;
        
        // Ensure menu stays within viewport
        const rect = contextMenu.getBoundingClientRect();
        if (rect.right > window.innerWidth) {
            contextMenu.style.left = `${x - rect.width}px`;
        }
        if (rect.bottom > window.innerHeight) {
            contextMenu.style.top = `${y - rect.height}px`;
        }
        
        // Store node ID as data attribute
        contextMenu.setAttribute('data-node-id', nodeId);
    }
    
    /**
     * Hide the context menu
     */
    function hideContextMenu() {
        contextMenu.style.display = 'none';
    }
    
    /**
     * Handle context menu actions
     */
    function handleContextMenuAction(action, nodeId) {
        if (!nodeId) return;
        
        const graph = renderer.getGraph();
        const attributes = graph.getNodeAttributes(nodeId);
        
        switch (action) {
            case 'view-github':
                // Open file on GitHub (placeholder URL)
                const repoUrl = 'https://github.com/enioxt/egos';
                const filePath = attributes.path;
                window.open(`${repoUrl}/blob/main/${filePath}`, '_blank');
                break;
                
            case 'add-references':
                // Placeholder for adding references functionality
                alert(`Add references to: ${attributes.label}`);
                break;
                
            case 'view-details':
                showNodeDetails(nodeId);
                break;
                
            case 'highlight-connections':
                selectNode(nodeId);
                break;
        }
    }
    
    /**
     * Toggle fullscreen mode
     */
    function toggleFullscreen() {
        if (!isFullscreen) {
            if (document.documentElement.requestFullscreen) {
                document.documentElement.requestFullscreen();
            }
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            }
        }
        
        isFullscreen = !isFullscreen;
        toggleFullscreenBtn.textContent = isFullscreen ? '⛶' : '⛶';
    }
    
    /**
     * Export graph data as CSV
     */
    function exportCsv() {
        const graph = renderer.getGraph();
        let csvContent = 'data:text/csv;charset=utf-8,';
        
        // Header row
        csvContent += 'File,Type,References,Referenced By,Has MQP,Has ROADMAP,Is Core\n';
        
        // Data rows
        graph.forEachNode((node, attributes) => {
            const row = [
                attributes.label,
                attributes.type || 'Unknown',
                attributes.references || 0,
                attributes.referenced_by || 0,
                attributes.has_mqp ? 'Yes' : 'No',
                attributes.has_roadmap ? 'Yes' : 'No',
                attributes.is_core ? 'Yes' : 'No'
            ];
            
            csvContent += row.join(',') + '\n';
        });
        
        // Create download link
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement('a');
        link.setAttribute('href', encodedUri);
        link.setAttribute('download', 'egos_cross_references.csv');
        document.body.appendChild(link);
        
        // Trigger download
        link.click();
        document.body.removeChild(link);
    }
    
    /**
     * Reset the view to default state
     */
    function resetView() {
        // Reset filters
        document.querySelectorAll('.filter-option input').forEach(checkbox => {
            checkbox.checked = true;
        });
        
        // Reset search
        searchInput.value = '';
        
        // Reset min references
        minReferencesSlider.value = 0;
        minReferences = 0;
        minReferencesValue.textContent = '0';
        
        // Deselect node
        deselectNode();
        
        // Reset camera
        if (renderer) {
            renderer.getCamera().animatedReset();
            renderer.refresh();
        }
    }
    
    /**
     * Refresh data from server (placeholder)
     */
    function refreshData() {
        loadingOverlay.style.display = 'flex';
        
        // Simulate refresh delay
        setTimeout(() => {
            loadingOverlay.style.display = 'none';
            alert('Data refreshed successfully!');
        }, 1000);
    }
    
    /**
     * Populate the top referenced files list
     */
    function populateTopReferencedFiles(graph) {
        // Get nodes sorted by referenced_by count
        const topNodes = [];
        graph.forEachNode((node, attributes) => {
            topNodes.push({
                id: node,
                label: attributes.label,
                count: attributes.referenced_by || 0
            });
        });
        
        // Sort by reference count (descending)
        topNodes.sort((a, b) => b.count - a.count);
        
        // Take top 10
        const top10 = topNodes.slice(0, 10);
        
        // Clear existing list
        topReferencedFilesList.innerHTML = '';
        
        // Add items to list
        top10.forEach(node => {
            const li = document.createElement('li');
            li.innerHTML = `
                <span class="file-name">${node.label}</span>
                <span class="file-count">${node.count}</span>
            `;
            
            // Add click handler
            li.addEventListener('click', () => {
                selectNode(node.id);
            });
            
            topReferencedFilesList.appendChild(li);
        });
    }
    
    /**
     * Calculate node size based on reference count
     */
    function calculateNodeSize(references) {
        // Base size
        const baseSize = 5;
        
        // Logarithmic scaling for references
        if (references === 0) return baseSize;
        return baseSize + Math.log(references + 1) * 2;
    }
    
    /**
     * Get node color based on file type
     */
    function getNodeColor(type) {
        switch (type) {
            case 'markdown':
                return '#3b82f6';  // Blue
            case 'python':
                return '#10b981';  // Green
            case 'yaml':
            case 'json':
                return '#f59e0b';  // Amber
            default:
                return '#8b5cf6';  // Purple
        }
    }
});
