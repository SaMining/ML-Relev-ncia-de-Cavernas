from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from ml_relev_ncia_de_cavernas.api.routes import router
from pathlib import Path
import joblib

BASE_DIR = Path(__file__).parent

app = FastAPI()
print(BASE_DIR)
app.state.model = joblib.load(BASE_DIR / "artifacts/random_forest_carajas_v4.pkl")

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)

app.include_router(router=router)