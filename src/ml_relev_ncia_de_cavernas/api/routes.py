from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import FileResponse
from ml_relev_ncia_de_cavernas.api.models import PredictionRequest
import pandas as pd
from fastapi.responses import StreamingResponse
from io import BytesIO
from pathlib import Path

router = APIRouter()

BASE_DIR = Path(__file__).parent


@router.get("/")
def home():
    return FileResponse(
        str( BASE_DIR.parent / "templates/index.html")
    ) 

@router.get("/favicon.ico")
def home():
    return FileResponse(
        str( BASE_DIR.parent / "static/images/favicon.ico")
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

@router.post("/predict-batch")
async def predict_batch(
    request: Request,
    file: UploadFile = File(...)
):

    model = request.app.state.model
    content = await file.read()

    df = pd.read_excel(BytesIO(content))

    df_to_predict = df.drop(columns=["cavidade", "target"])

    proba = model.predict_proba(df_to_predict)

    df["score"] = proba[:, 1]
    df_to_return = df[["cavidade", "target", "score"]]    
    output = BytesIO()

    df_to_return.to_excel(
        output,
        index=False
    )

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition":
                "attachment; filename=resultado.xlsx"
        }
    )