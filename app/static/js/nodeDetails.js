/**
 * Node Details Offcanvas Management
 * Handles displaying node information and managing relationships
 */

let currentSelectedNode = null;
let nodeDetailsOffcanvas = null;

// Initialize the offcanvas component when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const offcanvasElement = document.getElementById('nodeDetailsOffcanvas');
    if (offcanvasElement) {
        nodeDetailsOffcanvas = new bootstrap.Offcanvas(offcanvasElement);
    }
    
    // Set up form submission handler
    const addRelationshipForm = document.getElementById('addRelationshipForm');
    if (addRelationshipForm) {
        addRelationshipForm.addEventListener('submit', handleAddRelationship);
    }
    
    // Set up target node search
    const targetNodeInput = document.getElementById('targetNode');
    if (targetNodeInput) {
        targetNodeInput.addEventListener('input', handleNodeSearch);
    }
});

/**
 * Display node details in the offcanvas
 * @param {Object} node - The node object to display
 */
function showNodeDetails(node) {
    currentSelectedNode = node;
    
    // Debug: Log the node data
    console.log('Node data received:', node);
    
    // Update node information
    document.getElementById('nodeLabel').textContent = node.label || 'Unnamed Node';
    
    // Try different possible description fields
    let description = node.description || node.properties?.description || 'No description available';
    
    // If we still don't have a description, try parsing the title field if it contains JSON
    if (description === 'No description available' && node.title) {
        try {
            const titleData = JSON.parse(node.title);
            description = titleData.description || 'No description available';
        } catch (e) {
            // If title is not JSON, use it as description
            description = node.title;
        }
    }
    
    document.getElementById('nodeDescription').textContent = description;
    
    document.getElementById('nodeType').textContent = (node.type && node.type.length > 0) ? node.type.join(', ') : 'Unknown';
    document.getElementById('nodeUri').textContent = node.id || 'No URI';
    
    // Load and display existing relationships
    loadNodeRelationships(node.id);
    
    // Show the offcanvas
    if (nodeDetailsOffcanvas) {
        nodeDetailsOffcanvas.show();
    }
}

// Make showNodeDetails available globally
window.showNodeDetails = showNodeDetails;

/**
 * Load and display existing relationships for a node
 * @param {string} nodeId - The URI/ID of the node
 */
async function loadNodeRelationships(nodeId) {
    try {
        console.log('Loading relationships for node:', nodeId);
        const response = await fetch('/api/node_relationships', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ node_id: nodeId })
        });
        
        if (response.ok) {
            const relationships = await response.json();
            console.log('Relationships received:', relationships);
            displayRelationships(relationships);
        } else {
            console.error('Failed to load relationships', response.status);
            displayRelationships([]);
        }
    } catch (error) {
        console.error('Error loading relationships:', error);
        displayRelationships([]);
    }
}

/**
 * Display relationships in the UI
 * @param {Array} relationships - Array of relationship objects
 */
function displayRelationships(relationships) {
    const relationshipsList = document.getElementById('relationshipsList');
    
    if (!relationships || relationships.length === 0) {
        relationshipsList.innerHTML = '<p class="text-muted">No relationships found.</p>';
        return;
    }
    
    const relationshipsHtml = relationships.map(rel => {
        // Debug log each relationship
        console.log('Processing relationship:', rel);
        
        const direction = rel.direction || 'unknown';
        const arrow = direction === 'outgoing' ? '→' : '←';
        const directionClass = direction === 'outgoing' ? 'text-primary' : 'text-success';
        const relType = rel.type || 'UNKNOWN_TYPE';
        const targetLabel = rel.target_label || rel.target_id || 'Unknown Target';
        
        return `
        <div class="card mb-2">
            <div class="card-body py-2">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <strong>${relType}</strong>
                        <span class="badge bg-light text-dark ms-1">${direction}</span>
                        <br>
                        <small class="text-muted ${directionClass}">${arrow} ${targetLabel}</small>
                        ${rel.description ? `<br><small>${rel.description}</small>` : ''}
                    </div>
                    <button class="btn btn-sm btn-outline-danger" onclick="removeRelationship('${rel.id}')">
                        <i class="ph ph-trash"></i>
                    </button>
                </div>
            </div>
        </div>
        `;
    }).join('');
    
    relationshipsList.innerHTML = relationshipsHtml;
}

/**
 * Handle adding a new relationship
 * @param {Event} event - Form submission event
 */
async function handleAddRelationship(event) {
    event.preventDefault();
    
    if (!currentSelectedNode) {
        alert('No node selected');
        return;
    }
    
    const relationshipType = document.getElementById('relationshipType').value;
    const targetNode = document.getElementById('targetNode').value;
    const description = document.getElementById('relationshipDescription').value;
    
    if (!relationshipType || !targetNode) {
        alert('Please fill in all required fields');
        return;
    }
    
    try {
        const response = await fetch('/api/add_relationship', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                source_node: currentSelectedNode.id,
                target_node: targetNode,
                relationship_type: relationshipType,
                description: description
            })
        });
        
        if (response.ok) {
            // Clear form
            document.getElementById('addRelationshipForm').reset();
            document.getElementById('nodeSearchResults').style.display = 'none';
            
            // Reload relationships
            loadNodeRelationships(currentSelectedNode.id);
            
            // Optionally refresh the graph
            if (window.network) {
                // You might want to reload the graph data here
                console.log('Relationship added successfully');
            }
        } else {
            const error = await response.json();
            alert('Failed to add relationship: ' + (error.message || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error adding relationship:', error);
        alert('Error adding relationship');
    }
}

/**
 * Handle node search for relationship targets
 * @param {Event} event - Input event
 */
async function handleNodeSearch(event) {
    const query = event.target.value.trim();
    const resultsContainer = document.getElementById('nodeSearchResults');
    
    if (query.length < 2) {
        resultsContainer.style.display = 'none';
        return;
    }
    
    try {
        const response = await fetch('/api/search_nodes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        });
        
        if (response.ok) {
            const nodes = await response.json();
            displaySearchResults(nodes, resultsContainer);
        } else {
            console.error('Failed to search nodes');
        }
    } catch (error) {
        console.error('Error searching nodes:', error);
    }
}

/**
 * Display node search results
 * @param {Array} nodes - Array of node objects
 * @param {HTMLElement} container - Container element
 */
function displaySearchResults(nodes, container) {
    if (!nodes || nodes.length === 0) {
        container.innerHTML = '<div class="list-group-item text-muted">No nodes found</div>';
        container.style.display = 'block';
        return;
    }
    
    const resultsHtml = nodes.map(node => `
        <button type="button" class="list-group-item list-group-item-action" onclick="selectTargetNode('${node.id}', '${node.label}')">
            <div class="d-flex w-100 justify-content-between">
                <h6 class="mb-1">${node.label}</h6>
                <small class="text-muted">${node.type ? node.type[0] : 'Unknown'}</small>
            </div>
            ${node.description ? `<p class="mb-1 small">${node.description}</p>` : ''}
            <small class="text-muted">${node.id}</small>
        </button>
    `).join('');
    
    container.innerHTML = resultsHtml;
    container.style.display = 'block';
}

/**
 * Select a target node for relationship creation
 * @param {string} nodeId - The node URI/ID
 * @param {string} nodeLabel - The node label
 */
window.selectTargetNode = function(nodeId, nodeLabel) {
    document.getElementById('targetNode').value = nodeId;
    document.getElementById('nodeSearchResults').style.display = 'none';
};

/**
 * Remove a relationship
 * @param {string} relationshipId - The relationship ID to remove
 */
window.removeRelationship = async function(relationshipId) {
    if (!confirm('Are you sure you want to remove this relationship?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/remove_relationship', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ relationship_id: relationshipId })
        });
        
        if (response.ok) {
            // Reload relationships
            if (currentSelectedNode) {
                loadNodeRelationships(currentSelectedNode.id);
            }
        } else {
            alert('Failed to remove relationship');
        }
    } catch (error) {
        console.error('Error removing relationship:', error);
        alert('Error removing relationship');
    }
};