# backend/main.py
from fastapi import FastAPI, Response, Request, WebSocket, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import secrets
import time
import json
import hashlib
import requests

# Import enterprise modules
from backend.enhancements import EnterpriseFeatures
from backend.security import EnhancedSecurity
from backend.database import ProductionDatabase
from backend.monitoring import ProductionMonitor

# -- Progress status (replace with database in production) --
dash_state = {
    "legal": [{"label": "SEC Registration", "status": "PENDING"}],
    "technical": [{"label": "Core Architecture", "status": "IN PROGRESS"}],
    "business": [{"label": "Partnership Pipeline", "status": "ACTIVE OUTREACH"}],
    "resource_allocation": [
        {"name": "Technical Development", "percent": 40},
        {"name": "Legal & Compliance", "percent": 25},
    ],
    "risk": {"identified": ["Regulatory compliance challenges"], "mitigation": ["Early legal counsel engagement"]}
}
auditlog = []
last_hash = None

# -- Chain-audited, time-stamped hash calculation --
def hash_state(state, prev_hash=None):
    now = int(time.time() * 1000)
    payload = json.dumps({"state": state, "ts": now, "prev": prev_hash}, sort_keys=True)
    digest = hashlib.sha3_512(payload.encode('utf-8')).hexdigest()
    return digest, payload, now

def add_auditlog(state):
    global last_hash
    digest, payload, ts = hash_state(state, last_hash)
    auditlog.append({"ts": ts, "hash": digest, "prev": last_hash, "payload": payload})
    last_hash = digest

# -- Initial anchor --
add_auditlog(dash_state)

# -- Quantum randomness hook --
def get_quantum_randfloat():
    try:
        res = requests.get('https://qrng.anu.edu.au/API/jsonI.php?length=1&type=uint8', timeout=2)
        if res.status_code == 200:
            qval = res.json()['data'][0] / 255.0
            return qval
        else:
            return secrets.randbelow(10**12) / 1e12
    except Exception:
        return secrets.randbelow(10**12) / 1e12

def get_status_sync():
    qrand = get_quantum_randfloat()
    audit_entry = auditlog[-1] if auditlog else None
    return {
        "status": dash_state,
        "audit": {
            "root_hash": audit_entry['hash'] if audit_entry else "",
            "timestamp": audit_entry['ts'] if audit_entry else "",
            "quantum_rand": qrand
        }
    }


# -- Initialize Enterprise Modules --
enterprise = EnterpriseFeatures(get_status_sync)
security = EnhancedSecurity()
production_db = ProductionDatabase()
monitor = ProductionMonitor()
bearer_scheme = HTTPBearer()

# -- Initialize FastAPI App --
app = FastAPI(title="ValorAI Plus Quantum-Resilient Audit Dashboard")

# -- Add Middleware --
app.middleware("http")(security.rate_limit_middleware)

# -- API Endpoints --

@app.get("/api/status")
def get_status(request: Request):
    enterprise.track_analytics("/api/status")
    production_db.log_analytics_event("get_status", ip_address=request.client.host)
    return get_status_sync()

@app.get("/api/auditlog")
def get_audit_log(request: Request):
    enterprise.track_analytics("/api/auditlog")
    production_db.log_analytics_event("get_auditlog", ip_address=request.client.host)
    return {"auditlog": auditlog}

class UpdateItem(BaseModel):
    key: str
    value: list

@app.post("/api/status/update")
async def update_status(item: UpdateItem, request: Request):
    enterprise.track_analytics("/api/status/update")
    production_db.log_analytics_event("update_status", event_data=item.dict(), ip_address=request.client.host)

    # For demo: update in-memory state
    dash_state[item.key] = item.value
    add_auditlog(dash_state)

    # Broadcast the update
    await enterprise.broadcast_progress_update(get_status_sync())

    return {"success": True, "auditlog": auditlog[-1]}

@app.get("/api/pdf")
def get_pdf(request: Request):
    enterprise.track_analytics("/api/pdf")
    production_db.log_analytics_event("get_pdf", ip_address=request.client.host)
    pdf_bytes = b'%PDF-1.7\n%ValorAIPlus Evidence\n... (BODY) ...\n%%EOF'
    hashfooter = f"\nSHA3-512: {last_hash}\nQuantum-RNG-Seed: {get_quantum_randfloat()}"
    pdf_full = pdf_bytes + hashfooter.encode()
    return Response(content=pdf_full, media_type="application/pdf")

# -- Enterprise Endpoints --

@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    await enterprise.websocket_endpoint(websocket)

@app.get("/api/monitoring/metrics")
async def get_monitoring_metrics(request: Request, token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    if not security.validate_api_key(token):
        raise HTTPException(status_code=401, detail="Invalid API Key")
    enterprise.track_analytics("/api/monitoring/metrics")
    production_db.log_analytics_event("get_monitoring_metrics", ip_address=request.client.host)
    return monitor.get_system_metrics()

@app.get("/api/admin/analytics")
async def get_admin_analytics(request: Request, token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    if not security.validate_api_key(token):
        raise HTTPException(status_code=401, detail="Invalid API Key")
    enterprise.track_analytics("/api/admin/analytics")
    production_db.log_analytics_event("get_admin_analytics", ip_address=request.client.host)
    return await enterprise.get_system_analytics()

class KeyGenRequest(BaseModel):
    client_name: str

@app.post("/api/admin/generate_key")
def generate_key(req: KeyGenRequest, token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    # This should be a highly protected endpoint
    # For demo, we allow key generation with another valid key
    if not security.validate_api_key(token):
        raise HTTPException(status_code=401, detail="Invalid API Key for key generation")
    return {"client_name": req.client_name, "api_key": security.generate_api_key(req.client_name)}
