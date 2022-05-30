from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import get_query_status, get_data, set_data
from datetime import date

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/status")
def get_status(query):
    if get_query_status(query):
        time_to = date.fromisoformat(str(get_query_status(query)))
        time_do = date.today()
        timedelta = time_do - time_to
        if timedelta.days > 7:
            return {
                "status": True,
                "timer": False
            }
        else:
            return {
                "status": True,
                "timer": True
            }

    else:
        return {
            "status": False,
            "timer": False
        }


@app.get("/file")
def get_file(query):
    return get_data(query)


@app.post("/add_item")
def add_item(query, new_item):
    return set_data(query, new_item)
