#!/usr/bin/env python3
"""
Extract all classes, instances, and object properties from ontology YAML files
and compare with the simplified _object_properties.yaml
"""

import yaml
import os
from pathlib import Path
from collections import defaultdict
import json

def load_yaml(filepath):
    """Load a YAML file safely."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def extract_classes(data, filepath):
    """Extract class definitions from ontology data."""
    classes = {}
    filename = Path(filepath).name
    
    if not data:
        return classes
    
    # Check for classes section
    if 'classes' in data:
        for class_name, class_def in data['classes'].items():
            if isinstance(class_def, dict):
                classes[class_name] = {
                    'file': filename,
                    'uri': class_def.get('uri', f"monsieur:{class_name}"),
                    'label': class_def.get('label', class_name),
                    'parent': class_def.get('rdfs:subClassOf', 'Entity'),
                    'description': class_def.get('description', '')
                }
    
    return classes

def extract_instances(data, filepath):
    """Extract instance definitions from ontology data."""
    instances = {}
    filename = Path(filepath).name
    
    if not data:
        return instances
    
    # Check for instances section
    if 'instances' in data:
        for instance_name, instance_def in data['instances'].items():
            if isinstance(instance_def, dict):
                instances[instance_name] = {
                    'file': filename,
                    'uri': instance_def.get('uri', f"monsieur:{instance_name}"),
                    'label': instance_def.get('label', instance_name),
                    'type': instance_def.get('rdf:type', 'Unknown'),
                    'properties': {}
                }
                
                # Extract all properties that look like correspondences
                for key, value in instance_def.items():
                    if key.endswith('_CORRESPONDENCE') or key in [
                        'RULES', 'RULED_BY', 'HAS_DOMICILE', 'HAS_EXALTATION',
                        'HAS_DETRIMENT', 'HAS_FALL', 'MEMBER_OF', 'HAS_MEMBER',
                        'HAS_BASIC_ELEMENT', 'HAS_BASIC_QUALITY', 'HAS_POLARITY',
                        'HAS_TEMPERAMENT', 'HAS_GENRE', 'HAS_HUMOR'
                    ]:
                        instances[instance_name]['properties'][key] = value
    
    return instances

def extract_properties_used(data, filepath):
    """Extract object properties actually used in instances."""
    properties_used = defaultdict(lambda: {'files': set(), 'with_qualifiers': 0, 'without_qualifiers': 0})
    filename = Path(filepath).name
    
    if not data or 'instances' not in data:
        return properties_used
    
    for instance_name, instance_def in data['instances'].items():
        if not isinstance(instance_def, dict):
            continue
        
        # Check for properties in owl:ObjectProperty section (new format)
        if 'owl:ObjectProperty' in instance_def:
            obj_props = instance_def['owl:ObjectProperty']
            if isinstance(obj_props, dict):
                for prop_name, prop_values in obj_props.items():
                    properties_used[prop_name]['files'].add(filename)
                    
                    # Check if property has qualifiers
                    if isinstance(prop_values, list):
                        for value in prop_values:
                            if isinstance(value, dict):
                                if 'qualifiers' in value:
                                    properties_used[prop_name]['with_qualifiers'] += 1
                                else:
                                    properties_used[prop_name]['without_qualifiers'] += 1
        
        # Also check for direct properties (should be migrated to owl:ObjectProperty)
        for prop_name, prop_value in instance_def.items():
            # Skip non-property fields
            if prop_name in ['uri', 'label', 'description', 'rdf:type', 'rdfs:subClassOf', 
                           'aliases', 'notes', 'overall_frequency', 'owl:ObjectProperty']:
                continue
            
            # Check if it looks like a property
            if (prop_name.upper() == prop_name or 
                prop_name.endswith('_CORRESPONDENCE')):
                properties_used[prop_name]['files'].add(filename)
                properties_used[prop_name]['without_qualifiers'] += 1  # Direct properties typically don't have qualifiers
    
    return properties_used

def scan_ontology_directory(ont_dir):
    """Scan all YAML files in the ontology directory."""
    all_classes = {}
    all_instances = {}
    all_properties_used = defaultdict(lambda: {'files': set(), 'with_qualifiers': 0, 'without_qualifiers': 0})
    
    # Scan main directory
    for yaml_file in Path(ont_dir).glob('*.yaml'):
        # Skip the object properties definition file itself
        if yaml_file.name == '_object_properties.yaml':
            continue
            
        data = load_yaml(yaml_file)
        
        # Extract components
        classes = extract_classes(data, yaml_file)
        instances = extract_instances(data, yaml_file)
        properties = extract_properties_used(data, yaml_file)
        
        # Merge results
        all_classes.update(classes)
        all_instances.update(instances)
        for prop, stats in properties.items():
            all_properties_used[prop]['files'].update(stats['files'])
            all_properties_used[prop]['with_qualifiers'] += stats['with_qualifiers']
            all_properties_used[prop]['without_qualifiers'] += stats['without_qualifiers']
    
    # Also scan simplified directory if it exists
    simplified_dir = Path(ont_dir) / 'simplified'
    if simplified_dir.exists():
        for yaml_file in simplified_dir.glob('*.yaml'):
            # Skip definition files
            if yaml_file.name.startswith('_'):
                continue
                
            data = load_yaml(yaml_file)
            
            # Extract components
            classes = extract_classes(data, yaml_file)
            instances = extract_instances(data, yaml_file)
            properties = extract_properties_used(data, yaml_file)
            
            # Merge results
            all_classes.update(classes)
            all_instances.update(instances)
            for prop, stats in properties.items():
                all_properties_used[prop]['files'].update(stats['files'])
                all_properties_used[prop]['with_qualifiers'] += stats['with_qualifiers']
                all_properties_used[prop]['without_qualifiers'] += stats['without_qualifiers']
    
    return all_classes, all_instances, all_properties_used

def load_property_definitions(prop_file):
    """Load the property definitions from _object_properties.yaml."""
    data = load_yaml(prop_file)
    properties = {}
    
    if data and 'objectProperties' in data:
        for prop_name, prop_def in data['objectProperties'].items():
            if isinstance(prop_def, dict):
                properties[prop_name] = {
                    'uri': prop_def.get('uri'),
                    'label': prop_def.get('label'),
                    'description': prop_def.get('description'),
                    'domain': prop_def.get('rdfs:domain'),
                    'range': prop_def.get('rdfs:range'),
                    'characteristics': prop_def.get('owl:characteristics', [])
                }
    
    return properties

def compare_properties(properties_used, properties_defined):
    """Compare used properties with defined properties."""
    used_set = set(properties_used.keys())
    defined_set = set(properties_defined.keys())
    
    comparison = {
        'used_but_not_defined': sorted(used_set - defined_set),
        'defined_but_not_used': sorted(defined_set - used_set),
        'both': sorted(used_set & defined_set),
        'usage_stats': {
            prop: {
                'files': sorted(list(stats['files'])),
                'file_count': len(stats['files']),
                'with_qualifiers': stats['with_qualifiers'],
                'without_qualifiers': stats['without_qualifiers'],
                'total_uses': stats['with_qualifiers'] + stats['without_qualifiers']
            }
            for prop, stats in properties_used.items()
        }
    }
    
    return comparison

def save_results(output_dir, classes, instances, properties_used, comparison):
    """Save all results to files."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Save classes
    classes_file = Path(output_dir) / 'extracted_classes.yaml'
    with open(classes_file, 'w', encoding='utf-8') as f:
        yaml.dump({'extracted_classes': classes}, f, default_flow_style=False, sort_keys=True)
    print(f"Saved {len(classes)} classes to {classes_file}")
    
    # Save instances
    instances_file = Path(output_dir) / 'extracted_instances.yaml'
    with open(instances_file, 'w', encoding='utf-8') as f:
        yaml.dump({'extracted_instances': instances}, f, default_flow_style=False, sort_keys=True)
    print(f"Saved {len(instances)} instances to {instances_file}")
    
    # Save properties used
    props_used_file = Path(output_dir) / 'extracted_properties_used.yaml'
    with open(props_used_file, 'w', encoding='utf-8') as f:
        yaml.dump({
            'properties_used': {
                prop: {
                    'files': sorted(list(stats['files'])),
                    'with_qualifiers': stats['with_qualifiers'],
                    'without_qualifiers': stats['without_qualifiers']
                }
                for prop, stats in properties_used.items()
            }
        }, f, default_flow_style=False, sort_keys=True)
    print(f"Saved {len(properties_used)} used properties to {props_used_file}")
    
    # Save comparison
    comparison_file = Path(output_dir) / 'property_comparison.yaml'
    with open(comparison_file, 'w', encoding='utf-8') as f:
        yaml.dump({'property_comparison': comparison}, f, default_flow_style=False)
    print(f"Saved property comparison to {comparison_file}")
    
    # Print summary
    print("\n=== SUMMARY ===")
    print(f"Total classes extracted: {len(classes)}")
    print(f"Total instances extracted: {len(instances)}")
    print(f"Total properties used: {len(properties_used)}")
    print(f"\nProperties used but not defined: {len(comparison['used_but_not_defined'])}")
    if comparison['used_but_not_defined']:
        print("  - " + "\n  - ".join(comparison['used_but_not_defined'][:10]))
        if len(comparison['used_but_not_defined']) > 10:
            print(f"  ... and {len(comparison['used_but_not_defined']) - 10} more")
    
    print(f"\nProperties defined but not used: {len(comparison['defined_but_not_used'])}")
    if comparison['defined_but_not_used']:
        print("  - " + "\n  - ".join(comparison['defined_but_not_used'][:10]))
        if len(comparison['defined_but_not_used']) > 10:
            print(f"  ... and {len(comparison['defined_but_not_used']) - 10} more")
    
    # Print qualifier usage stats
    print("\n=== QUALIFIER USAGE ===\n")
    total_with_qual = sum(s['with_qualifiers'] for s in comparison['usage_stats'].values())
    total_without_qual = sum(s['without_qualifiers'] for s in comparison['usage_stats'].values())
    print(f"Properties with qualifiers: {total_with_qual}")
    print(f"Properties without qualifiers: {total_without_qual}")
    
    if comparison['usage_stats']:
        print("\nTop used properties:")
        sorted_props = sorted(comparison['usage_stats'].items(), 
                            key=lambda x: x[1]['total_uses'], reverse=True)[:10]
        for prop, stats in sorted_props:
            print(f"  {prop}: {stats['total_uses']} uses "
                  f"({stats['with_qualifiers']} with qualifiers, "
                  f"{stats['without_qualifiers']} without)")

def main():
    # Paths
    ont_dir = Path('/Users/fede/Desktop/Hermetic Library/monsieur_neo/ontologies')
    prop_file = ont_dir / 'simplified' / '_object_properties.yaml'
    output_dir = ont_dir / 'extraction_results'
    
    print("Extracting ontology components...")
    print(f"Scanning directory: {ont_dir}")
    
    # Extract from all ontology files
    classes, instances, properties_used = scan_ontology_directory(ont_dir)
    
    # Load property definitions
    print(f"\nLoading property definitions from {prop_file}")
    properties_defined = load_property_definitions(prop_file)
    
    # Compare properties
    print("\nComparing properties...")
    comparison = compare_properties(properties_used, properties_defined)
    
    # Save results
    print("\nSaving results...")
    save_results(output_dir, classes, instances, properties_used, comparison)
    
    print("\n✓ Extraction complete!")
    print(f"Results saved to: {output_dir}")

if __name__ == '__main__':
    main()