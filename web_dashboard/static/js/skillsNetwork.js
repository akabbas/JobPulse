/**
 * Skills Network Visualization for JobPulse
 * 
 * This module creates an interactive network graph showing relationships between
 * skills that commonly appear together in job postings. It uses the vis-network
 * library to render a force-directed graph where:
 * - Nodes represent individual skills (size based on frequency)
 * - Edges show co-occurrence relationships between skills
 * - Interactive features allow exploration of skill connections
 * 
 * Usage:
 * 1. Include vis-network CSS and JS in your HTML
 * 2. Create a container div with id="skills-network"
 * 3. Call initializeSkillsNetwork() to start the visualization
 */

class SkillsNetworkVisualizer {
    constructor(containerId, apiUrl = '/api/skills-network', useCurrentSearch = true, searchId = null) {
        this.containerId = containerId;
        this.apiUrl = apiUrl;
        this.useCurrentSearch = useCurrentSearch;
        this.searchId = searchId;
        this.container = null;
        this.network = null;
        this.nodes = new vis.DataSet([]);
        this.edges = new vis.DataSet([]);
        this.skillsData = null;
        
        // Filter parameters
        this.minFrequency = 2;
        this.minCoOccurrence = 1;
        
        // Network configuration options
        this.options = {
            nodes: {
                shape: 'circle',
                font: {
                    size: 14,
                    face: 'Arial',
                    color: '#333333'
                },
                borderWidth: 2,
                shadow: true,
                scaling: {
                    min: 10,
                    max: 50,
                    label: {
                        enabled: true,
                        min: 12,
                        max: 20
                    }
                }
            },
            edges: {
                width: 2,
                color: {
                    color: '#848484',
                    highlight: '#ff7675',
                    hover: '#74b9ff'
                },
                smooth: {
                    type: 'continuous',
                    forceDirection: 'none'
                },
                shadow: true
            },
            physics: {
                enabled: true,
                solver: 'forceAtlas2Based',
                forceAtlas2Based: {
                    gravitationalConstant: -50,
                    centralGravity: 0.01,
                    springLength: 100,
                    springConstant: 0.08,
                    damping: 0.4,
                    avoidOverlap: 0.5
                },
                stabilization: {
                    enabled: true,
                    iterations: 1000,
                    updateInterval: 100
                }
            },
            interaction: {
                hover: true,
                tooltipDelay: 200,
                hideEdgesOnDrag: true,
                navigationButtons: true,
                keyboard: {
                    enabled: true,
                    speed: {
                        x: 10,
                        y: 10,
                        zoom: 0.1
                    }
                }
            },
            layout: {
                improvedLayout: true,
                hierarchical: false
            }
        };
        
        this.init();
    }
    
    /**
     * Initialize the skills network visualizer
     */
    async init() {
        try {
            this.container = document.getElementById(this.containerId);
            if (!this.container) {
                throw new Error(`Container with id "${this.containerId}" not found`);
            }
            
            // Show loading state
            this.showLoading();
            
            // Fetch skills data from API
            await this.fetchSkillsData();
            
            // Create the network visualization
            this.createNetwork();
            
            // Add event listeners
            this.addEventListeners();
            
            // Hide loading state
            this.hideLoading();
            
            console.log('Skills network visualization initialized successfully');
            
        } catch (error) {
            console.error('Error initializing skills network:', error);
            this.showError(error.message);
        }
    }
    
    /**
     * Fetch skills co-occurrence data from the Flask API
     */
    async fetchSkillsData() {
        try {
            // Build query parameters
            const params = new URLSearchParams({
                min_frequency: this.minFrequency,
                min_co_occurrence: this.minCoOccurrence,
                use_current_search: this.useCurrentSearch.toString()
            });
            
            // Add search ID if available
            if (this.searchId) {
                params.append('search_id', this.searchId);
            }
            
            const response = await fetch(`${this.apiUrl}?${params}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            this.skillsData = await response.json();
            
            if (!this.skillsData.success) {
                throw new Error(this.skillsData.error || 'Failed to fetch skills data');
            }
            
            // Check if we have real data or just sample data
            if (this.skillsData.data.data_source === 'sample_data' && this.useCurrentSearch) {
                console.warn('No real job data available, showing sample data');
                // Show a message that this is sample data
                this.showSampleDataMessage();
            }
            
            console.log('Skills data fetched successfully:', this.skillsData);
            
        } catch (error) {
            console.error('Error fetching skills data:', error);
            
            // Check if it's a "no data" error
            if (error.message.includes('No recent searches found') || 
                error.message.includes('No real job data available')) {
                this.showNoDataMessage();
                return;
            }
            
            throw new Error(`Failed to fetch skills data: ${error.message}`);
        }
    }
    
    /**
     * Create the network visualization using vis-network
     */
    createNetwork() {
        if (!this.skillsData || !this.skillsData.data) {
            throw new Error('No skills data available');
        }
        
        const { skills, co_occurrences } = this.skillsData.data;
        
        // Validate data structure
        if (!skills || !co_occurrences) {
            throw new Error('Invalid data structure: missing skills or co_occurrences');
        }
        
        // Create nodes from skills data
        this.createNodes(skills);
        
        // Create edges from co-occurrence data
        this.createEdges(co_occurrences);
        
        // Create the network
        const data = {
            nodes: this.nodes,
            edges: this.edges
        };
        
        this.network = new vis.Network(this.container, data, this.options);
        
        // Fit the network to the container
        setTimeout(() => {
            this.network.fit();
        }, 100);
    }
    
    /**
     * Create nodes for each skill
     */
    createNodes(skills) {
        // Find the maximum frequency for scaling
        const maxFreq = Math.max(...Object.values(skills));
        const minFreq = Math.min(...Object.values(skills));
        
        // Create color scale based on frequency
        const getNodeColor = (frequency) => {
            const normalized = (frequency - minFreq) / (maxFreq - minFreq);
            if (normalized > 0.7) return '#e74c3c';      // High demand - Red
            if (normalized > 0.4) return '#f39c12';      // Medium demand - Orange
            if (normalized > 0.2) return '#f1c40f';      // Moderate demand - Yellow
            return '#2ecc71';                            // Lower demand - Green
        };
        
        // Create nodes
        Object.entries(skills).forEach(([skill, frequency]) => {
            const nodeSize = Math.max(15, Math.min(50, 15 + (frequency / maxFreq) * 35));
            
            this.nodes.add({
                id: skill,
                label: skill,
                size: nodeSize,
                color: getNodeColor(frequency),
                title: `${skill}<br>Frequency: ${frequency} jobs`,
                frequency: frequency,
                font: {
                    size: Math.max(10, Math.min(16, 10 + (frequency / maxFreq) * 6))
                }
            });
        });
    }
    
    /**
     * Create edges between co-occurring skills
     */
    createEdges(coOccurrences) {
        // Find the maximum co-occurrence count for scaling
        const maxCoOccurrence = Math.max(...Object.values(coOccurrences));
        
        Object.entries(coOccurrences).forEach(([pair, count]) => {
            const [skill1, skill2] = pair.split('|');
            
            // Only create edge if both skills exist as nodes
            if (this.nodes.get(skill1) && this.nodes.get(skill2)) {
                const edgeWidth = Math.max(1, Math.min(5, 1 + (count / maxCoOccurrence) * 4));
                
                this.edges.add({
                    from: skill1,
                    to: skill2,
                    width: edgeWidth,
                    title: `${skill1} + ${skill2}<br>Co-occurrence: ${count} jobs`,
                    coOccurrence: count
                });
            }
        });
    }
    
    /**
     * Add event listeners for interactive features
     */
    addEventListeners() {
        if (!this.network) return;
        
        // Node click event
        this.network.on('click', (params) => {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                this.highlightNodeConnections(nodeId);
                this.showSkillDetails(nodeId);
            }
        });
        
        // Node hover event
        this.network.on('hoverNode', (params) => {
            const nodeId = params.node;
            this.highlightNodeConnections(nodeId, true);
        });
        
        // Node unhover event
        this.network.on('blurNode', (params) => {
            this.resetNodeHighlights();
        });
        
        // Double click to reset view
        this.network.on('doubleClick', (params) => {
            if (params.nodes.length === 0) {
                this.network.fit();
            }
        });
    }
    
    /**
     * Highlight connections for a specific node
     */
    highlightNodeConnections(nodeId, isHover = false) {
        // Reset all nodes and edges to default appearance
        this.resetNodeHighlights();
        
        // Get connected edges
        const connectedEdges = this.network.getConnectedEdges(nodeId);
        
        // Highlight the selected node
        this.nodes.update({
            id: nodeId,
            color: isHover ? '#3498db' : '#e74c3c',
            size: this.nodes.get(nodeId).size * 1.2
        });
        
        // Highlight connected edges
        connectedEdges.forEach(edgeId => {
            this.edges.update({
                id: edgeId,
                color: isHover ? '#74b9ff' : '#ff7675',
                width: this.edges.get(edgeId).width * 1.5
            });
        });
        
        // Highlight connected nodes
        const connectedNodes = new Set();
        connectedEdges.forEach(edgeId => {
            const edge = this.edges.get(edgeId);
            if (edge.from !== nodeId) connectedNodes.add(edge.from);
            if (edge.to !== nodeId) connectedNodes.add(edge.to);
        });
        
        connectedNodes.forEach(connectedNodeId => {
            this.nodes.update({
                id: connectedNodeId,
                color: isHover ? '#74b9ff' : '#f39c12',
                size: this.nodes.get(connectedNodeId).size * 1.1
            });
        });
    }
    
    /**
     * Reset all nodes and edges to default appearance
     */
    resetNodeHighlights() {
        // Reset all nodes to their original colors and sizes
        this.nodes.forEach(node => {
            const originalSize = Math.max(15, Math.min(50, 15 + (node.frequency / Math.max(...this.nodes.map(n => n.frequency))) * 35));
            this.nodes.update({
                id: node.id,
                color: this.getOriginalNodeColor(node.frequency),
                size: originalSize
            });
        });
        
        // Reset all edges to default appearance
        this.edges.forEach(edge => {
            this.edges.update({
                id: edge.id,
                color: '#848484',
                width: edge.width
            });
        });
    }
    
    /**
     * Get the original color for a node based on frequency
     */
    getOriginalNodeColor(frequency) {
        const maxFreq = Math.max(...this.nodes.map(n => n.frequency));
        const minFreq = Math.min(...this.nodes.map(n => n.frequency));
        const normalized = (frequency - minFreq) / (maxFreq - minFreq);
        
        if (normalized > 0.7) return '#e74c3c';
        if (normalized > 0.4) return '#f39c12';
        if (normalized > 0.2) return '#f1c40f';
        return '#2ecc71';
    }
    
    /**
     * Show detailed information about a skill
     */
    showSkillDetails(skillId) {
        const node = this.nodes.get(skillId);
        if (!node) return;
        
        // Create or update skill details panel
        let detailsPanel = document.getElementById('skill-details-panel');
        if (!detailsPanel) {
            detailsPanel = document.createElement('div');
            detailsPanel.id = 'skill-details-panel';
            detailsPanel.className = 'skill-details-panel';
            this.container.parentNode.appendChild(detailsPanel);
        }
        
        // Get connected skills
        const connectedEdges = this.network.getConnectedEdges(skillId);
        const connectedSkills = connectedEdges.map(edgeId => {
            const edge = this.edges.get(edgeId);
            return edge.from === skillId ? edge.to : edge.from;
        });
        
        detailsPanel.innerHTML = `
            <div class="skill-details-header">
                <h3>${skillId}</h3>
                <button onclick="this.parentElement.parentElement.remove()" class="close-btn">&times;</button>
            </div>
            <div class="skill-details-content">
                <p><strong>Frequency:</strong> ${node.frequency} job postings</p>
                <p><strong>Connected Skills:</strong> ${connectedSkills.length}</p>
                <div class="connected-skills">
                    <strong>Commonly paired with:</strong>
                    <ul>
                        ${connectedSkills.slice(0, 10).map(skill => `<li>${skill}</li>`).join('')}
                        ${connectedSkills.length > 10 ? `<li>... and ${connectedSkills.length - 10} more</li>` : ''}
                    </ul>
                </div>
            </div>
        `;
        
        detailsPanel.style.display = 'block';
    }
    
    /**
     * Show loading state
     */
    showLoading() {
        this.container.innerHTML = `
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <p>Loading skills network...</p>
            </div>
        `;
    }
    
    /**
     * Hide loading state
     */
    hideLoading() {
        const loadingContainer = this.container.querySelector('.loading-container');
        if (loadingContainer) {
            loadingContainer.remove();
        }
    }
    
    /**
     * Show error message
     */
    showError(message) {
        this.container.innerHTML = `
            <div class="error-container">
                <div class="error-icon">⚠️</div>
                <h3>Error Loading Skills Network</h3>
                <p>${message}</p>
                <button onclick="this.parentElement.parentElement.remove(); this.parentElement.parentElement.parentElement.innerHTML = this.getAttribute('data-original-content');" class="retry-btn">Retry</button>
            </div>
        `;
    }
    
    /**
     * Show no data message
     */
    showNoDataMessage() {
        this.container.innerHTML = `
            <div class="no-data-container">
                <div class="no-data-icon">📊</div>
                <h3>No Skills Data Available</h3>
                <p>Perform a job search first to see skills data.</p>
                <div class="no-data-actions">
                    <button onclick="window.location.href='#search-section'" class="btn btn-primary">Go to Job Search</button>
                    <button onclick="this.parentElement.parentElement.remove(); this.parentElement.parentElement.parentElement.innerHTML = this.getAttribute('data-original-content');" class="btn btn-secondary">Try Again</button>
                </div>
            </div>
        `;
    }
    
    /**
     * Show sample data message
     */
    showSampleDataMessage() {
        // Create a banner to show this is sample data
        const banner = document.createElement('div');
        banner.className = 'sample-data-banner';
        banner.innerHTML = `
            <div class="alert alert-warning alert-dismissible fade show" role="alert">
                <strong>📊 Sample Data:</strong> This shows sample skills data. Perform a job search to see real job market data.
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        // Insert banner at the top of the container
        this.container.insertBefore(banner, this.container.firstChild);
    }
    
    /**
     * Update the network with new data
     */
    async refreshData() {
        try {
            await this.fetchSkillsData();
            this.nodes.clear();
            this.edges.clear();
            this.createNodes(this.skillsData.data.skills);
            this.createEdges(this.skillsData.data.co_occurrences);
            this.network.fit();
        } catch (error) {
            console.error('Error refreshing data:', error);
        }
    }
    
    /**
     * Update the search context without recreating the entire graph
     */
    async updateSearchContext(useCurrentSearch, searchId) {
        this.useCurrentSearch = useCurrentSearch;
        this.searchId = searchId;
        
        try {
            await this.refreshData();
            console.log(`Search context updated: useCurrentSearch=${useCurrentSearch}, searchId=${searchId}`);
        } catch (error) {
            console.error('Error updating search context:', error);
            this.showError('Failed to update search context. Please try again.');
        }
    }
    
    /**
     * Update filter parameters
     */
    updateFilters(minFrequency, minCoOccurrence) {
        this.minFrequency = minFrequency;
        this.minCoOccurrence = minCoOccurrence;
    }
    
    /**
     * Get current search context
     */
    getSearchContext() {
        return {
            useCurrentSearch: this.useCurrentSearch,
            searchId: this.searchId,
            minFrequency: this.minFrequency,
            minCoOccurrence: this.minCoOccurrence
        };
    }
    
    /**
     * Destroy the network and clean up
     */
    destroy() {
        if (this.network) {
            this.network.destroy();
            this.network = null;
        }
        this.nodes.clear();
        this.edges.clear();
    }
}

/**
 * Initialize the skills network visualization
 * Call this function after the DOM is loaded and vis-network library is included
 */
function initializeSkillsNetwork(containerId = 'skills-network') {
    // Check if vis-network is available
    if (typeof vis === 'undefined') {
        console.error('vis-network library not found. Please include vis-network.js and vis-network.css');
        return;
    }
    
    // Create the visualizer instance
    window.skillsNetwork = new SkillsNetworkVisualizer(containerId);
    
    return window.skillsNetwork;
}

/**
 * Global function to refresh the skills network data
 */
function refreshSkillsNetwork() {
    if (window.skillsNetwork) {
        window.skillsNetwork.refreshData();
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Check if the container exists
    if (document.getElementById('skills-network')) {
        initializeSkillsNetwork();
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SkillsNetworkVisualizer;
}
