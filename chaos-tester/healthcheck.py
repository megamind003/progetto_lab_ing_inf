# verifica stato servizi,




import requests
import os
import docker

client = docker.from_env()

def check_service(service_name):
    try:
        container = client.containers.get(service_name)
        # Verifica healthcheck Docker
        health = container.attrs['State'].get('Health', {}).get('Status', 'no healthcheck')
        
        # Verifica personalizzata (es. HTTP)
        if service_name == "web":
            response = requests.get("http://localhost:80/health", timeout=5)
            return response.status_code == 200
        elif service_name == "db":
            # Usa un client PostgreSQL per verificare la connessione
            import psycopg2
            conn = psycopg2.connect(host="localhost", user="user", password="pass", dbname="db")
            conn.close()
            return True
        return health == "healthy"
    except Exception as e:
        return False

# Esempio di utilizzo
if __name__ == "__main__":
    services = os.popen("docker-compose config --services").read().splitlines()
    for service in services:
        status = "OK" if check_service(service) else "FAIL"
        print(f"{service}: {status}")