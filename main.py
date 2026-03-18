import os
import glob
import html
import hmac
from fastapi import FastAPI, HTTPException, Request, Cookie, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from jinja2 import Template
import uvicorn
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
LOG_DIR = os.path.expanduser("~/Work/Logs")

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html class="h-full bg-slate-900">
    <head>
        <title>Login - Log Viewer</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="h-full flex items-center justify-center p-4">
        <div class="w-full max-w-sm bg-slate-800 p-8 rounded-xl shadow-2xl border border-slate-700">
            <h1 class="text-2xl font-black text-white mb-6 text-center">Log Viewer <span class="text-indigo-500">Access</span></h1>
            <form action="/login" method="post">
                <input type="password" name="token" placeholder="Enter Access Token" class="w-full p-3 mb-4 bg-slate-900 text-white rounded border border-slate-600 focus:border-indigo-500 outline-none">
                <button type="submit" class="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded transition">Enter</button>
            </form>
            <div id="error" class="text-red-400 text-sm mt-4 hidden text-center font-bold">Invalid Access Token</div>
        </div>
        <script>
            if (new URLSearchParams(window.location.search).has('error')) {
                document.getElementById('error').classList.remove('hidden');
            }
        </script>
    </body>
</html>
"""

HTML_TEMPLATE = """
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
                <div class="flex items-center gap-4">
                    <div class="text-sm text-slate-400 bg-slate-800 px-3 py-1 rounded-full font-mono border border-slate-700">
                        {{ filename }}
                    </div>
                    <form action="/logout" method="post">
                        <button type="submit" class="text-xs text-red-400 hover:text-red-300 font-bold">Logout</button>
                    </form>
                </div>
            </header>
            <main>
                <div class="rounded-xl border border-slate-700 bg-slate-800 shadow-2xl overflow-hidden">
                    <div class="border-b border-slate-700 bg-slate-900 px-4 py-2 flex items-center space-x-2">
                        <div class="w-3 h-3 rounded-full bg-red-500"></div>
                        <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
                        <div class="w-3 h-3 rounded-full bg-green-500"></div>
                    </div>
                    <pre class="p-6 text-sm text-green-400 font-mono leading-relaxed whitespace-pre-wrap">{{ content }}</pre>
                </div>
            </main>
        </div>
    </body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index():
    return LOGIN_TEMPLATE

@app.post("/login")
async def login(token: str = Form(...)):
    SECRET_TOKEN = os.getenv("LOG_VIEW_TOKEN")
    if not SECRET_TOKEN or not hmac.compare_digest(token, SECRET_TOKEN):
        return RedirectResponse(url="/?error=1", status_code=303)
    
    response = RedirectResponse(url="/view", status_code=303)
    response.set_cookie(key="token", value=token, httponly=True, secure=False, samesite="strict")
    return response

@app.post("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("token")
    return response

@app.get("/view", response_class=HTMLResponse)
async def read_logs(token: str = Cookie(None)):
    SECRET_TOKEN = os.getenv("LOG_VIEW_TOKEN")
    if not SECRET_TOKEN or not token or not hmac.compare_digest(token, SECRET_TOKEN):
        return RedirectResponse(url="/")
    
    files = glob.glob(os.path.join(LOG_DIR, "*.log"))
    if not files:
        return "<html><body><h1>No logs found</h1></body></html>"
    
    latest_file = max(files, key=os.path.getmtime)
    
    with open(latest_file, "r") as f:
        lines = f.readlines()[-100:]
        
    log_content = "".join(lines)
    
    template = Template(HTML_TEMPLATE)
    return template.render(
        filename=html.escape(os.path.basename(latest_file)),
        content=html.escape(log_content)
    )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
