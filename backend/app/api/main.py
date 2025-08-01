from fastapi import FastAPI
from backend.app.api.routes import screening, jobs, feedback, candidates, similarity

app = FastAPI(title="AI Screening API", debug=True)

app.include_router(screening.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(feedback.router, prefix="/api")
app.include_router(candidates.router, prefix="/api")
app.include_router(similarity.router, prefix="/api")