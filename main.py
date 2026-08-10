from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.routes import router
import joblib

app = FastAPI()

app.state.model = joblib.load("./artifacts/random_forest_v3.pkl")

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

app.include_router(router=router)