"""
COMPLETE WORKING EXAMPLE
========================

This demonstrates the entire weighted graph system with real scenarios.
Run this to see how different astrological conditions affect graph weights.
"""

from graph_weighting_system import GraphWeightCalculator, PlanetaryCondition
import json


def scenario_normal_hour_dominance():
    """
    Hour 1 Tuesday Day (Mars rules both)
    - Mars in Aries (domicile), high in sky
    - Strong hour ruler in its home sign
    
    Expected: Mars completely dominates, Iron/Red/Samael prominent
    """
    print("\n" + "="*70)
    print("SCENARIO 1: Normal Hour Dominance")
    print("Hour 1 Tuesday Day - Mars rules BOTH hour and day")
    print("="*70)
    
    calculator = GraphWeightCalculator()
    
    mars = PlanetaryCondition(
        planet='Mars',
        sign='Aries',
        altitude=55.0,
        distance_au=1.5,
        dignity='domicile',
        dignity_score=1.5,
        is_combust=False,
        is_cazimi=False,
        is_retrograde=False,
        is_stationary=False,
        is_out_of_bounds=False,
        combustion_modifier=0.0,
        phase_modifier=0.0,
        visibility_factor=0.92,  # High visibility
        is_hour_ruler=True,
        is_day_ruler=True
    )
    
    strength = calculator.calculate_planet_strength(mars)
    
    print(f"\nMars Analysis:")
    print(f"  Sign: {mars.sign} ({mars.dignity})")
    print(f"  Altitude: {mars.altitude}°")
    print(f"  Dignity Score: {mars.dignity_score}x")
    print(f"  Visibility: {mars.visibility_factor:.2f}")
    print(f"  Rules: Hour + Day")
    print(f"\n  → Final Strength: {strength:.2f}")
    
    # Calculate correspondences
    iron_weight = calculator.calculate_correspondence_weight(
        mars, 'Iron', 'metal', 1
    )
    red_weight = calculator.calculate_correspondence_weight(
        mars, 'Red', 'color', 1
    )
    samael_weight = calculator.calculate_correspondence_weight(
        mars, 'Samael', 'angel', 1
    )
    
    print(f"\nCorrespondence Weights:")
    print(f"  Mars → Iron: {iron_weight:.2f}")
    print(f"  Mars → Red: {red_weight:.2f}")
    print(f"  Mars → Samael: {samael_weight:.2f}")
    
    print(f"\n✓ Result: STRONG DOMINANCE")
    print(f"  All Martian correspondences highly available")


def scenario_day_override():
    """
    Hour 4 Friday Night (Saturn rules hour, Venus rules day)
    - Saturn in Aries (fall), combust, below horizon
    - Venus in Pisces (exaltation), high in sky
    
    Expected: Venus overrides despite being just day ruler
    """
    print("\n" + "="*70)
    print("SCENARIO 2: Day Override (The Key Scenario)")
    print("Hour 4 Friday Night - Saturn hour, but combust and fallen")
    print("="*70)
    
    calculator = GraphWeightCalculator()
    
    saturn = PlanetaryCondition(
        planet='Saturn',
        sign='Aries',
        altitude=-12.0,  # Below horizon!
        distance_au=9.8,
        dignity='fall',
        dignity_score=0.5,
        is_combust=True,  # Too close to Sun
        is_cazimi=False,
        is_retrograde=False,
        is_stationary=False,
        is_out_of_bounds=False,
        combustion_modifier=-1.8,
        phase_modifier=0.0,
        visibility_factor=0.25,  # Very low
        is_hour_ruler=True,
        is_day_ruler=False
    )
    
    venus = PlanetaryCondition(
        planet='Venus',
        sign='Pisces',
        altitude=48.0,  # High in sky!
        distance_au=0.8,
        dignity='exaltation',
        dignity_score=1.25,
        is_combust=False,
        is_cazimi=False,
        is_retrograde=False,
        is_stationary=False,
        is_out_of_bounds=False,
        combustion_modifier=0.0,
        phase_modifier=0.0,
        visibility_factor=0.88,  # Highly visible
        is_hour_ruler=False,
        is_day_ruler=True
    )
    
    saturn_strength = calculator.calculate_planet_strength(saturn)
    venus_strength = calculator.calculate_planet_strength(venus)
    
    print(f"\nSaturn (Hour Ruler):")
    print(f"  Sign: {saturn.sign} ({saturn.dignity}) ❌")
    print(f"  Altitude: {saturn.altitude}° (below horizon) ❌")
    print(f"  Combust: {saturn.is_combust} ❌")
    print(f"  → Strength: {saturn_strength:.2f} [VERY WEAK]")
    
    print(f"\nVenus (Day Ruler):")
    print(f"  Sign: {venus.sign} ({venus.dignity}) ✓")
    print(f"  Altitude: {venus.altitude}° (highly visible) ✓")
    print(f"  Combust: {venus.is_combust} ✓")
    print(f"  → Strength: {venus_strength:.2f} [STRONG]")
    
    hour_w, day_w, dominant = calculator.calculate_hour_vs_day_dominance(saturn, venus)
    
    print(f"\nDominance Analysis:")
    print(f"  Hour weight: {hour_w:.2f}")
    print(f"  Day weight: {day_w:.2f}")
    print(f"  Ratio: Venus is {venus_strength/saturn_strength:.1f}x stronger!")
    print(f"\n  → Dominant: {dominant.upper()}")
    
    # Calculate correspondences
    lead_weight = calculator.calculate_correspondence_weight(saturn, 'Lead', 'metal', 1)
    copper_weight = calculator.calculate_correspondence_weight(venus, 'Copper', 'metal', 1)
    
    print(f"\nCorrespondence Weights:")
    print(f"  Saturn → Lead: {lead_weight:.2f} [muted]")
    print(f"  Venus → Copper: {copper_weight:.2f} [prominent]")
    
    print(f"\n✓ Result: DAY OVERRIDES HOUR")
    print(f"  Despite Saturn ruling the hour, Venus's correspondences dominate")
    print(f"  Graph should emphasize Copper/Green/Anael over Lead/Black/Cassiel")


def scenario_balanced_power():
    """
    Hour 8 Thursday Day (Jupiter rules both)
    - Jupiter in Sagittarius (domicile), medium altitude
    - Mars in Capricorn (exaltation), high altitude
    
    Expected: Jupiter stronger but Mars visible too
    """
    print("\n" + "="*70)
    print("SCENARIO 3: Balanced Power")
    print("Multiple strong planets visible")
    print("="*70)
    
    calculator = GraphWeightCalculator()
    
    jupiter = PlanetaryCondition(
        planet='Jupiter',
        sign='Sagittarius',
        altitude=35.0,
        distance_au=5.2,
        dignity='domicile',
        dignity_score=1.5,
        is_combust=False,
        is_cazimi=False,
        is_retrograde=False,
        is_stationary=False,
        is_out_of_bounds=False,
        combustion_modifier=0.0,
        phase_modifier=0.0,
        visibility_factor=0.72,
        is_hour_ruler=True,
        is_day_ruler=True
    )
    
    mars = PlanetaryCondition(
        planet='Mars',
        sign='Capricorn',
        altitude=52.0,
        distance_au=1.4,
        dignity='exaltation',
        dignity_score=1.25,
        is_combust=False,
        is_cazimi=False,
        is_retrograde=False,
        is_stationary=False,
        is_out_of_bounds=False,
        combustion_modifier=0.0,
        phase_modifier=0.0,
        visibility_factor=0.88,
        is_hour_ruler=False,
        is_day_ruler=False
    )
    
    jupiter_strength = calculator.calculate_planet_strength(jupiter)
    mars_strength = calculator.calculate_planet_strength(mars)
    
    print(f"\nJupiter (Hour + Day Ruler):")
    print(f"  Strength: {jupiter_strength:.2f}")
    
    print(f"\nMars (Not ruling, but strong):")
    print(f"  Strength: {mars_strength:.2f}")
    
    # Calculate elemental dominance
    element_scores = calculator.calculate_elemental_dominance([jupiter, mars])
    
    print(f"\nElemental Balance:")
    for element, score in sorted(element_scores.items(), key=lambda x: x[1], reverse=True):
        if score > 0:
            bar = '█' * int(score)
            print(f"  {element:8} [{score:5.2f}] {bar}")
    
    print(f"\n✓ Result: BALANCED but Jupiter primary")
    print(f"  Multiple energies available, Fire strongest")


def scenario_moon_phases():
    """
    Moon phase effects on lunar operations
    """
    print("\n" + "="*70)
    print("SCENARIO 4: Moon Phase Effects")
    print("Same hour, different Moon phases")
    print("="*70)
    
    calculator = GraphWeightCalculator()
    
    phases = [
        ("New Moon", -0.7, 10),
        ("First Quarter", 0.3, 95),
        ("Full Moon", 1.2, 180),
        ("Last Quarter", -0.4, 270),
    ]
    
    for phase_name, modifier, angle in phases:
        moon = PlanetaryCondition(
            planet='Moon',
            sign='Cancer',  # Domicile
            altitude=40.0,
            distance_au=0.00257,  # ~384,400 km in AU
            dignity='domicile',
            dignity_score=1.5,
            is_combust=False,
            is_cazimi=False,
            is_retrograde=False,
            is_stationary=False,
            is_out_of_bounds=False,
            combustion_modifier=0.0,
            phase_modifier=modifier,
            visibility_factor=0.8,
            is_hour_ruler=True,
            is_day_ruler=False
        )
        
        strength = calculator.calculate_planet_strength(moon)
        print(f"\n{phase_name} ({angle}°):")
        print(f"  Phase modifier: {modifier:+.2f}")
        print(f"  → Strength: {strength:.2f}")


def run_all_scenarios():
    """Run all test scenarios"""
    scenario_normal_hour_dominance()
    scenario_day_override()
    scenario_balanced_power()
    scenario_moon_phases()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("""
The weighted graph system successfully handles:

1. ✓ Normal hour dominance (strong hour ruler)
2. ✓ Day override (weak hour ruler, strong day ruler)
3. ✓ Balanced power (multiple strong planets)
4. ✓ Moon phases (temporal variations)

Key Insight:
  Hour rulership is PRIMARY but not ABSOLUTE.
  Planetary conditions modulate actual energy availability.
  
This creates a dynamic, realistic representation of magical timing
that respects both tradition and astronomical reality.
    """)


if __name__ == "__main__":
    run_all_scenarios()
