import logging
from typing import Dict, List, Optional, Any
from app.utils._neo4j_helpers import neo4j_driver
from app.routes.utils.ephemeris_calculator import EphemerisCalculator
from app.routes.constants import ORDINAL_NAMES

logger = logging.getLogger(__name__)


class Neo4jQueries:
    """
    Class to handle Neo4j queries related to planetary hours and geolocation data.
    """
    
    # Constants for planet names
    CLASSICAL_PLANETS = {"Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"}
    
    # URI prefix constant
    HOUR_URI_PREFIX = "monsieur:MagicHour"

    def __init__(self, ephemeris_calculator: Optional[EphemerisCalculator] = None):
        """
        Initialize Neo4jQueries with optional EphemerisCalculator.
        
        Args:
            ephemeris_calculator: Optional calculator for ephemeris data
        """
        self.driver = neo4j_driver
        self.ephemeris_calculator = ephemeris_calculator
        logger.debug(f"Initialized Neo4jQueries with EphemerisCalculator: {self.ephemeris_calculator}")

    def format_hour_name(self, hour_index: int) -> str:
        """
        Format hour name for Neo4j query.
        
        Args:
            hour_index: Hour number (1 to 12 for day, -1 to -12 for night)
                       Negative numbers automatically become Night hours
        
        Returns:
            Formatted hour name (e.g., "Hour_4_Night_Wednesday")
            
        Raises:
            ValueError: If EphemerisCalculator is not initialized
        """
        if not self.ephemeris_calculator:
            raise ValueError("EphemerisCalculator is required to format hour names.")
        
        # Use absolute value to get the hour number
        hour_num = abs(hour_index)
        
        # Validate hour number
        if hour_num < 1 or hour_num > 12:
            raise ValueError(f"Hour number must be between 1 and 12, got {hour_num}")
        
        # Use sign to determine day/night (negative becomes Night)
        day_segment = 'Day' if hour_index > 0 else 'Night'
        weekday = self.ephemeris_calculator.now_local.strftime('%A')
        
        # Creates URIs like "Hour_4_Night_Wednesday" from -4
        # or "Hour_4_Day_Wednesday" from 4 (matching database format)
        return f"Hour_{hour_num}_{day_segment}_{weekday}"
    
    def _build_hour_uri(self, hour_name: str) -> str:
        """
        Build complete URI for an hour node.
        
        Args:
            hour_name: Formatted hour name or full URI
            
        Returns:
            Complete URI string
        """
        # If hour_name already contains the prefix, return as-is
        if hour_name.startswith(self.HOUR_URI_PREFIX):
            return hour_name
        # Otherwise add the prefix
        return f"{self.HOUR_URI_PREFIX}/{hour_name}"

    def fetch_hour_data(self, hour_name: str, planetary_positions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch and process Neo4j data for the given hour.
        
        Args:
            hour_name: Name of the hour to fetch
            planetary_positions: Dictionary of current planetary positions
            
        Returns:
            Dictionary containing hour data and connections
            
        Raises:
            Exception: If Neo4j query fails
        """
        try:
            with self.driver.session() as session:
                query = """
                MATCH (hour {uri: $hour_uri})
                OPTIONAL MATCH (hour)-[r]-(connectedNode)
                RETURN 
                    hour,
                    type(r) AS relationshipType,
                    connectedNode,
                    properties(r) AS relationshipProperties,
                    labels(connectedNode) AS nodeLabels,
                    properties(connectedNode) AS nodeProperties
                """
                
                hour_uri = self._build_hour_uri(hour_name)
                results = session.run(query, hour_uri=hour_uri)
                
                return self._process_hour_results(results, planetary_positions)
                
        except Exception as e:
            logger.error(f"Error fetching hour data for {hour_name}: {e}", exc_info=True)
            raise

    def _process_hour_results(self, results, planetary_positions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process Neo4j query results for hour data.
        
        Args:
            results: Neo4j query results
            planetary_positions: Dictionary of current planetary positions
            
        Returns:
            Simplified dictionary of hour data
        """
        simplified = {
            "hour": None,
            "connections": [],
            "hour_ruler": None
        }
        
        records = [record.data() for record in results]
        
        if not records:
            logger.warning("No records found for hour query")
            return simplified
        
        # Set hour data from first record
        first_record = records[0]
        if first_record.get("hour"):
            simplified["hour"] = {
                "label": first_record["hour"].get("label"),
                "description": first_record["hour"].get("description"),
                "uri": first_record["hour"].get("uri"),
                **planetary_positions
            }
        
        # Process all connections
        for record in records:
            if record.get("connectedNode"):
                connection = self._build_connection(record)
                simplified["connections"].append(connection)
                
                # Extract hour ruling planet
                if self._is_hour_ruler(connection):
                    simplified["hour_ruler"] = connection["targetNode"]["label"]
        
        return simplified

    def _build_connection(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build a connection dictionary from a Neo4j record.
        
        Args:
            record: Neo4j record data
            
        Returns:
            Connection dictionary
        """
        connected_node = record["connectedNode"]
        
        return {
            "relationshipType": record["relationshipType"],
            "targetNode": {
                "label": (connected_node.get("label") or 
                         connected_node.get("description") or 
                         connected_node.get("uri")),
                "description": connected_node.get("description"),
                "uri": connected_node.get("uri"),
                "type": record["nodeLabels"],
            },
            "relationshipProperties": record.get("relationshipProperties", {})
        }

    def _is_hour_ruler(self, connection: Dict[str, Any]) -> bool:
        """
        Check if a connection represents an hour ruler relationship.
        
        Args:
            connection: Connection dictionary
            
        Returns:
            True if connection is an hour ruler
        """
        return (connection["relationshipType"] == "HOUR_RULED_BY" and 
                connection["targetNode"]["label"] in self.CLASSICAL_PLANETS)

    # def fetch_hour_graph(self, hour_name: str) -> List[Dict[str, Any]]:
    #     """
    #     Fetch hour-related network graph data for visualization.
    #     Shows the hour and ALL connected entities through any relationship,
    #     including planets, colors, metals, angels, etc.
        
    #     Args:
    #         hour_name: Name of the hour to fetch graph for
            
    #     Returns:
    #         List of Neo4j records containing graph data
            
    #     Raises:
    #         Exception: If Neo4j query fails
    #     """
    #     try:
    #         with self.driver.session() as session:
    #             query = """
    #             MATCH (hour {uri: $hour_uri})
    #             OPTIONAL MATCH (hour)-[r1]-(connectedNode)
    #             OPTIONAL MATCH (connectedNode)-[r2:HAS_ANALOGY_WITH]-(analogyNode)
    #             RETURN 
    #                 hour { .uri, .label, .description, .aliases } AS hour,
    #                 type(r1) AS hourRelationshipType,
    #                 connectedNode { .* } AS connectedNode,
    #                 properties(r1) AS hourRelationshipProperties,
    #                 labels(connectedNode) AS connectedNodeLabels,
    #                 analogyNode { .* } AS planet,
    #                 type(r2) AS planetRelationshipType,
    #                 properties(r2) AS planetRelationshipProperties,
    #                 labels(analogyNode) AS planetLabels
    #             """
                
    #             hour_uri = self._build_hour_uri(hour_name)
    #             results = session.run(query, hour_uri=hour_uri)
                
    #             return [record.data() for record in results]
                
    #     except Exception as e:
    #         logger.error(f"Error fetching hour graph for {hour_name}: {e}", exc_info=True)
    #         raise


    def fetch_hour_graph(self, hour_name: str) -> List[Dict[str, Any]]:
        """
        Fetch hour-related network graph data for visualization.
        Shows the hour and ALL connected entities through any relationship,
        including planets, colors, metals, angels, etc.
        
        Args:
            hour_name: Name of the hour to fetch graph for
            
        Returns:
            List of Neo4j records containing graph data
            
        Raises:
            Exception: If Neo4j query fails
        """
        print(f"🚀 fetch_hour_graph called with: {hour_name}")
        try:
            with self.driver.session() as session:
                query = """
                MATCH (hour {uri: $hour_uri})
                
                // First level: all direct connections to hour
                OPTIONAL MATCH (hour)-[r1]-(connectedNode)
                
                // Second level: all connections from first level nodes
                // BUT avoid going back to the hour node (circular reference)
                OPTIONAL MATCH (connectedNode)-[r2]-(secondLevel)
                WHERE NOT secondLevel = hour
                
                RETURN 
                    hour { .uri, .label, .description, .aliases } AS hour,
                    type(r1) AS hourRelationshipType,
                    connectedNode { .* } AS connectedNode,
                    properties(r1) AS hourRelationshipProperties,
                    labels(connectedNode) AS connectedNodeLabels,
                    
                    // Changed from 'planet' to 'secondLevelNode' to reflect it could be anything
                    secondLevel { .* } AS secondLevelNode,
                    type(r2) AS secondRelationshipType,
                    properties(r2) AS secondRelationshipProperties,
                    labels(secondLevel) AS secondLevelLabels
                """
                
                hour_uri = self._build_hour_uri(hour_name)
                print(f"🔍 Looking for hour with URI: {hour_uri}")
                
                # Debug: Check if hour exists
                debug_query = "MATCH (h) WHERE h.uri = $hour_uri RETURN h.uri, h.label, labels(h)"
                debug_result = session.run(debug_query, hour_uri=hour_uri)
                debug_data = [record.data() for record in debug_result]
                print(f"🔍 Hour node exists: {len(debug_data) > 0}")
                if debug_data:
                    print(f"🔍 Found hour: {debug_data[0]}")
                
                results = session.run(query, hour_uri=hour_uri)
                
                data = [record.data() for record in results]
                logger.info(f"Fetched {len(data)} records for hour graph: {hour_name}")
                
                return data
                
        except Exception as e:
            logger.error(f"Error fetching hour graph for {hour_name}: {e}", exc_info=True)
            raise

    def query_planetary_data(self, planetary_positions: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Query planetary data from Neo4j.
        
        Args:
            planetary_positions: Dictionary of planetary positions
            
        Returns:
            Planetary data dictionary or None
            
        TODO: Implement this method
        """
        logger.warning("query_planetary_data not yet implemented")
        # Implementation needed
        pass

    def query_aspects(self, planet_name: str) -> Optional[List[Dict[str, Any]]]:
        """
        Query aspects for a given planet.
        
        Args:
            planet_name: Name of the planet
            
        Returns:
            List of aspect dictionaries or None
            
        TODO: Implement this method
        """
        logger.warning("query_aspects not yet implemented")
        # Implementation needed
        pass

    def query_natal_chart(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Query natal chart data for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Natal chart dictionary or None
            
        TODO: Implement this method
        """
        logger.warning("query_natal_chart not yet implemented")
        # Implementation needed
        pass

    def close(self):
        """
        Close the Neo4j driver connection.
        Should be called when the application shuts down.
        """
        if self.driver:
            self.driver.close()
            logger.info("Neo4j driver closed")