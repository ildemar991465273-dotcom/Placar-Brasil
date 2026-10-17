import os, json, urllib.request, urllib.parse, datetime, time, threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

API_KEY=os.getenv("API_FOOTBALL_KEY","")
FD_KEY=os.getenv("FOOTBALL_DATA_KEY","")
PORT=int(os.getenv("PORT","10000"))
CACHE={}
LOCK=threading.Lock()
ROUTES={"fixtures","events","statistics","lineups","players","leagues","teams","transfers"}
def football_data_competitions():
    if not FD_KEY: raise RuntimeError("FOOTBALL_DATA_KEY não configurada")
    req=urllib.request.Request("https://api.football-data.org/v4/competitions/",headers={"X-Auth-Token":FD_KEY,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=20) as resp: data=json.loads(resp.read().decode())
    return [{"id":c.get("id"),"name":c.get("name"),"code":c.get("code"),"country":(c.get("area") or {}).get("name"),"plan":c.get("plan")} for c in data.get("competitions",[])]

def football_data_games(params):
    if not FD_KEY: raise RuntimeError("FOOTBALL_DATA_KEY não configurada no Render")
    day=params.get("date",[datetime.date.today().isoformat()])[0]
    if not __import__("re").fullmatch(r"\d{4}-\d{2}-\d{2}",day): raise ValueError("Data inválida")
    url="https://api.football-data.org/v4/matches?"+urllib.parse.urlencode({"date":day})
    request=urllib.request.Request(url,headers={"X-Auth-Token":FD_KEY,"Accept":"application/json"})
    try:
        with urllib.request.urlopen(request,timeout=20) as response: payload=json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError("football-data.org HTTP "+str(e.code)+": "+e.read(300).decode("utf-8","replace"))
    games=[]
    for match in payload.get("matches",[]):
        status=match.get("status","")
        score=match.get("score") or {}
        full=score.get("fullTime") or {}
        home=full.get("home")
        away=full.get("away")
        if home is None and away is None:
            score_label="–"
        else: score_label=str(home if home is not None else "–")+" - "+str(away if away is not None else "–")
        games.append({"id":match.get("id"),"real":True,"sport":0,
            "a":(match.get("homeTeam") or {}).get("name") or "Casa",
            "b":(match.get("awayTeam") or {}).get("name") or "Visitante",
            "ea":"⚽","eb":"⚽","league":(match.get("competition") or {}).get("name") or "",
            "country":(match.get("area") or {}).get("name") or "",
            "flag":"🌍","score":score_label,"status":status,
            "live":status in ("IN_PLAY","PAUSED","EXTRA_TIME","PENALTY_SHOOTOUT")})
    return games

def get_data(route,params):
    if route=="competitions" and FD_KEY:
        key=("football-data-competitions",)
        with LOCK:
            cached=CACHE.get(key)
            if cached and time.time()-cached[0]<86400:return cached[1]
        data=football_data_competitions()
        with LOCK:CACHE[key]=(time.time(),data)
        return data
    if route=="fixtures" and FD_KEY:
        key=("football-data",tuple(sorted((k,tuple(v)) for k,v in params.items())))
        with LOCK:
            cached=CACHE.get(key)
            if cached and time.time()-cached[0]<90:return cached[1]
        result=football_data_games(params)
        with LOCK:CACHE[key]=(time.time(),result)
        return result
    if not API_KEY: raise RuntimeError("Configure FOOTBALL_DATA_KEY ou API_FOOTBALL_KEY no servidor")
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
        if route in ("","health"):return self.send_json(200,{"service":"GolUp API","ok":True,"configured":bool(FD_KEY or API_KEY),"provider":"football-data.org" if FD_KEY else "api-football" if API_KEY else "none"})
        if not route.startswith("api/"):return self.send_json(404,{"error":"Rota não encontrada"})
        try:self.send_json(200,{"data":get_data(route.split("/",1)[1],urllib.parse.parse_qs(url.query))})
        except ValueError as e:self.send_json(400,{"error":str(e)})
        except Exception as e:self.send_json(502,{"error":str(e)[:200]})
if __name__=="__main__":ThreadingHTTPServer(("0.0.0.0",PORT),Handler).serve_forever()
