# docker_visualizer.py
import os
import docker
import yaml
from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.container import Docker
from diagrams.custom import Custom
from diagrams.generic.database import SQL
from diagrams.generic.network import Firewall
from diagrams.programming.framework import FastAPI
from diagrams.onprem.client import Client
import argparse

class DockerVisualizer:
    def __init__(self, project_root):
        self.project_root = os.path.abspath(project_root)
        self.client = docker.from_env()
        self.services = {}
        self.networks = {}
        self.volumes = {}

    def analyze(self):
        self._find_compose_file()
        self._parse_compose()
        self._inspect_containers()
        self._build_connections()

    def _find_compose_file(self):
        for f in ['docker-compose.yml', 'docker-compose.yaml']:
            path = os.path.join(self.project_root, f)
            if os.path.exists(path):
                self.compose_path = path
                return
        raise FileNotFoundError("Nessun file docker-compose trovato")

    def _parse_compose(self):
        with open(self.compose_path) as f:
            compose = yaml.safe_load(f)
            for name, config in compose.get('services', {}).items():
                self.services[name] = {
                    'image': config.get('image'),
                    'ports': config.get('ports', []),
                    'networks': config.get('networks', []),
                    'depends_on': config.get('depends_on', []),
                    'volumes': config.get('volumes', []),
                    'status': 'not_running',
                    'health': 'N/A',
                    'ip': 'N/A',
                    'type': 'generic'
                }
            self.networks = compose.get('networks', {})
            self.volumes = compose.get('volumes', {})

    def _inspect_containers(self):
        for container in self.client.containers.list(all=True):
            inspect = container.attrs
            service_name = self._extract_service_name(inspect['Name'])
            
            service_info = {
                'status': inspect['State']['Status'],
                'health': inspect['State'].get('Health', {}).get('Status', 'N/A'),
                'ip': inspect['NetworkSettings']['IPAddress'],
                'ports': self._parse_ports(inspect),
                'networks': list(inspect['NetworkSettings']['Networks'].keys()),
                'volumes': [mount['Source'] for mount in inspect['Mounts']],
                'image': inspect['Config']['Image'],
                'type': self._determine_service_type(inspect)
            }
            
            if service_name in self.services:
                self.services[service_name].update(service_info)
            else:
                self.services[service_name] = service_info
                self.services[service_name]['status'] = inspect['State']['Status']

    def _extract_service_name(self, container_name):
        parts = container_name.lstrip('/').split('_')
        return parts[1] if len(parts) > 1 else parts[0]

    def _parse_ports(self, inspect_data):
        ports = []
        for port, mappings in inspect_data['NetworkSettings']['Ports'].items():
            if mappings:
                for mapping in mappings:
                    ports.append(f"{mapping['HostPort']}->{port}")
        return ports

    def _determine_service_type(self, inspect_data):
        image = inspect_data['Config']['Image'].lower()
        if 'postgres' in image:
            return 'database'
        if 'fastapi' in image or 'flask' in image:
            return 'api'
        if 'redis' in image or 'memcached' in image:
            return 'cache'
        if 'nginx' in image or 'apache' in image:
            return 'web_server'
        return 'generic'

    def _build_connections(self):
        for service, config in self.services.items():
            config['connections'] = {
                'services': config.get('depends_on', []),
                'networks': config.get('networks', []),
                'volumes': config.get('volumes', [])
            }

    def generate_diagram(self, output_format='png'):
        graph_attr = {
            "bgcolor": "white",
            "fontcolor": "#2D3436",
            "fontname": "Helvetica",
            "fontsize": "10",
            "layout": "dot"
        }

        with Diagram("Docker Architecture", show=False, direction="TB", 
                    outformat=output_format, filename="docker_arch", graph_attr=graph_attr):
            
            internet = Custom("Internet", os.path.join(self.project_root, "resources/internet.png"))
            components = {}
            network_nodes = {}
            volume_nodes = {}

            # Create network nodes
            for net_name in self.networks:
                network_nodes[net_name] = Firewall(net_name)

            # Create volume nodes
            for vol_name in self.volumes:
                volume_nodes[vol_name] = Custom(vol_name, "./resources/volume.png")

            # Create service nodes
            for service, config in self.services.items():
                node_color = "#4CAF50" if config.get('status', 'not_running') == 'running' else "#F44336"
                
                # Determine node type
                if config['type'] == 'database':
                    node = SQL(service)
                elif config['type'] == 'api':
                    node = FastAPI(service)
                elif config['type'] == 'web_server':
                    node = Client(service)
                else:
                    node = Docker(service)

                # Build label
                label = [
                    f"Service: {service}",
                    f"Status: {config.get('status', 'N/A').upper()}",
                    f"Image: {config.get('image', 'N/A')}",
                    f"Ports: {', '.join(config.get('ports', []))}"
                ]
                
                if config.get('health', 'N/A') != 'N/A':
                    label.append(f"Health: {config['health']}")
                
                node.label = "\n".join(label)
                node.fontcolor = node_color
                components[service] = node

            # Create connections
            for service, config in self.services.items():
                # Service dependencies
                for dep in config['connections']['services']:
                    if dep in components:
                        components[dep] >> Edge(color="#2196F3", label="depends_on") >> components[service]

                # Network connections
                for net in config['connections']['networks']:
                    if net in network_nodes:
                        components[service] - Edge(color="#9E9E9E", style="dotted") - network_nodes[net]

                # Volume connections
                for vol in config['connections']['volumes']:
                    if vol in volume_nodes:
                        components[service] >> Edge(color="#FF9800", style="dashed") >> volume_nodes[vol]

                # Exposed ports
                if config.get('ports'):
                    internet >> Edge(color="#F44336", style="bold") >> components[service]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Docker Architecture Visualizer')
    parser.add_argument('project_path', nargs='?', default='.', help='Project root directory')
    parser.add_argument('-f', '--format', default='png', choices=['png', 'jpeg', 'pdf', 'svg'])
    
    args = parser.parse_args()
    
    visualizer = DockerVisualizer(args.project_path)
    visualizer.analyze()
    visualizer.generate_diagram(args.format)
    print(f"Diagramma generato: docker_arch.{args.format}")