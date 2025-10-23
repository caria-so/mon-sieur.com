# app/routes/chart.py
from flask import Blueprint, jsonify, request, current_app, render_template
from app.routes.utils.chart_calculator import ChartCalculator
from app.routes.ephemeris import get_ephemeris_data

chart_routes = Blueprint('chart_routes', __name__)
calculator = ChartCalculator()

@chart_routes.route('/api/chart-svg-test', methods=['POST'])
def generate_chart_svg_test():
    """Simple test endpoint"""
    return '<svg>test</svg>', 200, {'Content-Type': 'image/svg+xml'}

@chart_routes.route('/api/chart-svg', methods=['POST'])
def generate_chart_svg():
    """Generate SVG chart using existing ephemeris data"""
    try:
        # Get data from the request
        data = request.get_json()
        print(f"DEBUG: Received data: {type(data)}")
        
        # If we receive direct ephemeris data, use it
        if data and 'ephemeris' in data:
            ephemeris_data = data
            print("DEBUG: Using direct ephemeris data")
        else:
            # Call ephemeris endpoint with the data from the request
            lat = data.get('latitude')
            lon = data.get('longitude')
            print(f"DEBUG: lat={lat}, lon={lon}")
            if lat is None or lon is None:
                return jsonify({"error": "Missing latitude or longitude"}), 400

            # Call ephemeris calculator directly instead of using the endpoint
            from app.routes.utils.ephemeris_calculator import EphemerisCalculator
            calculator_ephemeris = EphemerisCalculator(latitude=lat, longitude=lon)
            ephemeris_dataset = calculator_ephemeris.generate_ephemeris_dataset()
            ephemeris_data = {
                "ephemeris": ephemeris_dataset,
                "message": "Ephemeris data generated successfully"
            }
            print("DEBUG: Generated ephemeris data")
            
        # Generate SVG using the chart calculator
        print("DEBUG: About to generate SVG")
        svg = calculator.generate_chart_svg(ephemeris_data)
        print("DEBUG: SVG generated successfully")
        
        return svg, 200, {'Content-Type': 'image/svg+xml'}
        
    except Exception as e:
        current_app.logger.error(f"Error generating chart: {str(e)}")
        return jsonify({"error": str(e)}), 500
      
      
      
@chart_routes.route('/chart')
def show_chart():
    return render_template('chart.html')