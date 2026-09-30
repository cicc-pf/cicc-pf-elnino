import os
import requests
from datetime import datetime

from cache_utils import salvar_cache, ler_cache


CODIGO_PF = "A126"
CODIGO_MANAUS = "A101"

LAT_PF = -2.03
LON_PF = -60.03

URL_INMET = "https://apitempo.inmet.gov.br/estacao/dados"
URL_OPEN_METEO = "https://api.open-meteo.com/v1/forecast"


def _direcao_vento(graus):
    if graus is None:
        return "-"
    direcoes = ["N", "NE", "L", "SE", "S", "SO", "O", "NO"]
    indice = int((graus + 22.5) / 45) % 8
    return direcoes[indice]


def _classificar_umidade(umidade):
    if umidade >= 80:
        return "Muito Alta", (0.13, 0.59, 0.95, 1)
    elif umidade >= 60:
        return "Adequada", (0.13, 0.71, 0.43, 1)
    elif umidade >= 40:
        return "Baixa", (0.95, 0.61, 0.07, 1)
    else:
        return "Critica", (0.91, 0.30, 0.24, 1)


def _classificar_temperatura(temp):
    if temp >= 38:
        return "Extrema", (0.72, 0.11, 0.11, 1)
    elif temp >= 35:
        return "Muito Alta", (0.91, 0.30, 0.24, 1)
    elif temp >= 30:
        return "Alta", (0.95, 0.61, 0.07, 1)
    elif temp >= 20:
        return "Adequada", (0.13, 0.71, 0.43, 1)
    else:
        return "Baixa", (0.13, 0.59, 0.95, 1)


def _buscar_open_meteo():
    try:
        params = {
            "latitude": LAT_PF,
            "longitude": LON_PF,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,precipitation",
            "hourly": "precipitation",
            "past_days": 7,
            "timezone": "America/Manaus",
        }
        r = requests.get(URL_OPEN_METEO, params=params, timeout=20)
        r.raise_for_status()
        d = r.json()

        atual = d.get("current", {})
        temp = atual.get("temperature_2m")
        umid = atual.get("relative_humidity_2m")
        vento = atual.get("wind_speed_10m")
        direcao_graus = atual.get("wind_direction_10m")
        hora = atual.get("time", "")

        hourly = d.get("hourly", {})
        chuva_7d = 0.0
        if hourly.get("precipitation"):
            valores = [v for v in hourly["precipitation"] if v is not None]
            chuva_7d = round(sum(valores), 1)

        direcao = _direcao_vento(direcao_graus)
        _, cor_temp = _classificar_temperatura(temp)
        texto_umid, cor_umid = _classificar_umidade(umid)

        return {
            "temperatura": temp,
            "cor_temperatura": cor_temp,
            "umidade": umid,
            "texto_umidade": texto_umid,
            "cor_umidade": cor_umid,
            "vento": vento,
            "direcao": direcao,
            "chuva_7d": chuva_7d,
            "hora": hora,
            "fonte": "Open-Meteo",
            "erro": None,
        }
    except Exception as e:
        return {"erro": str(e), "fonte": "Open-Meteo"}


def _buscar_inmet():
    token = os.environ.get("INMET_TOKEN")
    if not token:
        return None

    try:
        hoje = datetime.now().strftime("%Y-%m-%d")
        url = URL_INMET + "/" + hoje + "/" + CODIGO_PF
        headers = {"Authorization": "Bearer " + token}
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        dados = r.json()

        if not dados:
            return None

        ultima = dados[-1]
        temp = float(ultima.get("TEM_INS", 0) or 0)
        umid = float(ultima.get("UMD_INS", 0) or 0)
        vento = float(ultima.get("VEN_VEL", 0) or 0)
        direcao_graus = float(ultima.get("VEN_DIR", 0) or 0)
        chuva = float(ultima.get("CHUVA", 0) or 0)
        hora = ultima.get("DT_MEDICAO", "")

        _, cor_temp = _classificar_temperatura(temp)
        texto_umid, cor_umid = _classificar_umidade(umid)
        direcao = _direcao_vento(direcao_graus)

        return {
            "temperatura": temp,
            "cor_temperatura": cor_temp,
            "umidade": umid,
            "texto_umidade": texto_umid,
            "cor_umidade": cor_umid,
            "vento": vento,
            "direcao": direcao,
            "chuva_7d": chuva,
            "hora": hora,
            "fonte": "INMET A126",
            "erro": None,
        }
    except Exception:
        return None


def buscar_dados_painel():
    dados = _buscar_inmet()
    if dados and not dados.get("erro"):
        salvar_cache("painel", dados)
        return dados

    dados = _buscar_open_meteo()
    if dados and not dados.get("erro"):
        salvar_cache("painel", dados)
        return dados

    cache, timestamp = ler_cache("painel")
    if cache:
        cache["fonte"] = "Cache offline (" + str(timestamp) + ")"
        return cache

    return {"erro": "Sem conexao com APIs e sem cache local", "fonte": "Offline"}


if __name__ == "__main__":
    r = buscar_dados_painel()
    if r.get("erro"):
        print("Erro:", r["erro"])
    else:
        print("Fonte:", r["fonte"])
        print("Temperatura:", r["temperatura"], "C")
        print("Umidade:", r["umidade"], "%")
        print("Vento:", r["vento"], "km/h direcao", r["direcao"])
        print("Chuva 7d:", r["chuva_7d"], "mm")
