from flask import Flask
import redis
import time

app = Flask(__name__)

# Configura Redis con tentativi di connessione
def get_redis_connection():
    retries = 5
    while retries > 0:
        try:
            return redis.Redis(host='redis', port=6379, db=0)
        except redis.exceptions.ConnectionError:
            retries -= 1
            time.sleep(2)
    raise Exception("Impossibile connettersi a Redis")

@app.route('/')
def home():
    return "Chaos Testing Environment"

@app.route('/health')
def health():
    try:
        r = get_redis_connection()
        if r.ping():
            return 'OK', 200
    except:
        pass
    return 'Unhealthy', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)