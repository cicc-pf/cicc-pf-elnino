import csv
import io
import os
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

from cache_utils import salvar_cache, ler_cache


URL_BASE = "https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/diario/Brasil"
CACHE_DIR = os.path.expanduser("~/.cache/cicc_elnino")
MUNICIPIO_ALVO = "PRESIDENTE FIGUEIREDO"
ESTADO_ALVO = "AMAZONAS"
DIAS_JANELA = 7


def _garantir_cache_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)


def _baixar_arquivo_dia(dia, tentativas=3):
    _garantir_cache_dir()
    nome = "focos_diario_br_" + dia.strftime("%Y%m%d") + ".csv"
    caminho_cache = os.path.join(CACHE_DIR, nome)

    if os.path.exists(caminho_cache):
        with open(caminho_cache, "r", encoding="utf-8") as f:
            return f.read()

    url = URL_BASE + "/" + nome

    for tentativa in range(tentativas):
        try:
            resposta = requests.get(url, timeout=90)
            resposta.raise_for_status()
            texto = resposta.text

            with open(caminho_cache, "w", encoding="utf-8") as f:
                f.write(texto)

            return texto
        except Exception:
            if tentativa < tentativas - 1:
                time.sleep(2 * (tentativa + 1))

    return None


def _filtrar_focos(texto_csv, dia):
    focos = []
    if not texto_csv:
        return focos

    leitor = csv.DictReader(io.StringIO(texto_csv))
    for linha in leitor:
        municipio = (linha.get("municipio") or "").strip().upper()
        estado = (linha.get("estado") or "").strip().upper()

        if municipio == MUNICIPIO_ALVO and estado == ESTADO_ALVO:
            try:
                risco = float(linha.get("risco_fogo") or 0)
            except (ValueError, TypeError):
                risco = 0.0
            try:
                frp = float(linha.get("frp") or 0)
            except (ValueError, TypeError):
                frp = 0.0
            try:
                dias_sem_chuva = int(linha.get("numero_dias_sem_chuva") or 0)
            except (ValueError, TypeError):
                dias_sem_chuva = 0

            focos.append({
                "data": dia.strftime("%Y-%m-%d"),
                "data_hora_gmt": linha.get("data_hora_gmt", ""),
                "satelite": linha.get("satelite", ""),
                "risco_fogo": risco,
                "frp": frp,
                "dias_sem_chuva": dias_sem_chuva,
                "bioma": linha.get("bioma", ""),
            })
    return focos


def _classificar_risco(risco):
    if risco >= 0.8:
        return "Critico", (0.72, 0.11, 0.11, 1)
    elif risco >= 0.6:
        return "Alto", (0.91, 0.30, 0.24, 1)
    elif risco >= 0.4:
        return "Moderado", (0.95, 0.61, 0.07, 1)
    elif risco >= 0.2:
        return "Baixo", (0.98, 0.80, 0.18, 1)
    else:
        return "Minimo", (0.13, 0.71, 0.43, 1)


def buscar_focos_presidente_figueiredo():
    hoje = datetime.now()
    dias = [hoje - timedelta(days=i) for i in range(1, DIAS_JANELA + 1)]

    focos_todos = []
    erros = []

    with ThreadPoolExecutor(max_workers=2) as executor:
        futuros = {executor.submit(_baixar_arquivo_dia, dia): dia for dia in dias}

        for futuro in as_completed(futuros):
            dia = futuros[futuro]
            try:
                texto = futuro.result()
                if texto is None:
                    erros.append(dia.strftime("%Y-%m-%d"))
                    continue
                focos_todos.extend(_filtrar_focos(texto, dia))
            except Exception:
                erros.append(dia.strftime("%Y-%m-%d"))

    por_dia = {}
    risco_max = 0.0
    frp_max = 0.0
    for foco in focos_todos:
        d = foco["data"]
        por_dia[d] = por_dia.get(d, 0) + 1
        if foco["risco_fogo"] > risco_max:
            risco_max = foco["risco_fogo"]
        if foco["frp"] > frp_max:
            frp_max = foco["frp"]

    resultado = {
        "total": len(focos_todos),
        "focos": focos_todos,
        "por_dia": por_dia,
        "risco_max": risco_max,
        "frp_max": frp_max,
        "dias_com_foco": len(por_dia),
        "erro": None,
        "erros_dias": erros,
    }

    # Se todos os downloads falharam, tenta cache JSON
    if len(erros) == len(dias) and len(focos_todos) == 0:
        cache, timestamp = ler_cache("incendio")
        if cache:
            cache["fonte"] = "Cache offline (" + str(timestamp) + ")"
            cache["erro"] = None
            return cache

    salvar_cache("incendio", resultado)
    return resultado


if __name__ == "__main__":
    print("Buscando focos dos ultimos 7 dias para Presidente Figueiredo...")
    r = buscar_focos_presidente_figueiredo()
    print("Total de focos:", r["total"])
    print("Dias com foco:", r["dias_com_foco"])
    print("Risco maximo:", round(r["risco_max"], 2))
    print("FRP maximo:", round(r["frp_max"], 1))
    if r.get("erros_dias"):
        print("Dias com erro:", r["erros_dias"])
