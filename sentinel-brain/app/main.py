from fastapi import FastAPI

app = FastAPI(title="Sentinel Brain", version="1.0.0")

@app.get("/health")
def health_check():
    return {"status": "operational", "module": "sentinel-brain"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)