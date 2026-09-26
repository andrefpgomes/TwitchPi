#!/usr/bin/env python3
import json, os, re, subprocess, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

BASE="/opt/twitch-pi"
PORT=int(os.environ.get("PORT","8765"))
STATE_FILE=os.environ.get("STATE_FILE",BASE+"/state.json")
WEB=BASE+"/web"
PROFILE=os.environ.get("TWITCH_PROFILE",os.path.expanduser("~/.config/twitch-pi-chromium"))
CHANNEL_RE=re.compile(r"^[A-Za-z0-9_]{1,30}$")

def load_state():
    state={"channel":"","status":"stopped","last_changed":None,"favorites":[]}
    try:
        with open(STATE_FILE,encoding="utf-8") as f: state.update(json.load(f))
    except Exception: pass
    state.setdefault("favorites",[]); return state

def save_state(s):
    os.makedirs(os.path.dirname(STATE_FILE),exist_ok=True); tmp=STATE_FILE+".tmp"
    with open(tmp,"w",encoding="utf-8") as f: json.dump(s,f,ensure_ascii=False,indent=2)
    os.replace(tmp,STATE_FILE)

def chromium():
    for x in ("chromium","chromium-browser"):
        if subprocess.call(["bash","-lc",f"command -v {x} >/dev/null 2>&1"])==0: return x
    return None

def stop_chromium():
    subprocess.run(["pkill","-f",f"--user-data-dir={PROFILE}"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

def start_chromium(url):
    cmd=chromium()
    if not cmd: raise RuntimeError("Chromium não está instalado.")
    os.makedirs(PROFILE,exist_ok=True)
    subprocess.Popen([cmd,f"--user-data-dir={PROFILE}","--no-first-run","--noerrdialogs","--disable-session-crashed-bubble","--disable-infobars",url],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

def open_channel(channel):
    if not CHANNEL_RE.fullmatch(channel): raise ValueError("Nome de canal Twitch inválido.")
    url="https://www.twitch.tv/"+channel; stop_chromium(); time.sleep(1); start_chromium(url); return url

def respond(h,code,obj):
    data=json.dumps(obj,ensure_ascii=False).encode(); h.send_response(code)
    h.send_header("Content-Type","application/json; charset=utf-8"); h.send_header("Cache-Control","no-store")
    h.send_header("Access-Control-Allow-Origin","*"); h.send_header("Content-Length",str(len(data))); h.end_headers(); h.wfile.write(data)

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/api/status":
            s=load_state(); s["hostname"]=os.uname().nodename; s["chromium"]=chromium() is not None; s["server_time"]=int(time.time()); respond(self,200,s); return
        if path=="/api/start":
            try:
                s=load_state()
                if not s.get("channel"): raise RuntimeError("Nenhum canal está selecionado.")
                s["url"]=open_channel(s["channel"]); s["status"]="playing"; s["last_changed"]=int(time.time()); save_state(s); respond(self,200,s)
            except Exception as e: respond(self,400,{"error":str(e)})
            return
        if path=="/api/stop":
            try:
                stop_chromium(); s=load_state(); s["status"]="stopped"; s["last_changed"]=int(time.time()); save_state(s); respond(self,200,s)
            except Exception as e: respond(self,400,{"error":str(e)})
            return
        if path=="/api/login":
            try:
                cmd=chromium()
                if not cmd: raise RuntimeError("Chromium não está instalado.")
                os.makedirs(PROFILE,exist_ok=True)
                subprocess.Popen([cmd,f"--user-data-dir={PROFILE}","--no-first-run","--noerrdialogs","https://www.twitch.tv/login"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                respond(self,200,{"ok":True,"message":"O login Twitch foi aberto no Chromium."})
            except Exception as e: respond(self,400,{"error":str(e)})
            return
        if path=="/": path="/index.html"
        files={"/index.html":"text/html; charset=utf-8","/style.css":"text/css; charset=utf-8","/app.js":"application/javascript; charset=utf-8"}
        if path in files:
            try: data=open(WEB+path,"rb").read()
            except FileNotFoundError: self.send_error(404); return
            self.send_response(200); self.send_header("Content-Type",files[path]); self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data); return
        self.send_error(404)
    def do_POST(self):
        path=urlparse(self.path).path
        if path not in ("/api/channel","/api/favorite"): respond(self,404,{"error":"not found"}); return
        try:
            n=int(self.headers.get("Content-Length","0")); body=json.loads(self.rfile.read(n) or b"{}"); s=load_state()
            if path=="/api/channel":
                c=str(body.get("channel","")).strip()
                if not CHANNEL_RE.fullmatch(c): raise ValueError("Canal Twitch inválido.")
                s["channel"]=c; save_state(s); respond(self,200,s); return
            c=str(body.get("channel","")).strip()
            if not CHANNEL_RE.fullmatch(c): raise ValueError("Canal inválido.")
            fav=s.get("favorites",[])
            if body.get("action")=="add" and c not in fav: fav.append(c)
            if body.get("action")=="remove": fav=[x for x in fav if x!=c]
            s["favorites"]=fav[:30]; save_state(s); respond(self,200,s)
        except Exception as e: respond(self,400,{"error":str(e)})

if __name__=="__main__":
    save_state(load_state()); ThreadingHTTPServer(("0.0.0.0",PORT),Handler).serve_forever()
