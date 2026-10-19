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
    #treinamento original e quadrilatero V3
    columns = ['cavidade', 'nome_entrada', 'desenv_aproximado', 'desnivel_propeccao',
       'zona_afotica', 'raizes', 'target', 'animal_observado_anfibios',
       'animal_observado_aves', 'animal_observado_invertebrados',
       'animal_observado_mamiferos', 'animal_observado_morcegos',
       'animal_observado_ninhos', 'animal_observado_peixes',
       'animal_observado_repteis', 'tipo_espeleotema_coraloides',
       'tipo_espeleotema_crosta', 'tipo_espeleotema_escorrimentos',
       'tipo_espeleotema_estalactites', 'tipo_espeleotema_estalagmites',
       'tipo_espeleotema_pingente', 'tipo_espeleotema_travertinos',
       'feicao_hidrologica_cachoeira', 'feicao_hidrologica_condensacao',
       'feicao_hidrologica_drenagem', 'feicao_hidrologica_gotejamento',
       'feicao_hidrologica_lago', 'feicao_hidrologica_percolacao',
       'dificuldade_interna_blocos_instaveis',
       'dificuldade_interna_lances_verticais',
       'dificuldade_interna_quebra_corpo', 'dificuldade_interna_rastejamento',
       'dificuldade_interna_teto_baixo', 'feicao_interna_blocos_abatidos',
       'feicao_interna_canaliculos', 'feicao_interna_claraboias',
       'feicao_interna_conduto', 'arqueologia_paleontologia_ceramico',
       'arqueologia_paleontologia_litico', 'arqueologia_paleontologia_ossada',
       'arqueologia_paleontologia_vestigio_historico',
       'litotipo_prospeccao_granito_gnaisse',
       'litotipo_prospeccao_rochas_carbonaticas',
       'litotipo_prospeccao_rochas_ferriferas',
       'litotipo_prospeccao_rochas_peliticas',
       'litotipo_prospeccao_rochas_siliciosas', 'ocorrencia_guano_concentrado',
       'ocorrencia_guano_disperso', 'tipo_cavidade__abrigo',
       'tipo_cavidade__cavidade', 'tipo_cavidade__feicao_espeleologica']

    #V4
    columns = ['cavidade','target', 'nome_entrada', 'zona_afotica', 'raizes', 'projecao_horizontal',
       'desnivel_topografia', 'area', 'volume', 'animal_observado_anfibios',
       'animal_observado_aves', 'animal_observado_invertebrados',
       'animal_observado_mamiferos', 'animal_observado_morcegos',
       'animal_observado_ninhos', 'animal_observado_peixes',
       'animal_observado_repteis', 'tipo_espeleotema_coraloides',
       'tipo_espeleotema_crosta', 'tipo_espeleotema_escorrimentos',
       'tipo_espeleotema_estalactites', 'tipo_espeleotema_estalagmites',
       'tipo_espeleotema_pingente', 'tipo_espeleotema_travertinos',
       'feicao_hidrologica_cachoeira', 'feicao_hidrologica_condensacao',
       'feicao_hidrologica_drenagem', 'feicao_hidrologica_gotejamento',
       'feicao_hidrologica_lago', 'feicao_hidrologica_percolacao',
       'dificuldade_interna_blocos_instaveis',
       'dificuldade_interna_lances_verticais',
       'dificuldade_interna_quebra_corpo', 'dificuldade_interna_rastejamento',
       'dificuldade_interna_teto_baixo', 'feicao_interna_blocos_abatidos',
       'feicao_interna_canaliculos', 'feicao_interna_claraboias',
       'feicao_interna_conduto', 'arqueologia_paleontologia_ceramico',
       'arqueologia_paleontologia_litico', 'arqueologia_paleontologia_ossada',
       'arqueologia_paleontologia_vestigio_historico',
       'litotipo_prospeccao_granito_gnaisse',
       'litotipo_prospeccao_rochas_carbonaticas',
       'litotipo_prospeccao_rochas_ferriferas',
       'litotipo_prospeccao_rochas_peliticas',
       'litotipo_prospeccao_rochas_siliciosas', 'ocorrencia_guano_concentrado',
       'ocorrencia_guano_disperso', 'tipo_cavidade__abrigo',
       'tipo_cavidade__cavidade', 'tipo_cavidade__feicao_espeleologica']

    #treinamento carajas V3
    # columns = ['cavidade', 'nome_entrada', 'desenv_aproximado', 'desnivel_propeccao',
    #    'zona_afotica', 'raizes', 'target', 'animal_observado_anfibios',
    #    'animal_observado_aves', 'animal_observado_invertebrados',
    #    'animal_observado_mamiferos', 'animal_observado_morcegos',
    #    'animal_observado_ninhos', 'animal_observado_peixes',
    #    'animal_observado_repteis', 'tipo_espeleotema_coraloides',
    #    'tipo_espeleotema_crosta', 'tipo_espeleotema_escorrimentos',
    #    'tipo_espeleotema_estalactites', 'tipo_espeleotema_estalagmites',
    #    'tipo_espeleotema_pingente', 'tipo_espeleotema_travertinos',
    #    'feicao_hidrologica_cachoeira', 'feicao_hidrologica_condensacao',
    #    'feicao_hidrologica_drenagem', 'feicao_hidrologica_gotejamento',
    #    'feicao_hidrologica_lago', 'feicao_hidrologica_percolacao',
    #    'dificuldade_interna_blocos_instaveis',
    #    'dificuldade_interna_lances_verticais',
    #    'dificuldade_interna_quebra_corpo', 'dificuldade_interna_rastejamento',
    #    'dificuldade_interna_teto_baixo', 'feicao_interna_blocos_abatidos',
    #    'feicao_interna_canaliculos', 'feicao_interna_claraboias',
    #    'feicao_interna_conduto', 'arqueologia_paleontologia_ceramico',
    #    'arqueologia_paleontologia_litico', 'arqueologia_paleontologia_ossada',
    #    'arqueologia_paleontologia_vestigio_historico',
    #    'litotipo_prospeccao_rochas_carbonaticas',
    #    'litotipo_prospeccao_rochas_ferriferas',
    #    'litotipo_prospeccao_rochas_siliciosas', 'ocorrencia_guano_concentrado',
    #    'ocorrencia_guano_disperso', 'tipo_cavidade__abrigo',
    #    'tipo_cavidade__cavidade', 'tipo_cavidade__feicao_espeleologica']

        #treinamento carajas V4
    # columns = ['cavidade','target', 'nome_entrada', 'zona_afotica', 'raizes', 'projecao_horizontal',
    #    'desnivel_topografia', 'area', 'volume', 'animal_observado_anfibios',
    #    'animal_observado_aves', 'animal_observado_invertebrados',
    #    'animal_observado_mamiferos', 'animal_observado_morcegos',
    #    'animal_observado_ninhos', 'animal_observado_peixes',
    #    'animal_observado_repteis', 'tipo_espeleotema_coraloides',
    #    'tipo_espeleotema_crosta', 'tipo_espeleotema_escorrimentos',
    #    'tipo_espeleotema_estalactites', 'tipo_espeleotema_estalagmites',
    #    'tipo_espeleotema_pingente', 'tipo_espeleotema_travertinos',
    #    'feicao_hidrologica_cachoeira', 'feicao_hidrologica_condensacao',
    #    'feicao_hidrologica_drenagem', 'feicao_hidrologica_gotejamento',
    #    'feicao_hidrologica_lago', 'feicao_hidrologica_percolacao',
    #    'dificuldade_interna_blocos_instaveis',
    #    'dificuldade_interna_lances_verticais',
    #    'dificuldade_interna_quebra_corpo', 'dificuldade_interna_rastejamento',
    #    'dificuldade_interna_teto_baixo', 'feicao_interna_blocos_abatidos',
    #    'feicao_interna_canaliculos', 'feicao_interna_claraboias',
    #    'feicao_interna_conduto', 'arqueologia_paleontologia_ceramico',
    #    'arqueologia_paleontologia_litico', 'arqueologia_paleontologia_ossada',
    #    'arqueologia_paleontologia_vestigio_historico',
    #    'litotipo_prospeccao_rochas_carbonaticas',
    #    'litotipo_prospeccao_rochas_ferriferas',
    #    'litotipo_prospeccao_rochas_siliciosas', 'ocorrencia_guano_concentrado',
    #    'ocorrencia_guano_disperso', 'tipo_cavidade__abrigo',
    #    'tipo_cavidade__cavidade', 'tipo_cavidade__feicao_espeleologica']


    df = pd.read_excel(BytesIO(content))

    df = df.reindex(columns=columns, fill_value=0)



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