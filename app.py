from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

sos_signals = []


def calculate_priority(condition: str, battery: int) -> float:
    severity_weights = {
        "Trapped under debris": 50.0,
        "Medical Emergency": 40.0,
        "Trapped in a Fire": 35.0,
        "Cut off by floodwater": 25.0,

    }
    base_score = severity_weights.get(condition, 10.0)
    battery_score = (100 - max(0, min(100, battery))) * 0.3
    return round(base_score + battery_score, 2)


@app.route('/')
def victim_view():
    return render_template('victim.html')


@app.route('/dashboard')
def dashboard_view():
    return render_template('dashboard.html')


@app.route('/api/sos', methods=['GET', 'POST'])
def handle_sos():
    if request.method == 'POST':
        data = request.json or {}
        condition = data.get('condition', 'Medical Emergency')
        battery = int(data.get('battery', 100))

        payload = {
            "id": len(sos_signals) + 1,
            "name": data.get('name', 'Anonymous Victim'),
            "condition": condition,
            "battery": battery,
            "lat": float(data.get('lat', 10.053)),
            "lng": float(data.get('lng', 76.627)),
            "priority": calculate_priority(condition, battery),
            "time": data.get('time', 'N/A')
        }

        sos_signals.append(payload)
        sos_signals.sort(key=lambda x: x['priority'], reverse=True)
        return jsonify({"status": "success", "data": payload})

    return jsonify(sos_signals)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)