from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import children, dashboard, exercises, sessions

app = FastAPI(title="VaakMirror API", version="0.1.0")

# Wildcard for now, not settings.cors_origin_list — this app has no auth yet
# (a deliberate, documented decision, not an oversight — see README), so a
# specific-origin allowlist wasn't actually protecting anything, just
# creating exact-match friction in local dev (different ports, localhost
# vs 127.0.0.1, etc.). Revisit this alongside adding real auth.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(children.router)
app.include_router(sessions.router)
app.include_router(dashboard.router)
app.include_router(exercises.router)


@app.get("/health")
def health():
    return {"status": "ok"}
