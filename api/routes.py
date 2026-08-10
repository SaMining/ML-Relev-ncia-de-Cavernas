from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
from .models import PredictionRequest
import pandas as pd

router = APIRouter()

@router.get("/")
def home():
    return FileResponse(
        "templates/index.html"
    ) 

@router.post("/predict")
def predict(
    request:Request,
    data: PredictionRequest
    ):

    model = request.app.state.model

    df = pd.DataFrame(
        [
            data.model_dump()
        ]
    )

    proba = model.predict_proba(df)

    return {
        "score" : float(proba[0][1])
    }