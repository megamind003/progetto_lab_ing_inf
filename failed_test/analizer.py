# analyzer.py
import os
import subprocess
import yaml
from docker import APIClient
from diagrams import Diagram, Node, Edge
from diagrams.custom import Custom

class DockerAnalyzer:
    def __init__(self, project_root):
        self.root = project_root
        self.services = {}
        self.networks = {}

    def find_docker_files(self):
        docker_files = []
        compose_files = []
        
        for root, dirs, files in os.walk(self.root):
            for file in files:
                if file == "Dockerfile":
                    docker_files.append(os.path.join(root, file))
                elif file in ["docker-compose.yml", "docker-compose.yaml"]:
                    compose_files.append(os.path.join(root, file))
        
        return docker_files, compose_files

    def parse_dockerfile(self, path):
        data = {'exposed_ports': [], 'healthcheck': None}
        with open(path) as f:
            for line in f:
                if line.startswith('EXPOSE'):
                    ports = line.strip().split()[1:]
                    data['exposed_ports'].extend([p.split('/')[0] for p in ports])
                elif line.startswith('HEALTHCHECK'):
                    data['healthcheck'] = line.strip()
        return data

    def parse_compose_file(self, path):
        with open(path) as f:
            compose = yaml.safe_load(f)
            services = compose.get('services', {})
            networks = compose.get('networks', {})
            
            for name, config in services.items():
                self.services[name] = {
                    'build': config.get('build', None),
                    'ports': config.get('ports', []),
                    'depends_on': config.get('depends_on', []),
                    'healthcheck': config.get('healthcheck', None),
                    'networks': config.get('networks', [])
                }

            self.networks.update(networks)

    def get_runtime_info(self):
        docker_client = APIClient(base_url='unix://var/run/docker.sock')
        containers = docker_client.containers()
        
        for container in containers:
            inspect = docker_client.inspect_container(container['Id'])
            service_name = inspect['Config']['Labels'].get('com.docker.compose.service')
            
            if service_name and service_name in self.services:
                self.services[service_name].update({
                    'status': inspect['State']['Status'],
                    'ip': inspect['NetworkSettings']['IPAddress'],
                    'ports': list(inspect['NetworkSettings']['Ports'].keys())
                })

                
    def generate_diagram(self, output_file="docker_architecture"):
        with Diagram(output_file, show=False, direction="LR"):
            nodes = {}
            for service, config in self.services.items():
                icon = "./docker.png"  # Path to docker icon
                nodes[service] = Custom(service, icon)
                
                if config.get('ports'):
                    ports = "\n".join(config['ports'])
                    nodes[service].label += f"\nPorts: {ports}"
                
                if config.get('healthcheck'):
                    nodes[service].label += "\n[Healthcheck]"

            for service, config in self.services.items():
                for dep in config['depends_on']:
                    nodes[service] >> Edge(color="black") << nodes[dep]

                for network in config['networks']:
                    net_node = Node(label=network, shape="ellipse")
                    nodes[service] - Edge(color="blue") - net_node

if __name__ == "__main__":
    #project_root = input("Inserisci il percorso del progetto: ")
    project_root = "/home/boss/Documents/progetto_lab_ing_inf/failed_test/dockerfiles/"
    analyzer = DockerAnalyzer(project_root)
    
    docker_files, compose_files = analyzer.find_docker_files()
    print(f"Trovati {len(docker_files)} Dockerfile e {len(compose_files)} Compose file")
    
    for df in docker_files:
        print(f"Analizzando Dockerfile: {df}")
        print(analyzer.parse_dockerfile(df))
    
    for cf in compose_files:
        print(f"Analizzando Compose file: {cf}")
        analyzer.parse_compose_file(cf)
    
    analyzer.get_runtime_info()
    analyzer.generate_diagram()