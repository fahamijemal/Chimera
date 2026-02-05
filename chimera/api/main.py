from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from chimera.api.routes import fleet, hitl

app = FastAPI(title="Chimera Orchestrator API", version="0.1.0")

# Configure CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(fleet.router, prefix="/api/fleet", tags=["Fleet"])
app.include_router(hitl.router, prefix="/api/hitl", tags=["HITL"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "chimera-orchestrator"}
