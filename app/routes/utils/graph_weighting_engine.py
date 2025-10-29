"""
Graph Weighting Engine for Astrological Correspondences
======================================================

Multi-dimensional weighting system for magical correspondences that considers:
1. Graph Proximity (network distance)
2. Astrological Authority (planetary strength, dignities)
3. Temporal Relevance (hour/day rulers, time conflicts)
4. Elemental Dominance (building blocks alignment)

Research prototype to analyze weighting strategies before integration.
"""

from typing import Dict, List, Any, Tuple
import math

# Mock constants for testing
ESSENTIAL_DIGNITIES = {
    'Sun': {'rulership': 'Leo', 'exaltation': 'Aries', 'detriment': 'Aquarius', 'fall': 'Libra'},
    'Moon': {'rulership': 'Cancer', 'exaltation': 'Taurus', 'detriment': 'Capricorn', 'fall': 'Scorpio'},
    'Mercury': {'rulership': 'Gemini', 'exaltation': 'Virgo', 'detriment': 'Sagittarius', 'fall': 'Pisces'},
    'Venus': {'rulership': 'Taurus', 'exaltation': 'Pisces', 'detriment': 'Scorpio', 'fall': 'Virgo'},
    'Mars': {'rulership': 'Aries', 'exaltation': 'Capricorn', 'detriment': 'Libra', 'fall': 'Cancer'},
    'Jupiter': {'rulership': 'Sagittarius', 'exaltation': 'Cancer', 'detriment': 'Gemini', 'fall': 'Capricorn'},
    'Saturn': {'rulership': 'Capricorn', 'exaltation': 'Libra', 'detriment': 'Cancer', 'fall': 'Aries'}
}


class GraphWeightingEngine:
    """
    Prototype engine for weighting magical correspondences based on multiple factors.
    """
    
    def __init__(self):
        self.weight_factors = {
            'graph_proximity': 0.3,
            'astrological_authority': 0.4,
            'temporal_relevance': 0.2,
            'elemental_dominance': 0.1
        }
    
    # ========================================
    # 1. GRAPH PROXIMITY WEIGHTING
    # ========================================
    
    def calculate_graph_proximity_weight(self, source_entity: str, target_entity: str, 
                                       graph_data: Dict) -> float:
        """
        Calculate weight based on network distance in the graph.
        
        Args:
            source_entity: Starting node (e.g., "Mars")
            target_entity: Target node (e.g., "Iron")
            graph_data: Current graph structure
            
        Returns:
            float: Weight from 0.1 to 1.0 based on graph distance
        """
        # Find shortest path between source and target
        path_length = self._find_shortest_path_length(source_entity, target_entity, graph_data)
        
        if path_length == 1:  # Direct connection
            return 1.0
        elif path_length == 2:  # 1 intermediary
            return 0.7
        elif path_length == 3:  # 2 intermediaries  
            return 0.4
        elif path_length == 4:  # 3 intermediaries
            return 0.2
        else:  # 4+ hops or no connection
            return 0.1
    
    def _find_shortest_path_length(self, source: str, target: str, graph_data: Dict) -> int:
        """
        Simplified BFS to find shortest path length.
        TODO: Implement proper graph traversal when we have real graph data.
        """
        # Placeholder implementation
        if source == target:
            return 0
        
        # Mock some common direct connections for testing
        direct_connections = {
            "Mars": ["Iron", "Sachiel", "Tuesday", "Red"],
            "Sun": ["Gold", "Michael", "Sunday", "Yellow"],
            "Moon": ["Silver", "Gabriel", "Monday", "Silver"]
        }
        
        if target in direct_connections.get(source, []):
            return 1
        else:
            return 3  # Assume 3-hop for everything else in prototype
    
    # ========================================
    # 2. ASTROLOGICAL AUTHORITY WEIGHTING  
    # ========================================
    
    def calculate_astrological_authority(self, planet: str, planetary_positions: Dict) -> float:
        """
        Calculate planetary authority based on current astrological conditions.
        Borrows concepts from heatmap calculator but focused on authority.
        
        Args:
            planet: Planet name (e.g., "Mars")
            planetary_positions: Current ephemeris data
            
        Returns:
            float: Authority score from 0.1 to 3.0
        """
        if planet not in planetary_positions:
            return 0.5  # Default for missing data
        
        position = planetary_positions[planet]
        authority = 1.0  # Base authority
        
        # 1. Essential Dignity Modifier
        sign = position.get("sign", "")
        dignity_mult = self._get_dignity_multiplier(planet, sign)
        authority *= dignity_mult
        
        # 2. Visibility (Above/Below Horizon)
        altitude = position.get("altitude", 0)
        if altitude >= 0:
            visibility_mult = 1.0 + (altitude / 90) * 0.5  # Up to 1.5x for zenith
        else:
            visibility_mult = 0.6  # Penalty for below horizon
        authority *= visibility_mult
        
        # 3. Combustion/Cazimi Effects
        if position.get("is_cazimi", False):
            authority *= 1.3  # Cazimi bonus
        elif position.get("is_combust", False):
            authority *= 0.3  # Major combustion penalty
        
        # 4. Retrograde Effects  
        if position.get("is_retrograde", False):
            authority *= 0.7  # Retrograde penalty
        
        # 5. Out of Bounds (for Moon)
        if planet == "Moon" and position.get("is_out_of_bounds", False):
            authority *= 0.4  # Severe penalty for OOB Moon
        
        return max(min(authority, 3.0), 0.1)  # Clamp between 0.1 and 3.0
    
    def _get_dignity_multiplier(self, planet: str, sign: str) -> float:
        """Get dignity multiplier from constants (for now)."""
        dignity = ESSENTIAL_DIGNITIES.get(planet, {})
        
        if sign == dignity.get('rulership'):
            return 1.5
        elif sign == dignity.get('exaltation'):  
            return 1.25
        elif sign == dignity.get('detriment'):
            return 0.75
        elif sign == dignity.get('fall'):
            return 0.5
        else:
            return 1.0
    
    # ========================================
    # 3. TEMPORAL RELEVANCE WEIGHTING
    # ========================================
    
    def calculate_temporal_relevance(self, relationship: Dict, hour_ruler: str, 
                                   day_ruler: str, current_weekday: str) -> float:
        """
        Calculate how relevant a correspondence is to the current time context.
        This is where we handle the complex cases you mentioned.
        
        Args:
            relationship: Graph relationship data
            hour_ruler: Current hour ruling planet
            day_ruler: Current day ruling planet  
            current_weekday: Current day of week
            
        Returns:
            float: Temporal relevance score from 0.1 to 2.0
        """
        source_planet = relationship.get("source_planet")
        target_type = relationship.get("target_type") 
        target_name = relationship.get("target_name")
        rel_type = relationship.get("relationship_type")
        
        base_relevance = 1.0
        
        # CASE 1: Hour Ruler Authority
        if source_planet == hour_ruler:
            base_relevance = 1.8  # Strong hour influence
            
            # Penalty for claiming wrong weekday
            if target_type == "Weekday" and target_name != current_weekday:
                base_relevance *= 0.3  # Major penalty for temporal mismatch
                
        # CASE 2: Day Ruler Background Influence  
        elif source_planet == day_ruler:
            base_relevance = 1.2  # Moderate day influence
            
            # Bonus for correct weekday
            if target_type == "Weekday" and target_name == current_weekday:
                base_relevance *= 1.3
                
        # CASE 3: Neither ruler
        else:
            base_relevance = 0.6  # Reduced influence for non-rulers
        
        # RELATIONSHIP TYPE MODIFIERS
        if rel_type == "HOUR_RULED_BY":
            base_relevance *= 1.5  # Hour relationships get precedence
        elif rel_type == "DAY_RULED_BY":
            base_relevance *= 1.0  # Day relationships neutral
        elif rel_type == "HAS_ANALOGY_WITH":
            base_relevance *= 0.8  # General correspondences reduced
        
        return max(min(base_relevance, 2.0), 0.1)
    
    # ========================================
    # 4. ELEMENTAL DOMINANCE WEIGHTING
    # ========================================
    
    def calculate_elemental_dominance(self, target_entity: Dict, 
                                    current_elemental_weather: Dict) -> float:
        """
        Calculate how well target entity aligns with current elemental dominance.
        This addresses your building blocks weighting question.
        
        Args:
            target_entity: Entity being weighted (plant, stone, etc.)
            current_elemental_weather: Current elemental state
            
        Returns:
            float: Elemental alignment score from 0.5 to 1.5
        """
        # Get entity's elemental signatures
        entity_elements = self._get_entity_elements(target_entity)
        
        if not entity_elements:
            return 1.0  # Neutral if no elemental data
        
        alignment_score = 1.0
        
        # Check alignment with dominant elements
        for element, strength in current_elemental_weather.items():
            if element in entity_elements:
                # Entity shares dominant element - boost it
                alignment_score += strength * 0.3
        
        return max(min(alignment_score, 1.5), 0.5)
    
    def _get_entity_elements(self, entity: Dict) -> List[str]:
        """
        Extract elemental signatures from entity.
        TODO: Query this from the graph via building blocks connections.
        """
        # Placeholder - in real implementation, would trace graph to building blocks
        entity_type = entity.get("type", "")
        entity_name = entity.get("name", "")
        
        # Mock some elemental associations for testing
        if "Iron" in entity_name:
            return ["Fire", "Dry"]  # Mars/Iron = Fire + Dry
        elif "Silver" in entity_name:
            return ["Water", "Moist"]  # Moon/Silver = Water + Moist
        elif "Gold" in entity_name:
            return ["Fire", "Hot"]  # Sun/Gold = Fire + Hot
        else:
            return []
    
    def calculate_current_elemental_weather(self, planetary_positions: Dict, 
                                          hour_ruler: str, day_ruler: str) -> Dict[str, float]:
        """
        Calculate the current "elemental weather" based on planetary positions.
        This determines which elements are strongest right now.
        
        Returns:
            Dict mapping element names to strength scores (0.0 to 1.0)
        """
        elemental_weather = {
            "Fire": 0.0,
            "Earth": 0.0, 
            "Air": 0.0,
            "Water": 0.0,
            "Hot": 0.0,
            "Cold": 0.0,
            "Dry": 0.0,
            "Moist": 0.0
        }
        
        # Simple approach: rulers contribute to elemental weather
        ruler_elements = {
            "Sun": {"Fire": 0.8, "Hot": 0.9, "Dry": 0.6},
            "Moon": {"Water": 0.8, "Cold": 0.6, "Moist": 0.9},
            "Mars": {"Fire": 0.9, "Hot": 0.8, "Dry": 0.7},
            "Venus": {"Earth": 0.7, "Moist": 0.8},
            "Mercury": {"Air": 0.8, "Cold": 0.6, "Dry": 0.6},
            "Jupiter": {"Air": 0.7, "Hot": 0.7, "Moist": 0.6},
            "Saturn": {"Earth": 0.9, "Cold": 0.9, "Dry": 0.8}
        }
        
        # Hour ruler gets stronger influence
        if hour_ruler in ruler_elements:
            for element, strength in ruler_elements[hour_ruler].items():
                elemental_weather[element] += strength * 1.0
        
        # Day ruler gets moderate influence  
        if day_ruler in ruler_elements and day_ruler != hour_ruler:
            for element, strength in ruler_elements[day_ruler].items():
                elemental_weather[element] += strength * 0.6
        
        # Normalize to 0-1 range
        max_val = max(elemental_weather.values()) if elemental_weather.values() else 1.0
        if max_val > 0:
            for element in elemental_weather:
                elemental_weather[element] /= max_val
        
        return elemental_weather
    
    # ========================================
    # 5. MASTER WEIGHTING FUNCTION
    # ========================================
    
    def calculate_final_weight(self, relationship: Dict, context: Dict) -> Dict[str, Any]:
        """
        Master function that combines all weighting factors.
        
        Args:
            relationship: Graph relationship to weight
            context: Current astrological context
            
        Returns:
            Dict with final weight and breakdown of factors
        """
        source_planet = relationship.get("source_planet")
        target_entity = relationship.get("target_entity")
        
        # Calculate individual weight components
        graph_weight = self.calculate_graph_proximity_weight(
            source_planet, target_entity.get("name", ""), context.get("graph_data", {})
        )
        
        astro_weight = self.calculate_astrological_authority(
            source_planet, context.get("planetary_positions", {})
        )
        
        temporal_weight = self.calculate_temporal_relevance(
            relationship, 
            context.get("hour_ruler"),
            context.get("day_ruler"), 
            context.get("current_weekday")
        )
        
        # Calculate elemental weather first
        elemental_weather = self.calculate_current_elemental_weather(
            context.get("planetary_positions", {}),
            context.get("hour_ruler"),
            context.get("day_ruler")
        )
        
        elemental_weight = self.calculate_elemental_dominance(
            target_entity, elemental_weather
        )
        
        # Combine with configured weights
        final_weight = (
            graph_weight * self.weight_factors['graph_proximity'] +
            astro_weight * self.weight_factors['astrological_authority'] + 
            temporal_weight * self.weight_factors['temporal_relevance'] +
            elemental_weight * self.weight_factors['elemental_dominance']
        )
        
        return {
            "final_weight": round(final_weight, 3),
            "breakdown": {
                "graph_proximity": round(graph_weight, 3),
                "astrological_authority": round(astro_weight, 3), 
                "temporal_relevance": round(temporal_weight, 3),
                "elemental_dominance": round(elemental_weight, 3),
                "elemental_weather": elemental_weather
            },
            "rank": self._calculate_rank(final_weight),
            "confidence": self._calculate_confidence(final_weight, context)
        }
    
    def _calculate_rank(self, weight: float) -> str:
        """Convert numeric weight to interpretable rank."""
        if weight >= 2.0:
            return "dominant"
        elif weight >= 1.5:
            return "strong"
        elif weight >= 1.0:
            return "moderate"
        elif weight >= 0.5:
            return "weak"
        else:
            return "minimal"
    
    def _calculate_confidence(self, weight: float, context: Dict) -> float:
        """Calculate confidence in the weight calculation."""
        # Higher confidence when we have complete data
        data_completeness = 1.0
        
        if not context.get("planetary_positions"):
            data_completeness *= 0.5
        if not context.get("hour_ruler"):
            data_completeness *= 0.8
        if not context.get("graph_data"):
            data_completeness *= 0.7
        
        # Weight stability also affects confidence
        weight_stability = min(weight / 2.0, 1.0)
        
        return round(data_completeness * weight_stability, 3)


# ========================================
# TESTING AND RESEARCH FUNCTIONS
# ========================================

def test_complex_scenarios():
    """
    Test the complex scenarios you mentioned to research the weighting strategy.
    """
    engine = GraphWeightingEngine()
    
    # Test Case 1: Saturday Mars Hour (temporal conflict)
    print("=" * 60)
    print("TEST CASE 1: Saturday Mars Hour (Temporal Conflict)")
    print("=" * 60)
    
    context_saturday_mars = {
        "hour_ruler": "Mars",
        "day_ruler": "Saturn", 
        "current_weekday": "Saturday",
        "planetary_positions": {
            "Mars": {"sign": "Aries", "altitude": 45, "is_combust": False},
            "Saturn": {"sign": "Capricorn", "altitude": 60, "is_combust": False}
        }
    }
    
    # Test Mars → Sachiel (hour angel)
    mars_sachiel = {
        "source_planet": "Mars",
        "target_entity": {"name": "Sachiel", "type": "Angel"},
        "relationship_type": "HOUR_RULED_BY"
    }
    
    result1 = engine.calculate_final_weight(mars_sachiel, context_saturday_mars)
    print(f"Mars → Sachiel (hour angel): {result1['final_weight']} ({result1['rank']})")
    print(f"  Breakdown: {result1['breakdown']}")
    
    # Test Mars → Tuesday (wrong day)
    mars_tuesday = {
        "source_planet": "Mars", 
        "target_entity": {"name": "Tuesday", "type": "Weekday"},
        "relationship_type": "DAY_RULED_BY"
    }
    
    result2 = engine.calculate_final_weight(mars_tuesday, context_saturday_mars)
    print(f"Mars → Tuesday (wrong day): {result2['final_weight']} ({result2['rank']})")
    print(f"  Breakdown: {result2['breakdown']}")
    
    # Test Saturn → Saturday (correct day, background)
    saturn_saturday = {
        "source_planet": "Saturn",
        "target_entity": {"name": "Saturday", "type": "Weekday"}, 
        "relationship_type": "DAY_RULED_BY"
    }
    
    result3 = engine.calculate_final_weight(saturn_saturday, context_saturday_mars)
    print(f"Saturn → Saturday (day ruler): {result3['final_weight']} ({result3['rank']})")
    print(f"  Breakdown: {result3['breakdown']}")
    
    # Test Case 2: Moon OOB Hour (dignity demotion)
    print("\n" + "=" * 60)
    print("TEST CASE 2: Moon Out of Bounds Hour (Dignity Demotion)")
    print("=" * 60)
    
    context_moon_oob = {
        "hour_ruler": "Moon",
        "day_ruler": "Moon",
        "current_weekday": "Monday", 
        "planetary_positions": {
            "Moon": {"sign": "Cancer", "altitude": 30, "is_out_of_bounds": True}
        }
    }
    
    moon_gabriel = {
        "source_planet": "Moon",
        "target_entity": {"name": "Gabriel", "type": "Angel"},
        "relationship_type": "HOUR_RULED_BY"
    }
    
    result4 = engine.calculate_final_weight(moon_gabriel, context_moon_oob)
    print(f"Moon OOB → Gabriel: {result4['final_weight']} ({result4['rank']})")
    print(f"  Breakdown: {result4['breakdown']}")
    
    print(f"\nElemental Weather: {result4['breakdown']['elemental_weather']}")


if __name__ == "__main__":
    test_complex_scenarios()