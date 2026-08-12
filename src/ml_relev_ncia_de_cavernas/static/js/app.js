function abrirAba(nome){

    document
        .querySelectorAll(".content")
        .forEach(div => div.classList.remove("active"))

    document
        .querySelectorAll(".tab")
        .forEach(btn => btn.classList.remove("active"))

    document
        .getElementById("planilhaResultado")
        .style.display = "none"

    document
        .getElementById(nome)
        .classList.add("active")

    event.target.classList.add("active")
}


function check(id) {
    return document.getElementById(id).checked ? 1 : 0;
}

function num(id) {
    return Number(document.getElementById(id).value || 0);
}
async function avaliarIndividual() {

    const payload = {

        nome_entrada: num("nome_entrada"),
        desenv_aproximado: num("desenv_aproximado"),
        desnivel_propeccao: num("desnivel_propeccao"),

        zona_afotica: check("zona_afotica"),
        raizes: check("raizes"),

        animal_observado_anfibios: check("animal_observado_anfibios"),
        animal_observado_aves: check("animal_observado_aves"),
        animal_observado_invertebrados: check("animal_observado_invertebrados"),
        animal_observado_mamiferos: check("animal_observado_mamiferos"),
        animal_observado_morcegos: check("animal_observado_morcegos"),
        animal_observado_ninhos: check("animal_observado_ninhos"),
        animal_observado_peixes: check("animal_observado_peixes"),
        animal_observado_repteis: check("animal_observado_repteis"),

        tipo_espeleotema_coraloides: check("tipo_espeleotema_coraloides"),
        tipo_espeleotema_crosta: check("tipo_espeleotema_crosta"),
        tipo_espeleotema_escorrimentos: check("tipo_espeleotema_escorrimentos"),
        tipo_espeleotema_estalactites: check("tipo_espeleotema_estalactites"),
        tipo_espeleotema_estalagmites: check("tipo_espeleotema_estalagmites"),
        tipo_espeleotema_pingente: check("tipo_espeleotema_pingente"),
        tipo_espeleotema_travertinos: check("tipo_espeleotema_travertinos"),

        feicao_hidrologica_cachoeira: check("feicao_hidrologica_cachoeira"),
        feicao_hidrologica_condensacao: check("feicao_hidrologica_condensacao"),
        feicao_hidrologica_drenagem: check("feicao_hidrologica_drenagem"),
        feicao_hidrologica_gotejamento: check("feicao_hidrologica_gotejamento"),
        feicao_hidrologica_lago: check("feicao_hidrologica_lago"),
        feicao_hidrologica_percolacao: check("feicao_hidrologica_percolacao"),

        dificuldade_interna_blocos_instaveis: check("dificuldade_interna_blocos_instaveis"),
        dificuldade_interna_lances_verticais: check("dificuldade_interna_lances_verticais"),
        dificuldade_interna_quebra_corpo: check("dificuldade_interna_quebra_corpo"),
        dificuldade_interna_rastejamento: check("dificuldade_interna_rastejamento"),
        dificuldade_interna_teto_baixo: check("dificuldade_interna_teto_baixo"),

        feicao_interna_blocos_abatidos: check("feicao_interna_blocos_abatidos"),
        feicao_interna_canaliculos: check("feicao_interna_canaliculos"),
        feicao_interna_claraboias: check("feicao_interna_claraboias"),
        feicao_interna_conduto: check("feicao_interna_conduto"),

        arqueologia_paleontologia_ceramico: check("arqueologia_paleontologia_ceramico"),
        arqueologia_paleontologia_litico: check("arqueologia_paleontologia_litico"),
        arqueologia_paleontologia_ossada: check("arqueologia_paleontologia_ossada"),
        arqueologia_paleontologia_vestigio_historico: check("arqueologia_paleontologia_vestigio_historico"),

        litotipo_prospeccao_granito_gnaisse: check("litotipo_prospeccao_granito_gnaisse"),
        litotipo_prospeccao_rochas_carbonaticas: check("litotipo_prospeccao_rochas_carbonaticas"),
        litotipo_prospeccao_rochas_ferriferas: check("litotipo_prospeccao_rochas_ferriferas"),
        litotipo_prospeccao_rochas_peliticas: check("litotipo_prospeccao_rochas_peliticas"),
        litotipo_prospeccao_rochas_siliciosas: check("litotipo_prospeccao_rochas_siliciosas"),

        ocorrencia_guano_concentrado: check("ocorrencia_guano_concentrado"),
        ocorrencia_guano_disperso: check("ocorrencia_guano_disperso"),

        tipo_cavidade__abrigo: check("tipo_cavidade__abrigo"),
        tipo_cavidade__cavidade: check("tipo_cavidade__cavidade"),
        tipo_cavidade__feicao_espeleologica: check("tipo_cavidade__feicao_espeleologica")
    };

    try {

        const response = await fetch("/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const resultado = await response.json();

        const score = Math.round(resultado.score * 100);

        document
            .getElementById("resultado")
            .style.display = "block";

        document
            .getElementById("score")
            .innerHTML = score + "%";

        document
            .getElementById("classe")
            .innerHTML =
                score >= 50
                    ? "ALTO POTENCIAL"
                    : "BAIXO POTENCIAL";

    } catch (erro) {

        console.error(erro);

        alert(
            "Erro ao comunicar com a API."
        );

    }
}

async function processarPlanilha(){
    const arquivo = document.getElementById("arquivoExcel").files[0];
    
    document
        .getElementById("planilhaResultado")
        .style.display = "none"

    if(!arquivo){
        alert("Selecione uma planilha!")
        return
    }

    const formData = new FormData()

    formData.append(
        "file",
        arquivo
    )

    const response = await fetch(
        "/predict-batch",
        {
            method: "POST",
            body: formData
        }
    )

    const blob = await response.blob();

    const url =
    window.URL.createObjectURL(blob);
    
    const btn =
    document.getElementById(
        "btnDownloadResultado"
    );

    btn.onclick = () => { 
        const a =
            document.createElement("a");

        a.href = url;
        a.download =
            "resultado.xlsx";

        a.click();
    };

    console.log(response)

    document
        .getElementById("planilhaResultado")
        .style.display = "block"

}

async function processarTreinamento(){
    const arquivo = document.getElementById("arquivoTreinamento").files[0];
    
    if(!arquivo){
        alert("Selecione uma planilha!")
        return
    }

    const formData = new FormData()

    formData.append(
        "file",
        arquivo
    )

    const response = await fetch(
        "/predict-batch",
        {
            method: "POST",
            body: formData
        }
    )

    const blob = await response.blob();

    const url =
    window.URL.createObjectURL(blob);
    
    const btn =
    document.getElementById(
        "btnDownloadResultado"
    );

    btn.onclick = () => { 
        const a =
            document.createElement("a");

        a.href = url;
        a.download =
            "resultado.xlsx";

        a.click();
    };

    console.log(response)

    document
        .getElementById("planilhaResultado")
        .style.display = "block"

}