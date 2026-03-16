import os
import glob
from fastapi import FastAPI, HTTPException, Header
import uvicorn

app = FastAPI()
LOG_DIR = os.path.expanduser("~/Work/Logs")
SECRET_TOKEN = os.getenv("LOG_VIEW_TOKEN")

@app.get("/view")
async def read_logs(token: str):
    if token != SECRET_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    files = glob.glob(os.path.join(LOG_DIR, "*.log"))
    if not files:
        return {"error": "No logs found"}
    
    latest_file = max(files, key=os.path.getmtime)
    
    with open(latest_file, "r") as f:
        lines = f.readlines()[-100:]
        
    return {"file": latest_file, "content": "".join(lines)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
