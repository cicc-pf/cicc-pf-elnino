import requests

from cache_utils import salvar_cache, ler_cache


URL_NOAA = "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/detrend.nino34.ascii.txt"


def _classificar_anomalia(valor):
    if valor >= 2.0:
        return "El Nino Muito Forte", (0.72, 0.11, 0.11, 1)
    elif valor >= 1.5:
        return "El Nino Forte", (0.91, 0.30, 0.24, 1)
    elif valor >= 1.0:
        return "El Nino Moderado", (0.95, 0.61, 0.07, 1)
    elif valor >= 0.5:
        return "El Nino Fraco", (0.98, 0.80, 0.18, 1)
    elif valor > -0.5:
        return "Neutro", (0.13, 0.71, 0.43, 1)
    elif valor > -1.0:
        return "La Nina Fraco", (0.53, 0.85, 0.92, 1)
    elif valor > -1.5:
        return "La Nina Moderado", (0.13, 0.59, 0.95, 1)
    elif valor > -2.0:
        return "La Nina Forte", (0.10, 0.40, 0.78, 1)
    else:
        return "La Nina Muito Forte", (0.06, 0.22, 0.55, 1)


def _tendencia(valor_atual, valor_anterior):
    diferenca = valor_atual - valor_anterior
    if diferenca > 0.15:
        return "Subindo", (0.91, 0.30, 0.24, 1)
    elif diferenca < -0.15:
        return "Caindo", (0.13, 0.59, 0.95, 1)
    else:
        return "Estavel", (0.6, 0.6, 0.6, 1)


def buscar_nino34():
    try:
        resposta = requests.get(URL_NOAA, timeout=20)
        resposta.raise_for_status()
        texto = resposta.text
    except Exception as e:
        cache, timestamp = ler_cache("enso")
        if cache:
            cache["fonte"] = "Cache offline (" + str(timestamp) + ")"
            cache["erro"] = None
            return cache
        return {
            "valor": None, "ano": None, "mes": None,
            "classificacao": "Erro", "fase": "Erro ao buscar dados",
            "cor": (0.6, 0.6, 0.6, 1),
            "tendencia": "-", "cor_tendencia": (0.6, 0.6, 0.6, 1),
            "variacao": None, "historico": [],
            "erro": str(e),
        }

    linhas = [l for l in texto.splitlines() if l.strip()]

    dados = []
    for linha in linhas:
        partes = linha.split()
        if len(partes) >= 5:
            try:
                ano = int(partes[0])
                mes = int(partes[1])
                anomalia = float(partes[4])
                dados.append({"ano": ano, "mes": mes, "valor": anomalia})
            except ValueError:
                continue

    if len(dados) < 2:
        cache, timestamp = ler_cache("enso")
        if cache:
            cache["fonte"] = "Cache offline (" + str(timestamp) + ")"
            cache["erro"] = None
            return cache
        return {
            "valor": None, "ano": None, "mes": None,
            "classificacao": "Dados insuficientes", "fase": "-",
            "cor": (0.6, 0.6, 0.6, 1),
            "tendencia": "-", "cor_tendencia": (0.6, 0.6, 0.6, 1),
            "variacao": None, "historico": [],
            "erro": "Nenhuma linha de dados valida",
        }

    atual = dados[-1]
    anterior = dados[-2]

    classificacao, cor = _classificar_anomalia(atual["valor"])
    tendencia, cor_tendencia = _tendencia(atual["valor"], anterior["valor"])
    variacao = round(atual["valor"] - anterior["valor"], 2)

    if atual["valor"] >= 0.5:
        fase = "El Nino"
    elif atual["valor"] <= -0.5:
        fase = "La Nina"
    else:
        fase = "Neutro"

    resultado = {
        "valor": atual["valor"],
        "ano": atual["ano"],
        "mes": atual["mes"],
        "classificacao": classificacao,
        "fase": fase,
        "cor": cor,
        "tendencia": tendencia,
        "cor_tendencia": cor_tendencia,
        "variacao": variacao,
        "historico": dados[-6:],
        "erro": None,
    }
    salvar_cache("enso", resultado)
    return resultado


if __name__ == "__main__":
    r = buscar_nino34()
    print("Valor:", r["valor"])
    print("Classificacao:", r["classificacao"])
    print("Tendencia:", r["tendencia"])
