// initGraph.js
/**
 * Graph initialization and filtering utilities.
 * Contains network configuration and node filtering logic.
 * Used by graphFiltering.js for setting up and managing the graph visualization.
 */

// Global variable to store node class colors
let nodeClassColors = {};

// Function to fetch and cache node class colors from backend
async function loadNodeClassColors() {
    if (Object.keys(nodeClassColors).length === 0) {
        try {
            const response = await fetch('/api/node_colors');
            if (response.ok) {
                nodeClassColors = await response.json();
                console.log('Node class colors loaded:', Object.keys(nodeClassColors).length, 'classes');
            } else {
                console.error('Failed to load node class colors');
            }
        } catch (error) {
            console.error('Error loading node class colors:', error);
        }
    }
}

// Function to get color for a node class
function getNodeColorByClass(nodeClass) {
    const classColor = nodeClassColors[nodeClass];
    if (classColor) {
        return classColor;
    }
    
    // Return default color if class not found
    return nodeClassColors['Default'] || { background: '#D3D3D3', border: '#A9A9A9' };
}


// Node filtering configuration
export const nodeFilters = {
    // List of node patterns to exclude from visualization
    excludedPatterns: [
        'MagicHour',
    ],

    /**
     * Check if a node should be excluded from visualization
     * @param {Object} node - Node to check
     * @returns {boolean} True if node should be excluded
     */
    shouldExcludeNode: (node) => {
        return nodeFilters.excludedPatterns.some(pattern => 
            node.id === pattern || node.label === pattern
        );
    },

    /**
     * Filter nodes based on exclusion patterns
     * @param {Array} nodes - Array of nodes to filter
     * @returns {Array} Filtered nodes array
     */
    getFilteredNodes: (nodes) => {
        return nodes.filter(node => !nodeFilters.shouldExcludeNode(node));
    },



    /**
     * Get edges between filtered nodes
     * @param {Array} edges - Array of edges
     * @param {Array} filteredNodes - Array of filtered nodes
     * @returns {Array} Filtered edges array
     */
    getFilteredEdges: (edges, filteredNodes) => {
        return edges.filter(edge => 
            filteredNodes.some(n => n.id === edge.from) && 
            filteredNodes.some(n => n.id === edge.to)
        );
    }
};


/**
 * Initialize the network visualization with nodes and edges
 * @param {Array} nodes - Array of nodes to visualize
 * @param {Array} edges - Array of edges to visualize
 * @returns {vis.Network} Initialized network instance
 */

export function initializeNetwork(nodes = [], edges = []) {
    const container = document.getElementById('network');
    const options = {
        layout: { improvedLayout: false },
        physics: {
            enabled: true,
            solver: 'forceAtlas2Based',
            forceAtlas2Based: {
                gravitationalConstant: -150,    // Stronger repulsion to spread nodes
                centralGravity: 0.01,           // Moderate center pull
                springLength: 250,              // Longer default distance
                springConstant: 0.08,           // Firmer springs for better structure
                damping: 0.4,                   // More damping for stability
                avoidOverlap: 1.0               // Full overlap avoidance
            },
            stabilization: { 
                enabled: true,
                iterations: 100,                // Reduced iterations
                updateInterval: 50,
                onlyDynamicEdges: false,
                fit: true
            }
        },
        interaction: { hover: true, tooltipDelay: 200 },
        nodes: { shape: 'dot', size: 16 },
        edges: { 
            smooth: { type: 'continuous' },     // Changed from dynamic
            width: 1                            // Thinner edges
        }
    };

    const network = new vis.Network(container, { nodes, edges }, options);

    // Add click event handler for showing node details
    network.on('click', function(params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            const node = nodes.get(nodeId);
            if (node && window.showNodeDetails) {
                window.showNodeDetails(node);
            }
        }
    });

    // Enable physics on double-click
    network.on('doubleClick', () => {
        network.setOptions({ physics: { enabled: true } });
        setTimeout(() => {
            network.setOptions({ physics: { enabled: false } });
        }, 3000); // Allow movement for 3 seconds
    });

    return network;
}



/**
 * Load and initialize the full graph visualization
 * Fetches graph data from the API and sets up the initial network view
 * with default styling and filtering
 */

export async function loadFullGraph() {
    console.log('🚀 Starting loadFullGraph...');
    const startTime = performance.now();
    
    // Load node class colors first
    await loadNodeClassColors();
    
    try {
        const response = await fetch('/api/graph_data');
        console.log(`📡 Graph data fetched in ${(performance.now() - startTime).toFixed(0)}ms`);
        
        const data = await response.json();
        console.log(`📊 Graph data parsed in ${(performance.now() - startTime).toFixed(0)}ms`);
        
        if (!data.nodes || !data.edges) {
            console.error('No graph data received:', data);
            return;
        }

        // Exclude class nodes (e.g., "MagicHourEntity") and specific edges
        const excludedNodeLabels = ['MagicHour'];
        const excludedEdgeLabels = ['IS_PART_OF_DAY', 'HOUR_RULED_BY'];

        const nodes = new vis.DataSet(data.nodes.filter(node => {
            return !excludedNodeLabels.includes(node.label);
        }).map(node => {
            // Get node class (first label from type array)
            const nodeClass = node.type && node.type.length > 0 ? node.type[0] : 'Default';
            
            // Get class-based color
            const color = getNodeColorByClass(nodeClass);
            
            return {
                ...node, // Spread existing node properties
                shape: 'dot',
                size: ['Planet', 'Angel', 'Demon'].includes(nodeClass) ? 22 : 16,
                color: color,
                title: `${nodeClass}: ${node.title || 'No description'}`
            };
        }));

        const edges = new vis.DataSet(data.edges.filter(edge => {
            return !excludedEdgeLabels.includes(edge.label);
        }).map(edge => ({
            ...edge, // Spread existing edge properties
            smooth: { type: 'dynamic' },
            width: 2,
            color: { color: '#666' },
            label: '', // Hide edge labels in default view
        })));

        console.log(`🔧 About to initialize network with ${nodes.length} nodes, ${edges.length} edges...`);
        const networkStartTime = performance.now();
        
        window.network = initializeNetwork(nodes, edges);
        
        console.log(`✅ Network initialized in ${(performance.now() - networkStartTime).toFixed(0)}ms`);
        console.log(`🏁 Total loadFullGraph time: ${(performance.now() - startTime).toFixed(0)}ms`);
        
    } catch (error) {
        console.error('Error fetching graph data:', error);
    }
}
