import requests
import time
import logging

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/client/client.log'),
        logging.StreamHandler()
    ]
)

def simulate_traffic():
    while True:
        try:
            start_time = time.time()
            
            # Effettua richiesta al web server
            response = requests.get(
                "http://web:8000/data",
                timeout=2
            )
            
            duration = (time.time() - start_time) * 1000  # ms
            
            logging.info(
                f"Response: {response.status_code} | "
                f"Content: {response.text.strip()} | "
                f"Latency: {duration:.2f}ms"
            )

        except requests.exceptions.ConnectionError:
            logging.error("Connection refused: Web server unreachable")
            
        except requests.exceptions.Timeout:
            logging.warning("Request timed out: Server did not respond within 2s")
            
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")

        time.sleep(5)

if __name__ == "__main__":
    logging.info("Starting client simulator...")
    simulate_traffic()