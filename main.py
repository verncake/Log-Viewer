import os
import glob
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()
LOG_DIR = os.path.expanduser("~/Work/Logs")
SECRET_TOKEN = os.getenv("LOG_VIEW_TOKEN")

@app.get("/view", response_class=HTMLResponse)
async def read_logs(token: str):
    if token != SECRET_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    files = glob.glob(os.path.join(LOG_DIR, "*.log"))
    if not files:
        return "<html><body><h1>No logs found</h1></body></html>"
    
    latest_file = max(files, key=os.path.getmtime)
    
    with open(latest_file, "r") as f:
        lines = f.readlines()[-100:]
        
    log_content = "".join(lines)
    
    return f"""
    <html>
        <head>
            <title>Log Viewer</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <style>
                body {{ background-color: #1a202c; color: #cbd5e0; font-family: monospace; }}
                pre {{ padding: 1rem; border-radius: 0.5rem; background: #2d3748; overflow-x: auto; }}
            </style>
        </head>
        <body class="p-8">
            <h1 class="text-2xl font-bold mb-4 text-white">Log Viewer: {latest_file}</h1>
            <pre class="border border-gray-700">{log_content}</pre>
        </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
