from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.auth.route import router as auth_router
from .reports.route import router as report_router
from .diagnosis.route import router as diagnosis_router


app=FastAPI(title="RBAC Medical Report Diagnosis")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "message": "Server is running"}
    
app.include_router(auth_router)
app.include_router(report_router)
app.include_router(diagnosis_router)