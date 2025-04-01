import requests
import os
import docker
import redis

client = docker.from_env()

def check_service(service_name):
    try:
        container = client.containers.get(f"chaos-tester_{service_name}_1")
        
        # Verifica stato Docker
        status = container.status
        health = container.attrs['State'].get('Health', {}).get('Status', 'no healthcheck')
        
        # Verifiche personalizzate
        if service_name == "web":
            try:
                response = requests.get("http://localhost:5000/health", timeout=3)
                return response.status_code == 200
            except:
                return False
        elif service_name == "redis":
            try:
                r = redis.Redis(host='redis', port=6379, db=0)
                return r.ping()
            except:
                return False
                
        return health == "healthy"
    except Exception as e:
        return False

if __name__ == "__main__":
    services = os.popen("docker-compose -p chaos-tester config --services").read().splitlines()
    for service in services:
        status = "OK" if check_service(service) else "FAIL"
        print(f"{service}: {status}")