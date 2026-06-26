from flask import Flask, request, jsonify, render_template
import json

app = Flask(__name__)

gps_data = []


@app.route('/api/gps', methods=['POST'])
def receive_gps():
    global gps_data
    data = request.json
    latitude = data.get("latitude", 0.0)
    longitude = data.get("longitude", 0.0)
    gps_data.append({"latitude": latitude, "longitude": longitude})

    # 限制保存的点的数量，例如100个点
    if len(gps_data) > 100:
        gps_data.pop(0)

    return jsonify({"status": "success"}), 200


@app.route('/gps_data')
def get_gps_data():
    return jsonify(gps_data)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
