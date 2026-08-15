from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def get_api_info():
    
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }
@app.get("/health")
async def health_check():

    return {"status": "ok"}