from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from agent import build_graph

app = FastAPI()

# CORS CONFIG
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_graph()


class BlogRequest(BaseModel):
    topic: str


@app.post("/generate")
def generate_blog(req: BlogRequest):

    result = graph.invoke({
        "topic": req.topic,
        "sections": []
    })

    return {"blog": result["final"]}