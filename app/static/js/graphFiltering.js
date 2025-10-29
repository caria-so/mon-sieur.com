/**
* Filter the graph based on received ephemeris and hour data.
* This function is called from main.js after geolocationService has fetched the data.
* 
* The data flow is:
* 1. geolocationService.js gets location and makes API call to /api/geolocation_ephemeris
* 2. main.js receives this data and passes it to this function
* 3. This function extracts the current hour URI from the Neo4j data
* 4. The hour URI is used to filter and update the graph visualization
*
* @param {Object} data - The full data object from geolocation service containing:
*   - neo4j_data: Object with hour info and graph relationships
*   - planetary_positions: Current planetary positions
*   - other ephemeris data
* @param {number} latitude - User's latitude (not used in current implementation)
* @param {number} longitude - User's longitude (not used in current implementation)
* @throws {Error} If required hour data is missing from the response
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

export async function fetchCurrentHourAndFilter(data) {
    console.log('Raw hour data:', data);
    if (!data.neo4j_data || !data.neo4j_data.hour) {
        throw new Error('Missing hour data in response');
    }
    
    // Load node class colors before filtering
    await loadNodeClassColors();
    
    const currentHourUri = data.neo4j_data.hour.uri;
    console.log('Current hour URI for filtering:', currentHourUri);
    filterByHour(currentHourUri);
}


function filterByHour(hourName) {
    fetch('/api/filter_by_hour', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ hour_name: hourName }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.error || !data.nodes || !data.edges) {
                console.error('Error or no data received:', data);
                return;
            }
            console.log('Filtered Data Received:', data);
            
            // Only exclude the MagicHourEntity class, but keep the specific hour node
            const excludedNodeLabels = ['MagicHour'];
            const excludedEdgeLabels = []; // Add edge types to exclude if needed

            // Filter and create nodes with class-based coloring
            const filteredNodes = new vis.DataSet(data.nodes
                .filter(node => !excludedNodeLabels.includes(node.label))
                .map(node => {
                    const isCurrentHour = node.id === hourName;
                    
                    // Get node class (first label)
                    const nodeClass = node.type && node.type.length > 0 ? node.type[0] : 'Default';
                    
                    // Check if this is a magic hour node (but not the current one)
                    const isMagicHour = nodeClass === 'MagicHour' || (node.type && node.type.includes('MagicHour'));
                    const isOtherMagicHour = isMagicHour && !isCurrentHour;
                    
                    // Get color from class-based color scheme
                    let color = getNodeColorByClass(nodeClass);
                    let size = 20;
                    
                    // Special highlighting for current hour
                    if (isCurrentHour) {
                        color = { background: '#FFD700', border: '#DAA520' }; // Gold highlight
                        size = 25;
                    } else if (isOtherMagicHour) {
                        // Gray out other magic hours - much more subdued
                        color = { background: '#F5F5F5', border: '#CCCCCC' };
                        size = 14; // Much smaller
                    } else {
                        // Slightly larger for important classes
                        if (['Planet', 'Angel', 'Demon'].includes(nodeClass)) {
                            size = 22;
                        }
                    }
                    
                    return {
                        id: node.id,
                        label: node.label || 'Unnamed Node',
                        title: `${nodeClass}: ${node.description || 'No description'}`,
                        color: color,
                        size: size,
                        opacity: isOtherMagicHour ? 0.4 : 1.0, // Make other magic hours semi-transparent
                        font: isOtherMagicHour ? {
                            color: '#BBBBBB',  // Very light gray text
                            size: 10,          // Smaller font
                            strokeWidth: 0     // No outline
                        } : undefined
                    };
                }));

         
            // Filter and create edges
            const filteredEdges = new vis.DataSet(data.edges
                .filter(edge => !excludedEdgeLabels.includes(edge.label)) // Filter out unwanted edges
                .map(edge => {
                    // Check if edge connects to other magic hours
                    const fromNode = data.nodes.find(n => n.id === edge.from);
                    const toNode = data.nodes.find(n => n.id === edge.to);
                    
                    const fromIsMagicHour = fromNode && (fromNode.type && fromNode.type.includes('MagicHour'));
                    const toIsMagicHour = toNode && (toNode.type && toNode.type.includes('MagicHour'));
                    const fromIsCurrentHour = edge.from === hourName;
                    const toIsCurrentHour = edge.to === hourName;
                    
                    // Gray out edges connected to non-current magic hours
                    const isConnectedToOtherMagicHour = (fromIsMagicHour && !fromIsCurrentHour) || (toIsMagicHour && !toIsCurrentHour);
                    
                    return {
                        from: edge.from,
                        to: edge.to,
                        label: edge.label,
                        title: JSON.stringify(edge.properties, null, 2), // Show properties on hover
                        arrows: {
                            to: {
                                enabled: true,
                                scaleFactor: 0.5  // Smaller arrows
                            }
                        },
                        font: {
                            size: 10,      // Smaller font size
                            color: isConnectedToOtherMagicHour ? '#CCC' : '#666', // Lighter color for grayed edges
                            face: 'arial', // Regular font
                            strokeWidth: 0, // No text outline
                            align: 'middle',  // Can be 'horizontal' or 'middle'
                            vadjust: 0,         // Adjust vertical position of the label
                            background: 'white',
                            backgroundPadding: { top: 2, right: 2, bottom: 2, left: 2 } 
                        },
                        color: { 
                            color: isConnectedToOtherMagicHour ? '#E0E0E0' : '#006400', 
                            opacity: isConnectedToOtherMagicHour ? 0.3 : 0.6 
                        },
                        width: isConnectedToOtherMagicHour ? 0.5 : 1,         // Thinner lines for grayed edges
                        smooth: {
                            enabled: true,
                            type: 'continuous',
                            roundness: 0.5
                        }
                    };
                }));

            console.log('Filtered nodes count:', filteredNodes.length);
            console.log('Filtered edges count:', filteredEdges.length);
            console.log('Sample nodes:', filteredNodes.get().slice(0, 3));
            console.log('Sample edges:', filteredEdges.get().slice(0, 3));

            // Update existing network instead of creating new one
            if (window.network) {
                window.network.setData({
                    nodes: filteredNodes,
                    edges: filteredEdges
                });
                window.network.fit();
                console.log('Updated existing network with filtered data');
                return;
            }

            // Create a new network only if one doesn't exist
            const container = document.getElementById('network');
            const options = {
                layout: { improvedLayout: false },
                physics: {
                    enabled: true,
                    solver: 'forceAtlas2Based',
                    forceAtlas2Based: {
                        gravitationalConstant: -150,     // Reduced from -50 for less repulsion
                        centralGravity: 0.005,          // Reduced from 0.01 for gentler center pull
                        springLength: 200,              // Keep the desired distance
                        springConstant: 0.02,           // Reduced from 0.08 for softer springs
                        damping: 0.15,                  // Reduced from 0.4 for smoother movement
                        avoidOverlap: 0.5
                    },
                    stabilization: { iterations: 250 }
                },
                interaction: { hover: true, tooltipDelay: 200 },
                nodes: { shape: 'dot' },
                edges: { 
                    smooth: { enabled: true, type: 'dynamic' },
                    width: 2,
                    arrows: 'to'
                }
            };

            window.network = new vis.Network(container, { 
                nodes: filteredNodes, 
                edges: filteredEdges 
            }, options);

            // Add click event handler for showing node details
            window.network.on('click', function(params) {
                if (params.nodes.length > 0) {
                    const nodeId = params.nodes[0];
                    const node = filteredNodes.get(nodeId);
                    if (node && window.showNodeDetails) {
                        window.showNodeDetails(node);
                    }
                }
            });

            window.network.fit();
            console.log('Network Updated with Filtered Data');
        })
        .catch((error) => {
            console.error('Error fetching or processing filtered data:', error);
        });
}







