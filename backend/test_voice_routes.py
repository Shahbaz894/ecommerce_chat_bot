from fastapi import FastAPI, UploadFile, File

app = FastAPI()

@app.post("/api/voice/query-json")
async def test_endpoint(file: UploadFile = File(...)):
    return {"message": "Working!", "filename": file.filename}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("test_voice_routes:app", host="127.0.0.1", port=8000, reload=True)