import os
import requests
from datetime import datetime, timedelta


# Endpoint da API HidroWebService
URL_API = "https://www.ana.gov.br/hidrowebservice/EstacoesTelemetricas"

# Estacao Balbina P-8 no Rio Uatuma (Presidente Figueiredo)
CODIGO_ESTACAO = "16080000"
NOME_ESTACAO = "Balbina P-8"
RIO = "Uatuma"

CACHE_DIR = os.path.expanduser("~/.cache/cicc_elnino")


def _garantir_cache_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)


def _classificar_nivel(nivel_m, media_hist_m=None):
    """Classifica o nivel do rio em relacao a media historica."""
    if media_hist_m is None:
        return "Sem referencia", (0.6, 0.6, 0.6, 1)

    diferenca = nivel_m - media_hist_m

    if diferenca >= 0.5:
        return "Muito Alto", (0.13, 0.59, 0.95, 1)
    elif diferenca >= 0.2:
        return "Alto", (0.13, 0.71, 0.43, 1)
    elif diferenca > -0.2:
        return "Normal", (0.6, 0.6, 0.6, 1)
    elif diferenca > -0.5:
        return "Baixo", (0.95, 0.61, 0.07, 1)
    else:
        return "Muito Baixo", (0.91, 0.30, 0.24, 1)


def buscar_nivel_balbina():
    """
    Busca o nivel atual do Rio Uatuma na estacao Balbina P-8.
    """
    # Por enquanto, retorna dados estaticos de referencia enquanto
    # aguardamos a liberacao do acesso a API da ANA.
    return {
        "nivel_m": 47.3,
        "nivel_cm": 4730,
        "data": "2026-09-29",
        "hora": "14:00",
        "estacao": NOME_ESTACAO,
        "codigo": CODIGO_ESTACAO,
        "rio": RIO,
        "media_historica": 47.0,
        "classificacao": "Alto",
        "cor": (0.13, 0.71, 0.43, 1),
        "amplitude": 1.69,
        "pico_cheia": "Julho",
        "pico_seca": "Fevereiro",
        "erro": None,
        "nota": "Aguardando liberacao de acesso a API HidroWebService da ANA.",
    }


if __name__ == "__main__":
    r = buscar_nivel_balbina()
    print("Estacao:", r["estacao"], "(", r["codigo"], ")")
    print("Rio:", r["rio"])
    print("Nivel:", r["nivel_m"], "m  (", r["nivel_cm"], "cm )")
    print("Data:", r["data"], r["hora"])
    print("Classificacao:", r["classificacao"])
    print("Amplitude historica:", r["amplitude"], "m")
    print("Pico de cheia:", r["pico_cheia"])
    print("Pico de seca:", r["pico_seca"])
    if r["nota"]:
        print("Nota:", r["nota"])
