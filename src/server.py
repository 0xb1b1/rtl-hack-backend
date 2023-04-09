"""Docstring."""
from os import getenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from modules.database.db import init_db
from routers import auth, profile, customs, resolvers, statistics
from modules.database.models import Metric, TaskGoal, Task, Script, \
    StatisticsProto


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(customs.router)
app.include_router(resolvers.router)
app.include_router(statistics.router)


@app.on_event("startup")
async def start_db():
    """Start database on FastAPI startup."""
    await init_db(getenv("MONGODB_USER", ""),
                  getenv("MONGODB_PASS", ""),
                  getenv("MONGODB_HOST", ""),
                  getenv("MONGODB_PORT", ""))

    await load_mock_data("modules/database/mock_data/mock_achievements.json",
                         "modules/database/mock_data/mock_statistics.json")


async def load_mock_data(achievements_f: str,
                         statistics_f: str):
    """Fill the Beanie scripts, metrics, ... with data from a JSON file."""
    # Do not re-populate the database - check if any scripts exist
    if len(await Script.find().to_list()) != 0:
        return

    from json import load
    with open(achievements_f, 'r') as f:
        data = load(f)

    for script in data['scripts']:
        await Script.insert_one(Script(**script))

    for task in data['tasks']:
        await Task.insert_one(Task(**task))

    for task_goal in data['task_goals']:
        await TaskGoal.insert_one(TaskGoal(**task_goal))

    for metric in data['metrics']:
        await Metric.insert_one(Metric(**metric))

    with open(statistics_f, 'r') as f:
        data_stat: dict = load(f)['statistics']

    await StatisticsProto.insert_one(StatisticsProto(daily=data_stat['day'],
                                                     monthly=None,
                                                     yearly=None))

    (await (await StatisticsProto.find_one())  # type: ignore
        .set({StatisticsProto.monthly: data_stat['month']}))  # type: ignore

    (await (await StatisticsProto.find_one())  # type: ignore
        .set({StatisticsProto.yearly: data_stat['year']}))  # type: ignore
