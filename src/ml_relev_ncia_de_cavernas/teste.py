from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


# ============================================================
# CONFIGURAÇÕES
# ============================================================

PASTA_ENTRADA = Path("../serra_norte_e_SRA")
PASTA_SAIDA = Path("../resultados_metricas_carajas")
PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

ARQUIVOS = {
    ("Consolidado SRA + Serra Norte", "V3"): "../datasets/df_SERRA_NORTE_e_SRA_FILTRADO_v3.xlsx",
    ("Consolidado SRA + Serra Norte", "V4"): "../datasets/df_SERRA_NORTE_e_SRA_FILTRADO_v4.xlsx",
}

THRESHOLDS = np.arange(0.50, 0.19, -0.05).round(2)

# Paleta visual inspirada nas cores da Vale
VALE_VERDE = "#009639"
VALE_VERDE_ESCURO = "#006A3D"
VALE_AMARELO = "#FFCD00"
VALE_VERDE_CLARO = "#72BF44"

CINZA = "#6D6E71"
CINZA_CLARO = "#D9D9D9"
BRANCO = "#FFFFFF"
VERMELHO = "#C00000"

CORES_VERSAO = {
    "V3": VALE_VERDE,
    "V4": VALE_AMARELO,
}

CORES_BASE = {
    "Carajas Consolidado": VALE_VERDE
}


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def validar_dataframe(df, nome_arquivo):
    colunas_necessarias = {"cavidade", "target", "score"}
    colunas_ausentes = colunas_necessarias - set(df.columns)

    if colunas_ausentes:
        raise ValueError(
            f"O arquivo {nome_arquivo} não contém as colunas: "
            f"{sorted(colunas_ausentes)}"
        )

    df = df.copy()

    df["cavidade"] = (
        df["cavidade"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    df["target"] = pd.to_numeric(
        df["target"],
        errors="coerce"
    )

    df["score"] = pd.to_numeric(
        df["score"],
        errors="coerce"
    )

    problemas = df[
        df[["target", "score"]].isna().any(axis=1)
    ]

    if not problemas.empty:
        print(
            f"\nAtenção: {len(problemas)} linha(s) inválida(s) em "
            f"{nome_arquivo}. Elas serão removidas."
        )

    df = df.dropna(
        subset=["cavidade", "target", "score"]
    ).copy()

    df["target"] = df["target"].astype(int)

    targets_invalidos = set(df["target"].unique()) - {0, 1}

    if targets_invalidos:
        raise ValueError(
            f"Targets inválidos em {nome_arquivo}: "
            f"{targets_invalidos}"
        )

    if not df["score"].between(0, 1).all():
        raise ValueError(
            f"Existem scores fora do intervalo 0–1 em {nome_arquivo}."
        )

    return df


def calcular_metricas(df, base, versao, threshold):
    y_true = df["target"].to_numpy()

    y_pred = (
        df["score"].to_numpy() >= threshold
    ).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        y_pred,
        labels=[0, 1]
    ).ravel()

    accuracy = accuracy_score(y_true, y_pred)

    precision = precision_score(
        y_true,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_true,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_true,
        y_pred,
        zero_division=0
    )

    especificidade = (
        tn / (tn + fp)
        if (tn + fp) > 0
        else np.nan
    )

    taxa_falso_positivo = (
        fp / (fp + tn)
        if (fp + tn) > 0
        else np.nan
    )

    taxa_falso_negativo = (
        fn / (fn + tp)
        if (fn + tp) > 0
        else np.nan
    )

    valor_preditivo_negativo = (
        tn / (tn + fn)
        if (tn + fn) > 0
        else np.nan
    )

    maximas_reais = int((y_true == 1).sum())
    nao_maximas_reais = int((y_true == 0).sum())
    maximas_previstas = int((y_pred == 1).sum())

    diferenca_maximas = maximas_previstas - maximas_reais

    percentual_maximas_capturadas = (
        tp / maximas_reais
        if maximas_reais > 0
        else np.nan
    )

    percentual_excesso_indicacoes = (
        max(diferenca_maximas, 0) / maximas_reais
        if maximas_reais > 0
        else np.nan
    )

    return {
        "base": base,
        "versao": versao,
        "threshold": threshold,

        "quantidade_registros": len(df),
        "maximas_reais": maximas_reais,
        "nao_maximas_reais": nao_maximas_reais,
        "maximas_previstas": maximas_previstas,
        "diferenca_maximas": diferenca_maximas,

        "verdadeiros_positivos": tp,
        "falsos_positivos": fp,
        "verdadeiros_negativos": tn,
        "falsos_negativos": fn,

        "recall": recall,
        "precision": precision,
        "f1_score": f1,
        "accuracy": accuracy,
        "especificidade": especificidade,
        "valor_preditivo_negativo": valor_preditivo_negativo,

        "taxa_falso_positivo": taxa_falso_positivo,
        "taxa_falso_negativo": taxa_falso_negativo,

        "percentual_maximas_capturadas":
            percentual_maximas_capturadas,

        "percentual_excesso_indicacoes":
            percentual_excesso_indicacoes,
    }


def configurar_grafico(titulo, ylabel):
    plt.title(
        titulo,
        fontsize=14,
        fontweight="bold",
        color=VALE_VERDE_ESCURO,
        pad=15
    )

    plt.xlabel("Threshold")
    plt.ylabel(ylabel)

    plt.xticks(THRESHOLDS)

    plt.grid(
        axis="y",
        linestyle="--",
        alpha=0.30
    )

    plt.gca().invert_xaxis()

    plt.legend(
        frameon=False,
        loc="best"
    )

    plt.tight_layout()


# ============================================================
# LEITURA E CONSOLIDAÇÃO DAS BASES
# ============================================================


# Consolidação

v3_unificado = pd.read_excel("../datasets/df_SERRA_NORTE_e_SRA_FILTRADO_v3.xlsx")

v4_unificado = pd.read_excel("../datasets/df_SERRA_NORTE_e_SRA_FILTRADO_v4.xlsx")

dados = {
    ("Base completa - SRA + Serra Norte ", "V3"): v3_unificado,
    ("Base completa - SRA + Serra Norte ", "V4"): v4_unificado
}

for (base, versao), df in dados.items():

    print(
        f"{base} | {versao}: "
        f"{len(df)} registros | "
        f"{df['target'].sum()} máximas"
    )

# ============================================================
# CÁLCULO DAS MÉTRICAS
# ============================================================

resultados = []

for (base, versao), df in dados.items():

    for threshold in THRESHOLDS:

        metricas = calcular_metricas(
            df=df,
            base=base,
            versao=versao,
            threshold=threshold
        )

        resultados.append(metricas)


df_metricas = pd.DataFrame(resultados)

df_metricas = df_metricas.sort_values(
    by=["base", "versao", "threshold"],
    ascending=[True, True, False]
).reset_index(drop=True)


# ============================================================
# RESUMO DAS BASES
# ============================================================

resumo_bases = []

for (base, versao), df in dados.items():

    resumo_bases.append({
        "base": base,
        "versao": versao,
        "quantidade_registros": len(df),
        "maximas_reais": int(df["target"].sum()),
        "nao_maximas_reais": int(
            (df["target"] == 0).sum()
        ),
        "percentual_maximas_reais":
            df["target"].mean()
    })

df_resumo_bases = pd.DataFrame(resumo_bases)


# ============================================================
# ESCOLHA AUTOMÁTICA DO MELHOR THRESHOLD
# ============================================================

# Critério:
# 1. prioriza thresholds com recall >= 80%
# 2. dentre eles, escolhe o maior F1
# 3. em empate, escolhe a maior precision
# 4. depois, o threshold mais alto

melhores_thresholds = []

for (base, versao), grupo in df_metricas.groupby(
    ["base", "versao"]
):

    candidatos = grupo[
        grupo["recall"] >= 0.80
    ].copy()

    if candidatos.empty:
        candidatos = grupo.copy()

    melhor = candidatos.sort_values(
        by=[
            "f1_score",
            "precision",
            "threshold"
        ],
        ascending=[
            False,
            False,
            False
        ]
    ).iloc[0]

    melhores_thresholds.append(melhor)

df_melhores_thresholds = pd.DataFrame(
    melhores_thresholds
).reset_index(drop=True)


# ============================================================
# DETALHAMENTO POR CAVIDADE E THRESHOLD
# ============================================================

detalhes = []

for (base, versao), df in dados.items():

    for threshold in THRESHOLDS:

        temporario = df[
            ["cavidade", "target", "score"]
        ].copy()

        temporario["base"] = base
        temporario["versao"] = versao
        temporario["threshold"] = threshold

        temporario["target_previsto"] = (
            temporario["score"] >= threshold
        ).astype(int)

        temporario["resultado"] = np.select(
            [
                (temporario["target"] == 1)
                & (temporario["target_previsto"] == 1),

                (temporario["target"] == 0)
                & (temporario["target_previsto"] == 1),

                (temporario["target"] == 0)
                & (temporario["target_previsto"] == 0),

                (temporario["target"] == 1)
                & (temporario["target_previsto"] == 0),
            ],
            [
                "Verdadeiro positivo",
                "Falso positivo",
                "Verdadeiro negativo",
                "Falso negativo",
            ],
            default="Não identificado"
        )

        detalhes.append(temporario)

df_detalhes = pd.concat(
    detalhes,
    ignore_index=True
)


# ============================================================
# GRÁFICO 1: MÉTRICAS POR THRESHOLD
# ============================================================

for base in df_metricas["base"].unique():

    filtro_base = df_metricas[
        df_metricas["base"] == base
    ]

    fig, axes = plt.subplots(
        nrows=2,
        ncols=2,
        figsize=(14, 9)
    )

    metricas_grafico = [
        ("recall", "Recall"),
        ("precision", "Precision"),
        ("f1_score", "F1-score"),
        ("accuracy", "Accuracy"),
    ]

    for ax, (coluna, titulo) in zip(
        axes.flatten(),
        metricas_grafico
    ):

        for versao in ["V3", "V4"]:

            dados_versao = filtro_base[
                filtro_base["versao"] == versao
            ].sort_values("threshold")

            ax.plot(
                dados_versao["threshold"],
                dados_versao[coluna],
                marker="o",
                linewidth=2.5,
                markersize=6,
                label=versao,
                color=CORES_VERSAO[versao]
            )

        ax.set_title(
            titulo,
            fontweight="bold",
            color=VALE_VERDE_ESCURO
        )

        ax.set_xlabel("Threshold")
        ax.set_ylabel(titulo)
        ax.set_xticks(THRESHOLDS)
        ax.set_ylim(0, 1.05)
        ax.invert_xaxis()

        ax.grid(
            axis="y",
            linestyle="--",
            alpha=0.30
        )

        ax.legend(frameon=False)

    fig.suptitle(
        f"Desempenho por threshold – {base}",
        fontsize=16,
        fontweight="bold",
        color=VALE_VERDE_ESCURO
    )

    plt.tight_layout()

    nome_base = base.lower().replace(" ", "_")

    plt.savefig(
        PASTA_SAIDA
        / f"metricas_threshold_{nome_base}.png",
        dpi=300,
        bbox_inches="tight",
        facecolor=BRANCO
    )

    plt.close()


# ============================================================
# GRÁFICO 2: MÁXIMAS REAIS × PREVISTAS
# ============================================================

for base in df_metricas["base"].unique():

    filtro_base = df_metricas[
        df_metricas["base"] == base
    ].copy()

    maximas_reais = int(
        filtro_base["maximas_reais"].iloc[0]
    )

    plt.figure(figsize=(11, 6))

    plt.axhline(
        y=maximas_reais,
        color=VALE_VERDE_ESCURO,
        linestyle="--",
        linewidth=2.5,
        label=f"Máximas reais: {maximas_reais}"
    )

    for versao in ["V3", "V4"]:

        dados_versao = filtro_base[
            filtro_base["versao"] == versao
        ].sort_values("threshold")

        plt.plot(
            dados_versao["threshold"],
            dados_versao["maximas_previstas"],
            marker="o",
            linewidth=2.5,
            label=f"Máximas previstas – {versao}",
            color=CORES_VERSAO[versao]
        )

    configurar_grafico(
        titulo=f"Máximas reais × previstas – {base}",
        ylabel="Quantidade de cavidades"
    )

    plt.savefig(
        PASTA_SAIDA
        / (
            "maximas_reais_previstas_"
            + base.lower().replace(" ", "_")
            + ".png"
        ),
        dpi=300,
        bbox_inches="tight",
        facecolor=BRANCO
    )

    plt.close()


# ============================================================
# GRÁFICO 3: TP, FP E FN POR THRESHOLD
# ============================================================

for base in df_metricas["base"].unique():

    for versao in ["V3", "V4"]:

        filtro = df_metricas[
            (df_metricas["base"] == base)
            & (df_metricas["versao"] == versao)
        ].sort_values("threshold")

        plt.figure(figsize=(11, 6))

        plt.plot(
            filtro["threshold"],
            filtro["verdadeiros_positivos"],
            marker="o",
            linewidth=2.5,
            label="Máximas identificadas corretamente (TP)",
            color=VALE_VERDE
        )

        plt.plot(
            filtro["threshold"],
            filtro["falsos_positivos"],
            marker="o",
            linewidth=2.5,
            label="Não máximas classificadas como máximas (FP)",
            color=VALE_AMARELO
        )

        plt.plot(
            filtro["threshold"],
            filtro["falsos_negativos"],
            marker="o",
            linewidth=2.5,
            label="Máximas não identificadas (FN)",
            color=VERMELHO
        )

        configurar_grafico(
            titulo=(
                f"Acertos e erros na classe Máxima – "
                f"{base} | {versao}"
            ),
            ylabel="Quantidade de cavidades"
        )

        nome_base = base.lower().replace(" ", "_")

        plt.savefig(
            PASTA_SAIDA
            / f"tp_fp_fn_{nome_base}_{versao.lower()}.png",
            dpi=300,
            bbox_inches="tight",
            facecolor=BRANCO
        )

        plt.close()


# ============================================================
# GRÁFICO 4: RECALL × PRECISION
# ============================================================

for base in df_metricas["base"].unique():

    plt.figure(figsize=(10, 7))

    for versao in ["V3", "V4"]:

        filtro = df_metricas[
            (df_metricas["base"] == base)
            & (df_metricas["versao"] == versao)
        ].sort_values("threshold")

        plt.plot(
            filtro["recall"],
            filtro["precision"],
            marker="o",
            linewidth=2.5,
            color=CORES_VERSAO[versao],
            label=versao
        )

        for _, linha in filtro.iterrows():

            plt.annotate(
                f"{linha['threshold']:.2f}",
                (
                    linha["recall"],
                    linha["precision"]
                ),
                xytext=(5, 5),
                textcoords="offset points",
                fontsize=8
            )

    plt.title(
        f"Equilíbrio entre recall e precision – {base}",
        fontsize=14,
        fontweight="bold",
        color=VALE_VERDE_ESCURO,
        pad=15
    )

    plt.xlabel("Recall das máximas")
    plt.ylabel("Precision das máximas")

    plt.xlim(0, 1.05)
    plt.ylim(0, 1.05)

    plt.grid(
        linestyle="--",
        alpha=0.30
    )

    plt.legend(frameon=False)
    plt.tight_layout()

    plt.savefig(
        PASTA_SAIDA
        / (
            "recall_precision_"
            + base.lower().replace(" ", "_")
            + ".png"
        ),
        dpi=300,
        bbox_inches="tight",
        facecolor=BRANCO
    )

    plt.close()


# ============================================================
# GRÁFICO 5: COMPARAÇÃO V3 × V4 POR BASE E THRESHOLD
# ============================================================

for metrica, titulo in [
    ("recall", "Recall"),
    ("precision", "Precision"),
    ("f1_score", "F1-score"),
    ("accuracy", "Accuracy"),
]:

    plt.figure(figsize=(10, 6))

    combinacoes = [
    ("Carajas Consolidado", "V3", VALE_VERDE, "-", "o"),
    ("Carajas Consolidado", "V4", VALE_AMARELO, "-", "s"),
]

    for base, versao, cor, estilo, marcador in combinacoes:
    
        filtro = df_metricas[
            (df_metricas["base"] == base)
            & (df_metricas["versao"] == versao)
        ].sort_values("threshold")
    
        plt.plot(
            filtro["threshold"],
            filtro[metrica],
            marker=marcador,
            markersize=8,
            linewidth=3,
            linestyle=estilo,
            color=cor,
            label=versao
        )
        configurar_grafico(
           titulo=f"{titulo} por threshold",
           ylabel=titulo
       )

        plt.ylim(0, 1.05)

        plt.savefig(
           PASTA_SAIDA
           / f"comparacao_geral_{metrica}.png",
           dpi=300,
           bbox_inches="tight",
           facecolor=BRANCO
       )

        plt.close()
       


# ============================================================
# GRÁFICO 6: HEATMAP DE F1
# ============================================================

for base in df_metricas["base"].unique():

    pivot = (
        df_metricas[
            df_metricas["base"] == base
        ]
        .pivot(
            index="versao",
            columns="threshold",
            values="f1_score"
        )
        .reindex(columns=THRESHOLDS)
    )

    fig, ax = plt.subplots(figsize=(11, 3.5))

    imagem = ax.imshow(
        pivot.values,
        cmap="YlGn",
        aspect="auto",
        vmin=0,
        vmax=1
    )

    ax.set_xticks(
        range(len(pivot.columns))
    )

    ax.set_xticklabels(
        [f"{valor:.2f}" for valor in pivot.columns]
    )

    ax.set_yticks(
        range(len(pivot.index))
    )

    ax.set_yticklabels(
        pivot.index
    )

    ax.set_xlabel("Threshold")
    ax.set_ylabel("Versão")

    ax.set_title(
        f"F1-score por threshold – {base}",
        fontweight="bold",
        color=VALE_VERDE_ESCURO
    )

    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):

            valor = pivot.iloc[i, j]

            ax.text(
                j,
                i,
                f"{valor:.2f}",
                ha="center",
                va="center",
                color=(
                    BRANCO
                    if valor >= 0.60
                    else "black"
                ),
                fontweight="bold"
            )

    fig.colorbar(
        imagem,
        ax=ax,
        label="F1-score"
    )

    plt.tight_layout()

    plt.savefig(
        PASTA_SAIDA
        / (
            "heatmap_f1_"
            + base.lower().replace(" ", "_")
            + ".png"
        ),
        dpi=300,
        bbox_inches="tight",
        facecolor=BRANCO
    )

    plt.close()


# ============================================================
# EXPORTAÇÃO PARA EXCEL
# ============================================================

arquivo_excel = (
    PASTA_SAIDA
    / "avaliacao_modelo_carajas_SRA_SRN_V3_V4.xlsx"
)

with pd.ExcelWriter(
    arquivo_excel,
    engine="openpyxl"
) as writer:

    df_resumo_bases.to_excel(
        writer,
        sheet_name="Resumo_bases",
        index=False
    )

    df_metricas.to_excel(
        writer,
        sheet_name="Metricas_threshold",
        index=False
    )

    df_melhores_thresholds.to_excel(
        writer,
        sheet_name="Melhores_thresholds",
        index=False
    )

    df_detalhes.to_excel(
        writer,
        sheet_name="Detalhamento_cavidades",
        index=False
    )

    for (base, versao), df in dados.items():

        nome_aba = (
            f"{base}_{versao}"
            .replace(" ", "_")[:31]
        )

        df.to_excel(
            writer,
            sheet_name=nome_aba,
            index=False
        )