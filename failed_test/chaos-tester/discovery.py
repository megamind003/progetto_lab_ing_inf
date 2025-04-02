import docker
import requests
import json

client = docker.from_env()

def get_container_info(container):
    info = {
        "id": container.id,
        "name": container.name,
        "status": container.status,
        "ports": container.attrs['NetworkSettings']['Ports'],
        "env": container.attrs['Config']['Env'],
        "endpoints": [],
        "dependencies": []
    }

    # Rileva endpoint HTTP
    if '8000/tcp' in info['ports']:
        try:
            port = info['ports']['8000/tcp'][0]['HostPort']
            response = requests.get(f"http://localhost:{port}/health", timeout=2)
            if response.status_code == 200:
                info['endpoints'].append('/health')
        except:
            pass

    # Rileva dipendenze di rete
    networks = container.attrs['NetworkSettings']['Networks']
    for network in networks.values():
        info['dependencies'] += [c.split('.')[0] for c in network['Aliases'] if c != container.name]

    return info

def main():
    containers = client.containers.list()
    report = {}
    
    for container in containers:
        report[container.name] = get_container_info(container)
    
    with open('traffic_logs/container_report.json', 'w') as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    main()