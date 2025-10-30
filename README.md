# Monsieur.so

# Overview
Monsieur.so is a web application that infuses astronomy and artificial intelligence into the three pillars of traditional knowledge: Astrology, Alchemy, and Magic.

## Core Functionality
At its core, it’s an interactive knowledge graph that brings together astronomical calculations, astrological correspondences, and hermetic philosophy. Think of it as a digital implementation of traditional astrological and magical practices—reimagined through modern computational astronomy and graph database technology. 

1. Astronomical & Astrological Calculations
Real-time Planetary Positions: Calculates precise positions of all planets (including outer planets) using the Swiss Ephemeris and Skyfield libraries
Astrological Chart Generation: Creates complete natal charts with houses, aspects, and planetary positions
Planetary Hours: Calculates traditional planetary hours based on sunrise/sunset times
Moon Phases & Properties: Tracks lunar cycles, illumination, declination, and out-of-bounds status
Aspect Calculations: Determines angular relationships between planets (conjunctions, squares, trines, etc.)
Combustion & Cazimi: Identifies when planets are too close to the Sun
Geographic Integration: Uses user's location for accurate calculations

2. Knowledge Graph System
The application maintains a comprehensive Neo4j graph database containing:
Magic Hours: 168 specific hours (12 day + 12 night × 7 days) with their ruling planets and angels
Spiritual Entities: Angels, demons, and elemental beings associated with planetary hours
Colors & Metals: Traditional correspondences (e.g., Jupiter = Blue = Tin)
Chemical Substances: Metals, stones, and materials linked to planetary energies
Zodiacal Signs: Complete astrological sign system with properties
Evidence & Sources: Tracks knowledge sources (e.g., "The Key of Solomon") with confidence levels

3. Interactive Visualization
Network Graph: Visualizes relationships between hours, planets, angels, colors, and materials
Dynamic Filtering: Shows relevant entities based on current planetary hour
Astrological Chart: SVG-based natal chart with planetary positions and aspects
Heatmap Visualization: Background visualization showing planetary energies
Terminal Interface: Command-line style interaction for exploring the system

4. Historical & Traditional Knowledge
Solomonic Magic: Based on "The Key of Solomon" and other grimoires
Planetary Correspondences: Traditional associations between planets, colors, metals, angels
Aspect Data: Historical planetary aspect data (e.g., Saturn-Pluto aspects from 1939)
Hermetic Philosophy: Integration of classical hermetic principles

## Technical Architecture
### Backend (Flask)

- Ephemeris Calculator: Handles all astronomical calculations
- Chart Calculator: Generates SVG astrological charts
- Neo4j Integration: Manages the knowledge graph
- REST API: Provides data to the frontend

### Frontend (JavaScript)
- Interactive Network: Uses vis.js for graph visualization -> maybe move to d3.js
- Geolocation Service: Automatically detects user location
- Terminal Interface: Command-line style interaction
- Real-time Updates: Dynamic filtering based on current time/location

### Data Sources
- Swiss Ephemeris: High-precision astronomical calculations
- Skyfield: Python astronomy library
- Neo4j: Graph database for knowledge relationships
- YAML Ontologies: Structured knowledge definitions

## Use Cases
1. Astrological Practice: Generate accurate natal charts and analyze planetary positions
2. Magical Timing: Determine optimal times for rituals based on planetary hours
3. Knowledge Exploration: Navigate traditional correspondences and relationships
4. Educational Tool: Learn about hermetic philosophy and astrological systems
5. Research Platform: Study historical astrological data and patterns

### Key Features
- Real-time Calculations: Always shows current planetary positions and aspects
- Location-Aware: Adapts to user's geographic location for accurate timing
- Interactive Learning: Explore knowledge through visual graph navigation
- Traditional Accuracy: Based on historical grimoires and astrological texts
- Modern Interface: Combines ancient knowledge with contemporary UX

This system essentially digitizes and makes accessible the complex web of correspondences found in traditional hermetic and astrological texts, while providing accurate astronomical calculations and an intuitive interface for exploration and practical use.

# Detailed Explanation: Ephemeris Calculator & Heatmap System
## Ephemeris Calculator - The NASA Data Engine

The Ephemeris Calculator (ephemeris_calculator.py) is the astronomical computation engine that provides real-time, location-aware planetary data using NASA's JPL (Jet Propulsion Laboratory) ephemeris data.
Core Functionality:

### A. Astronomical Calculations
- Planetary Positions: Calculates precise longitude, latitude, altitude, and azimuth for all planets
- Distance Calculations: Computes actual distances from Earth in Astronomical Units (AU)
- Motion Analysis: Determines if planets are retrograde, stationary, or direct
- Sun/Moon Times: Calculates sunrise/sunset times for the observer's location
- Timezone Detection: Automatically determines timezone based on coordinates

### B. Astrological Enhancements
- Planetary Hours: Calculates traditional 12-hour day/night cycles based on sunrise/sunset
- Essential Dignities: Determines if planets are in rulership, exaltation, detriment, or fall
- Combustion & Cazimi: Identifies when planets are too close to the Sun (≤8.5° = combust, ≤0.283° = cazimi)
- Moon Phases: Calculates lunar illumination, phase angle, and declination
- Aspect Calculations: Determines angular relationships between planets

### C. Data Sources
- Swiss Ephemeris: High-precision astronomical calculations
- Skyfield: Python astronomy library for planetary positions
- JPL DE440: NASA's planetary ephemeris data (de440s.bsp file)
- TimezoneFinder: Geographic timezone detection


'''
# Main data generation
generate_ephemeris_dataset()  # Returns comprehensive planetary data

# Core calculations
calculate_planetary_positions()  # Longitude, altitude, azimuth
calculate_planetary_distances()  # AU distances from Earth
calculate_combustion_and_cazimi()  # Sun proximity analysis
calculate_moon_properties()  # Lunar phase and illumination
calculate_aspects()  # Planetary angular relationships

'''


## Heatmap Calculator - Visualizing Planetary Influence
The Heatmap Calculator (heatmap_calculator.py) transforms raw astronomical data into visual representations of planetary influence that are location-aware and dynamically calculated.

### Core Concept:
The heatmap system creates radial gradients around each planet's position in the sky, where:

- Size = Distance from Earth (closer = larger)
- Intensity = Multiple astrological factors
- Color = Traditional planetary correspondences
- Position = Actual sky position (altitude/azimuth)

#### A. Intensity Calculation System
The system calculates planetary "influence intensity" using multiple weighted factors:

1. Proximity Factor (15% weight)
intensity

2. Visibility Factor (20% weight)

3. Ruling Bonuses (40% weight)
- Hour Ruler: +9.0 intensity (current planetary hour)
- Day Ruler: +6.5 intensity (current day of week)
- Both: +1.5 additional bonus

4. Essential Dignity (20% weight)
- Rulership: 1.5x multiplier
- Exaltation: 1.25x multiplier
- Detriment: 0.75x multiplier
- Fall: 0.5x multiplier

5. Special Conditions
- Cazimi: +0.5 bonus (planet in Sun's heart)
- Combustion: -1.8 penalty (planet too close to Sun)
- Moon Phase: Variable modifier based on lunar cycle

### B. Visual Rendering System
#### Gradient Generation:
Each planet gets a 3-layer radial gradient:

'''
gradient_data = {
    "core": {
        "radius": core_radius,           # Bright center
        "color": "#F2FF00"              # Planet's traditional color
    },
    "inner": {
        "radius": inner_radius,          # Medium intensity
        "color": "#FFF7B0"              # Lighter shade
    },
    "outer": {
        "radius": outer_radius,          # Faint edge
        "color": "#FFFFD0"              # Very light/transparent
    }
}
'''

Size Normalization:
- Distance-based: Closer planets appear larger
- Physical size: Actual planetary diameters (Jupiter = 139,820 km, Mercury = 4,879 km)
- Logarithmic scaling: Prevents extreme size differences

### Color System:
Based on traditional planetary correspondences:

Sun: Yellow (#F2FF00)
Moon: Silver (#D7DEDC)
Mercury: Purple (#7C00FE)
Venus: Green (#00FF00)
Mars: Red (#FF0000)
Jupiter: Blue (#0000FF)
Saturn: Black (#000000)
C. Location-Aware Rendering
The frontend (heatmap.js) renders the heatmap as a canvas overlay showing:

1. Observer Perspective
- Observer marker: Central point representing the user
- Horizon line: Curved line showing the horizon
- Sky dome: 360° representation of the sky

2. Planet Positioning
- Azimuth mapping: 0-360° → Canvas X coordinates
- Altitude mapping: -90° to +90° → Canvas Y coordinates
- Distance scaling: AU distances affect visual size
- Overlap resolution: Prevents planets from overlapping visually

3. Dynamic Effects
- Ruling planet emphasis: Hour/day rulers get larger, brighter gradients
- Combustion warnings: Console warnings for combust planets
- Moon-specific alerts: Special warnings for lunar conditions

### D. Real-Time Updates
The system continuously updates based on:
- Current time: Planetary positions change constantly
- User location: Different coordinates = different sky view
- Planetary hours: Changes every ~2 hours
- Moon phases: Changes throughout the month

### E. Practical Applications
1. Astrological Timing
- Optimal moments: When ruling planets are strong
- Avoid periods: When planets are combust or weak
- Lunar guidance: Moon phase affects decision timing

2. Visual Learning
- Sky awareness: See where planets actually are
- Influence visualization: Understand planetary strength
- Traditional correspondences: Learn color/planet associations

3. Magical Practice
- Ritual timing: Choose optimal planetary hours
- Energy work: Focus on strong planetary influences
- Meditation: Align with current cosmic energies

### Integration & Data Flow

User Location → Ephemeris Calculator → Heatmap Calculator → Canvas Rendering
     ↓                    ↓                    ↓              ↓
Latitude/Longitude → Planetary Data → Intensity Scores → Visual Gradients

The system creates a living, breathing representation of the cosmos that updates in real-time, showing not just where planets are, but how their astrological influence manifests based on traditional hermetic principles and modern astronomical accuracy.
This is essentially a digital implementation of ancient sky-watching practices, enhanced with NASA-level precision and modern visualization techniques.




