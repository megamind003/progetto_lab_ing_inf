from flask import Flask, jsonify
import redis
import logging

app = Flask(__name__)
logging.basicConfig(filename='/var/log/web/server.log', level=logging.INFO)

@app.route('/health')
def health():
    app.logger.info('Health check requested')
    return jsonify({"status": "OK"}), 200

@app.route('/data')
def get_data():
    try:
        r = redis.Redis(host=app.config.get('REDIS_HOST', 'redis'),
                        port=app.config.get('REDIS_PORT', 6379),
                        socket_connect_timeout=2)
        return jsonify({"response": str(r.ping())}), 200
    except Exception as e:
        app.logger.error(f"Redis error: {str(e)}")
        return jsonify({"error": str(e)}), 503