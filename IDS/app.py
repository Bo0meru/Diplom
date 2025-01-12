# app.py
from datetime import datetime
from flask import Flask, request, jsonify
from ids_core import IDS
from alert_bot.notify import send_notification

# Инициализация Flask
app = Flask(__name__)
ids = IDS(alert_func=send_notification)

@app.route('/check_ip', methods=['GET'])
def check_ip():
    ip_address = request.args.get('ip')
    if not ip_address:
        return jsonify({"error": "IP address is required"}), 400
    result = ids.check_ip(ip_address)
    return jsonify({"ip": ip_address, "result": result}), 200

@app.route('/block_ip', methods=['POST'])
def block_ip():
    data = request.get_json()
    ip_address = data.get('ip')
    if not ip_address:
        return jsonify({"error": "IP address is required"}), 400
    ids.block_ip(ip_address)
    return jsonify({"ip": ip_address, "result": "blocked"}), 200

@app.route('/log_event', methods=['POST'])
def log_event():
    data = request.get_json()
    user = data.get('user', 'unknown')
    action = data.get('action', 'unknown')
    critical = data.get('critical', False)
    ids.log_event(user, action, critical=critical)
    return jsonify({"user": user, "action": action, "logged": True}), 200

@app.route('/generate_report', methods=['GET'])
def generate_report():
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    try:
        start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") if start_time else None
        end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S") if end_time else None
        report_path = ids.generate_report(start_time, end_time)
        if not report_path:
            return jsonify({"error": "Failed to generate report"}), 500
        return jsonify({"report_path": report_path, "result": "generated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
