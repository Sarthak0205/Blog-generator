from __future__ import annotations

import os
import operator
from typing import TypedDict, List, Annotated

from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq


# ---------- Load ENV ----------
load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")

if not groq_key:
    raise ValueError("GROQ_API_KEY not found in .env file")


# ---------- Models ----------

class Task(BaseModel):
    id: int
    titles: str
    brief: str = Field(..., description="what to cover")


class Plan(BaseModel):
    blog_title: str
    tasks: List[Task]


class State(TypedDict):
    topic: str
    plan: Plan
    sections: Annotated[List[str], operator.add]
    final: str


# ---------- LLM ----------

llm = ChatGroq(
    model="qwen/qwen3-32b",
    api_key=groq_key
)


# ---------- Orchestrator ----------

def orchestrator(state: State) -> dict:

    plan = llm.with_structured_output(Plan).invoke(
        [
            SystemMessage(
                content="Create a blog plan with 5–7 sections."
            ),
            HumanMessage(content=f"Topic: {state['topic']}"),
        ]
    )

    return {"plan": plan}


# ---------- Fanout ----------

def fanout(state: State):

    return [
        Send(
            "worker",
            {
                "task": task,
                "topic": state["topic"],
                "plan": state["plan"]
            }
        )
        for task in state["plan"].tasks
    ]


# ---------- Worker ----------

def worker(payload: dict) -> dict:

    task = payload["task"]
    topic = payload["topic"]
    plan = payload["plan"]

    section_md = llm.invoke(
        [
            SystemMessage(content="Write one clean Markdown section."),
            HumanMessage(
                content=(
                    f"Blog: {plan.blog_title}\n"
                    f"Topic: {topic}\n\n"
                    f"Section: {task.titles}\n"
                    f"Brief: {task.brief}\n\n"
                    "Return only the section content in Markdown."
                )
            ),
        ]
    ).content.strip()

    return {"sections": [section_md]}


# ---------- Reducer ----------

import re

def reducer(state: State) -> dict:

    title = state["plan"].blog_title
    body = "\n\n".join(state["sections"]).strip()

    final_md = f"# {title}\n\n{body}\n"

    # remove reasoning blocks if model outputs them
    final_md = re.sub(r"<think>.*?</think>", "", final_md, flags=re.DOTALL)

    return {"final": final_md}


# ---------- Graph Builder ----------

def build_graph():

    g = StateGraph(State)

    g.add_node("orchestrator", orchestrator)
    g.add_node("worker", worker)
    g.add_node("reducer", reducer)

    g.add_edge(START, "orchestrator")
    g.add_conditional_edges("orchestrator", fanout, ["worker"])
    g.add_edge("worker", "reducer")
    g.add_edge("reducer", END)

    return g.compile()