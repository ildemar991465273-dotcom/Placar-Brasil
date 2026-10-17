import os, json, urllib.request, urllib.parse, datetime, time, threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

API_KEY=os.getenv("API_FOOTBALL_KEY","")
PORT=int(os.getenv("PORT","10000"))
CACHE={}
LOCK=threading.Lock()
ROUTES={"fixtures","events","statistics","lineups","players","leagues","teams","transfers"}
def get_data(route,params):
    if not API_KEY: raise RuntimeError("API_FOOTBALL_KEY não configurada no servidor")
    if route not in ROUTES: raise ValueError("Rota desconhecida")
    params={k:v[0] for k,v in params.items() if k in {"date","fixture","league","season","team","id","player","live","country","search","timezone","from","to"} and v and len(v[0])<=100}
    if route=="fixtures" and "date" not in params and "live" not in params: params["date"]=datetime.date.today().isoformat()
    key=(route,tuple(sorted(params.items())))
    ttl=40 if route in {"fixtures","events"} else 240
    with LOCK:
        cached=CACHE.get(key)
        if cached and time.time()-cached[0]<ttl:return cached[1]
    url="https://v3.football.api-sports.io/"+route+"?"+urllib.parse.urlencode(params)
    request=urllib.request.Request(url,headers={"x-apisports-key":API_KEY,"Accept":"application/json","User-Agent":"GolUp/2.9"})
    with urllib.request.urlopen(request,timeout=20) as response: value=json.loads(response.read().decode())
    if value.get("errors"): raise RuntimeError("API-Football: "+str(value["errors"])[:200])
    result=value.get("response",[])
    if route=="fixtures":result=[{
        "id":v.get("fixture",{}).get("id"),"real":True,"sport":0,
        "a":v.get("teams",{}).get("home",{}).get("name","Casa"),
        "b":v.get("teams",{}).get("away",{}).get("name","Visitante"),
        "ea":"⚽","eb":"⚽","league":v.get("league",{}).get("name",""),
        "country":v.get("league",{}).get("country",""),
        "flag":"🌍",
        "score":(str(v.get("goals",{}).get("home") if v.get("goals",{}).get("home") is not None else "–")+" - "+str(v.get("goals",{}).get("away") if v.get("goals",{}).get("away") is not None else "–")),
        "status":v.get("fixture",{}).get("status",{}).get("short",""),
        "live":v.get("fixture",{}).get("status",{}).get("short","") in ["1H","HT","2H","ET","P","BT","LIVE"]
    } for v in result]
    with LOCK:CACHE[key]=(time.time(),result)
    return result

class Handler(BaseHTTPRequestHandler):
    def send_json(self,code,data):
        raw=json.dumps(data,ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(raw)))
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Methods","GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers","Content-Type")
        self.end_headers();self.wfile.write(raw)
    def do_OPTIONS(self):self.send_json(200,{})
    def do_GET(self):
        url=urllib.parse.urlparse(self.path);route=url.path.strip("/")
        if route in ("","health"):return self.send_json(200,{"service":"GolUp API","ok":True,"configured":bool(API_KEY)})
        if not route.startswith("api/"):return self.send_json(404,{"error":"Rota não encontrada"})
        try:self.send_json(200,{"data":get_data(route.split("/",1)[1],urllib.parse.parse_qs(url.query))})
        except ValueError as e:self.send_json(400,{"error":str(e)})
        except Exception as e:self.send_json(502,{"error":str(e)[:200]})
if __name__=="__main__":ThreadingHTTPServer(("0.0.0.0",PORT),Handler).serve_forever()
