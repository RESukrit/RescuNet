import os
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# In-memory triage database for fast hackathon processing
sos_signals = []


def calculate_priority(condition: str, battery: int) -> float:
    """Calculates emergency priority score based on medical severity and battery status."""
    severity_weights = {
        "Trapped under debris": 50.0,
        "Medical Emergency": 40.0,
        "Cut off by floodwater": 25.0
    }
    base_score = severity_weights.get(condition, 10.0)

    # Low battery increases priority score (urgency multiplier)
    battery_score = (100 - max(0, min(100, battery))) * 0.3
    return round(base_score + battery_score, 2)


@app.route('/')
def victim_view():
    return render_template('victim.html')


@app.route('/dashboard')
def dashboard_view():
    return render_template('dashboard.html')


@app.route('/api/hazards', methods=['GET'])
def get_hazards():
    hazard_path = os.path.join(app.static_folder, 'hazards.json')
    if os.path.exists(hazard_path):
        with open(hazard_path, 'r') as f:
            return jsonify(json.load(f))
    return jsonify({"type": "FeatureCollection", "features": []})


@app.route('/api/sos', methods=['GET', 'POST'])
def handle_sos():
    if request.method == 'POST':
        data = request.json or {}

        condition = data.get('condition', 'Unknown')
        battery = int(data.get('battery', 100))

        payload = {
            "id": len(sos_signals) + 1,
            "name": data.get('name', 'Anonymous'),
            "condition": condition,
            "battery": battery,
            "lat": float(data.get('lat', 10.053)),
            "lng": float(data.get('lng', 76.627)),
            "priority": calculate_priority(condition, battery),
            "time": data.get('time', 'N/A')
        }

        sos_signals.append(payload)
        # Sort queue automatically: Highest priority first
        sos_signals.sort(key=lambda x: x['priority'], reverse=True)
        return jsonify({"status": "broadcast_success", "data": payload})

    return jsonify(sos_signals)


if __name__ == '__main__':
    # Binds to 0.0.0.0 to allow access from local mobile devices via Ngrok/Wi-Fi
    app.run(host='0.0.0.0', port=5000, debug=True)