#!/usr/bin/env python3
import io,json,hashlib,runpy,sys,urllib.request
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent
RAW=OUT/"raw"; RAW.mkdir(exist_ok=True)
REAL=urllib.request.urlopen
records=[]
class RecordedResponse:
 def __init__(self,data,response):
  self._io=io.BytesIO(data); self.status=getattr(response,"status",None); self.code=getattr(response,"code",self.status); self.headers=getattr(response,"headers",{}); self.url=getattr(response,"url",None)
 def read(self,*a,**k): return self._io.read(*a,**k)
 def readable(self): return True
 def getcode(self): return self.code
 def geturl(self): return self.url
 def info(self): return self.headers
 def __enter__(self): return self
 def __exit__(self,*a): self._io.close()
def recording_urlopen(req,*args,**kwargs):
 ordinal=len(records)+1; started=datetime.now(timezone.utc).isoformat()
 response=REAL(req,*args,**kwargs); data=response.read(); ended=datetime.now(timezone.utc).isoformat()
 url=req.full_url if hasattr(req,"full_url") else str(req); method=req.get_method() if hasattr(req,"get_method") else "GET"; body=(req.data or b"") if hasattr(req,"data") else b""
 try: keyword=json.loads(body).get("keyword","")
 except Exception: keyword=""
 raw=RAW/f"{ordinal:03d}-{keyword}.json"; raw.write_bytes(data)
 rec={"ordinal":ordinal,"url":url,"method":method,"request_headers":dict(req.header_items()) if hasattr(req,"header_items") else {},"request_body_utf8":body.decode("utf-8"),"request_body_sha256":hashlib.sha256(body).hexdigest(),"fetch_started_utc":started,"fetch_completed_utc":ended,"http_status":getattr(response,"status",None),"raw_response_path":str(raw),"raw_response_bytes":len(data),"raw_response_sha256":hashlib.sha256(data).hexdigest()}
 records.append(rec)
 with open(OUT/"http_capture.jsonl","a") as f:f.write(json.dumps(rec,sort_keys=True,separators=(",",":"))+"\n")
 try: response.close()
 except Exception: pass
 return RecordedResponse(data,response)
urllib.request.urlopen=recording_urlopen
tool=Path(sys.argv[1]).resolve(); sys.argv=[str(tool),*sys.argv[2:]]; sys.path.insert(0,str(tool.parent))
try: runpy.run_path(str(tool),run_name="__main__")
finally: urllib.request.urlopen=REAL
