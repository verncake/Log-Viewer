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
    <!DOCTYPE html>
    <html class="h-full bg-slate-900">
        <head>
            <title>Log Viewer Pro</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="h-full p-4 md:p-8">
            <div class="max-w-7xl mx-auto">
                <header class="mb-6 flex justify-between items-center">
                    <h1 class="text-3xl font-black text-white tracking-tighter">
                        <span class="text-indigo-500">Log</span>Viewer
                    </h1>
                    <div class="text-sm text-slate-400 bg-slate-800 px-3 py-1 rounded-full font-mono border border-slate-700">
                        {os.path.basename(latest_file)}
                    </div>
                </header>
                <main>
                    <div class="rounded-xl border border-slate-700 bg-slate-800 shadow-2xl overflow-hidden">
                        <div class="border-b border-slate-700 bg-slate-900 px-4 py-2 flex items-center space-x-2">
                            <div class="w-3 h-3 rounded-full bg-red-500"></div>
                            <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
                            <div class="w-3 h-3 rounded-full bg-green-500"></div>
                        </div>
                        <pre class="p-6 text-sm text-green-400 font-mono leading-relaxed whitespace-pre-wrap">{log_content}</pre>
                    </div>
                </main>
            </div>
        </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
