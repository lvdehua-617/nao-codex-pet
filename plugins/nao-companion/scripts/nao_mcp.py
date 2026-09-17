import json, os, sys, time, uuid
from pathlib import Path

DATA = Path(os.getenv("LOCALAPPDATA", Path.home())) / "NaoCompanion"
COMMANDS, STATE = DATA / "commands", DATA / "data.json"
COMMANDS.mkdir(parents=True, exist_ok=True)
TOOLS = [
 {"name":"nao_task_status","description":"Show a Codex task step in Nao's desktop bubble.","inputSchema":{"type":"object","properties":{"status":{"type":"string","enum":["working","waiting","complete","failed"]},"message":{"type":"string"}},"required":["status","message"]}},
 {"name":"nao_say","description":"Make Nao show and speak a short character message.","inputSchema":{"type":"object","properties":{"message":{"type":"string"},"animation":{"type":"string","enum":["idle","wave","jump","sad","waiting","working","done"]}},"required":["message"]}},
 {"name":"nao_start_timer","description":"Start a local focus, rest, or water timer.","inputSchema":{"type":"object","properties":{"kind":{"type":"string","enum":["focus","rest","water"]},"minutes":{"type":"integer","minimum":1,"maximum":480}},"required":["kind","minutes"]}},
 {"name":"nao_remember","description":"Save a user-approved preference to Nao's local-only memory.","inputSchema":{"type":"object","properties":{"key":{"type":"string"},"value":{"type":"string"}},"required":["key","value"]}},
 {"name":"nao_local_state","description":"Read Nao's local profile, timer, todos and affection status.","inputSchema":{"type":"object","properties":{}}}
]
def reply(mid,result=None,error=None):
 obj={"jsonrpc":"2.0","id":mid}; obj["error" if error else "result"]=error or result; print(json.dumps(obj,ensure_ascii=False),flush=True)
def enqueue(action,args):
 p=COMMANDS/f"{time.time_ns()}-{uuid.uuid4().hex}.json"; p.write_text(json.dumps({"action":action,**args,"created_at":time.time()},ensure_ascii=False),encoding="utf-8")
for line in sys.stdin:
 try:
  req=json.loads(line); method=req.get("method"); mid=req.get("id")
  if method=="initialize": reply(mid,{"protocolVersion":"2025-03-26","capabilities":{"tools":{}},"serverInfo":{"name":"nao-companion","version":"0.1.0"}})
  elif method=="notifications/initialized": continue
  elif method=="tools/list": reply(mid,{"tools":TOOLS})
  elif method=="tools/call":
   p=req.get("params",{}); name=p.get("name"); args=p.get("arguments",{})
   if name=="nao_local_state":
    try: value=json.loads(STATE.read_text(encoding="utf-8"))
    except Exception: value={"running":False,"message":"Start Nao Companion first."}
    reply(mid,{"content":[{"type":"text","text":json.dumps(value,ensure_ascii=False)}]})
   else:
    actions={"nao_task_status":"status","nao_say":"say","nao_start_timer":"timer","nao_remember":"remember"}
    if name not in actions: raise ValueError(f"Unknown tool: {name}")
    enqueue(actions[name],args); reply(mid,{"content":[{"type":"text","text":"奈绪已收到。"}]})
  elif mid is not None: reply(mid,{})
 except Exception as exc:
  if 'mid' in locals() and mid is not None: reply(mid,error={"code":-32603,"message":str(exc)})
