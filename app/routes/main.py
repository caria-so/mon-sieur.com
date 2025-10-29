from flask import Blueprint, render_template, current_app, jsonify, request, Response
from app.routes.constants import neo4j_driver, NODE_CLASS_COLORS
import json



main_bp = Blueprint('main_bp', __name__)

driver = neo4j_driver

# Fetch Network Graph from Neo4j
@main_bp.route('/api/graph_data')
def get_graph_data():
    # Debug: Check what MagicHour nodes exist
    with driver.session() as debug_session:
        debug_result = debug_session.run("MATCH (h:MagicHour) RETURN h.uri, h.label LIMIT 5")
        magic_hours = [record.data() for record in debug_result]
        print(f"🕐 Found {len(magic_hours)} MagicHour nodes:")
        for hour in magic_hours:
            print(f"  - {hour}")
    
    query = """
    MATCH (n)-[r]->(m)
    RETURN n, r, m
    """
    with driver.session() as session:
        results = session.run(query)
        nodes = {}
        edges = []

        for record in results:
            node1 = record["n"]
            node2 = record["m"]
            relationship = record["r"]

            for node in [node1, node2]:
                # Use URI as the consistent identifier instead of Neo4j internal ID
                node_uri = node.get("uri")
                if node_uri and node_uri not in nodes:
                    label = node.get("label") or node_uri
                    nodes[node_uri] = {
                        "id": node_uri,  # Use URI as ID for consistency with filtering
                        "label": label,
                        "title": json.dumps(dict(node.items()), indent=2),
                        "properties": dict(node.items()),
                        "type": list(node.labels)  # Add node labels for filtering
                    }

            # Only add edge if both nodes have URIs
            node1_uri = node1.get("uri")
            node2_uri = node2.get("uri")
            if node1_uri and node2_uri:
                edges.append({
                    "from": node1_uri,
                    "to": node2_uri,
                    "label": relationship.type,
                    "title": json.dumps(dict(relationship.items()), indent=2),
                    "properties": dict(relationship.items())
                })

    return jsonify({"nodes": list(nodes.values()), "edges": edges})


# API endpoint to serve node class colors
@main_bp.route('/api/node_colors')
def get_node_colors():
    return jsonify(NODE_CLASS_COLORS)


# API endpoint to get relationships for a node
@main_bp.route('/api/node_relationships', methods=['POST'])
def get_node_relationships():
    data = request.json
    node_id = data.get('node_id')
    
    if not node_id:
        return jsonify({"error": "Missing node_id parameter"}), 400
    
    try:
        with driver.session() as session:
            # Simpler approach: separate outgoing and incoming queries
            outgoing_query = """
            MATCH (n {uri: $node_id})-[r]->(connected)
            RETURN 
                type(r) as relationship_type,
                connected.uri as target_id,
                connected.label as target_label,
                connected.description as target_description,
                properties(r) as relationship_properties,
                id(r) as relationship_id,
                'outgoing' as direction
            """
            
            incoming_query = """
            MATCH (connected)-[r]->(n {uri: $node_id})
            RETURN 
                type(r) as relationship_type,
                connected.uri as target_id,
                connected.label as target_label,
                connected.description as target_description,
                properties(r) as relationship_properties,
                id(r) as relationship_id,
                'incoming' as direction
            """
            
            relationships = []
            
            # Get outgoing relationships
            outgoing_results = session.run(outgoing_query, node_id=node_id)
            for record in outgoing_results:
                relationships.append({
                    "id": str(record["relationship_id"]),
                    "type": record["relationship_type"],
                    "target_id": record["target_id"],
                    "target_label": record["target_label"],
                    "target_description": record["target_description"],
                    "direction": record["direction"],
                    "description": record["relationship_properties"].get("description", "") if record["relationship_properties"] else "",
                    "properties": dict(record["relationship_properties"]) if record["relationship_properties"] else {}
                })
            
            # Get incoming relationships
            incoming_results = session.run(incoming_query, node_id=node_id)
            for record in incoming_results:
                relationships.append({
                    "id": str(record["relationship_id"]),
                    "type": record["relationship_type"],
                    "target_id": record["target_id"],
                    "target_label": record["target_label"],
                    "target_description": record["target_description"],
                    "direction": record["direction"],
                    "description": record["relationship_properties"].get("description", "") if record["relationship_properties"] else "",
                    "properties": dict(record["relationship_properties"]) if record["relationship_properties"] else {}
                })
            
            # Sort: outgoing first, then incoming, then by type and target
            relationships.sort(key=lambda x: (x["direction"] != "outgoing", x["type"], x["target_label"]))
            
            return jsonify(relationships)
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# API endpoint to search for nodes
@main_bp.route('/api/search_nodes', methods=['POST'])
def search_nodes():
    data = request.json
    query = data.get('query', '').strip()
    
    if len(query) < 2:
        return jsonify([])
    
    try:
        with driver.session() as session:
            search_query = """
            MATCH (n)
            WHERE n.label CONTAINS $query OR n.description CONTAINS $query OR n.uri CONTAINS $query
            RETURN n.uri as id, n.label as label, n.description as description, labels(n) as type
            LIMIT 10
            """
            results = session.run(search_query, query=query)
            
            nodes = []
            for record in results:
                nodes.append({
                    "id": record["id"],
                    "label": record["label"] or record["id"],
                    "description": record["description"],
                    "type": record["type"]
                })
            
            return jsonify(nodes)
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# API endpoint to add a new relationship
@main_bp.route('/api/add_relationship', methods=['POST'])
def add_relationship():
    data = request.json
    source_node = data.get('source_node')
    target_node = data.get('target_node')
    relationship_type = data.get('relationship_type')
    description = data.get('description', '')
    
    if not all([source_node, target_node, relationship_type]):
        return jsonify({"error": "Missing required parameters"}), 400
    
    try:
        with driver.session() as session:
            # Check if both nodes exist
            check_query = """
            MATCH (source {uri: $source}), (target {uri: $target})
            RETURN source, target
            """
            check_result = session.run(check_query, source=source_node, target=target_node)
            if not check_result.single():
                return jsonify({"error": "One or both nodes do not exist"}), 400
            
            # Create the relationship
            create_query = """
            MATCH (source {uri: $source}), (target {uri: $target})
            CREATE (source)-[r:%s {description: $description, created_at: datetime()}]->(target)
            RETURN id(r) as relationship_id
            """ % relationship_type
            
            result = session.run(create_query, 
                               source=source_node, 
                               target=target_node, 
                               description=description)
            
            relationship_id = result.single()["relationship_id"]
            
            return jsonify({
                "message": "Relationship created successfully",
                "relationship_id": str(relationship_id)
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# API endpoint to remove a relationship
@main_bp.route('/api/remove_relationship', methods=['DELETE'])
def remove_relationship():
    data = request.json
    relationship_id = data.get('relationship_id')
    
    if not relationship_id:
        return jsonify({"error": "Missing relationship_id parameter"}), 400
    
    try:
        with driver.session() as session:
            query = """
            MATCH ()-[r]-()
            WHERE id(r) = $relationship_id
            DELETE r
            RETURN count(r) as deleted_count
            """
            result = session.run(query, relationship_id=int(relationship_id))
            deleted_count = result.single()["deleted_count"]
            
            if deleted_count > 0:
                return jsonify({"message": "Relationship deleted successfully"})
            else:
                return jsonify({"error": "Relationship not found"}), 404
                
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Landing page
@main_bp.route('/')
def landing_page():
    return render_template('landing_page.html')

# Admin Page Route
@main_bp.route('/admin')
def admin_page():
    return render_template('admin_page.html')




# @main_bp.route('/topics', methods=['GET'])
# def list_topics():
#     """
#     Renders a page that lists all topics with options to edit or delete each topic.
#     """
#     graph = current_app.config['graph']

#     try:
#         # Retrieve all topic nodes from the database
#         query = "MATCH (t:Topic) RETURN t.id as id, t.name as name, t.type as type, t.subtype as subtype"
#         topics = graph.run(query).data()

#         return render_template('pages/topics_all.html', topics=topics), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500



# @main_bp.route('/analogy_systems', methods=['GET'])
# def list_and_get_systems():
#     """
#     Handles both rendering the list of analogy systems for an HTML page and returning
#     systems in JSON format for dropdown population based on request type.
#     """
#     graph = current_app.config['graph']

#     try:
#         # Retrieve all system nodes from the database
#         query = "MATCH (s:AnalogySystem) RETURN s.id as id, s.name as name"
#         systems = graph.run(query).data()

#         if request.accept_mimetypes.best == 'application/json':
#             # If the request expects JSON, return JSON data (for the dropdown)
#             return jsonify(systems), 200

#         # Otherwise, render the systems page
#         return render_template('pages/analogy_systems_all.html', systems=systems), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
