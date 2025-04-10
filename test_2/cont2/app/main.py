from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI()
API_SERVICE_URL = "http://fastapi-app:8000"  # Nome del servizio dal compose

@app.get("/combined")
async def get_combined_data():
    try:
        async with httpx.AsyncClient() as client:
            # Chiamata al primo container
            response = await client.get(f"{API_SERVICE_URL}/")
            api_data = response.json()
            
        return {
            "client_message": "Data from client service",
            "api_service_data": api_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    try:
        async with httpx.AsyncClient() as client:
            await client.get(f"{API_SERVICE_URL}/health")
        return {"status": "connected", "service": "client"}
    except:
        return {"status": "disconnected", "service": "client"}