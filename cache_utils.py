import os
import json
from datetime import datetime


CACHE_DIR = os.path.expanduser("~/.cache/cicc_elnino")
os.makedirs(CACHE_DIR, exist_ok=True)


def salvar_cache(nome, dados):
    caminho = os.path.join(CACHE_DIR, nome + ".json")
    try:
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump({
                "dados": dados,
                "salvo_em": datetime.now().isoformat(),
            }, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def ler_cache(nome):
    caminho = os.path.join(CACHE_DIR, nome + ".json")
    if not os.path.exists(caminho):
        return None, None

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            obj = json.load(f)
        dados = obj.get("dados")
        salvo_em = obj.get("salvo_em", "")
        try:
            dt = datetime.fromisoformat(salvo_em)
            timestamp = dt.strftime("%d/%m/%Y %H:%M")
        except Exception:
            timestamp = salvo_em

        if isinstance(dados, dict):
            dados["_do_cache"] = True
            dados["_cache_timestamp"] = timestamp

        return dados, timestamp
    except Exception:
        return None, None


def limpar_cache(nome=None):
    if nome:
        caminho = os.path.join(CACHE_DIR, nome + ".json")
        if os.path.exists(caminho):
            os.remove(caminho)
    else:
        for arq in os.listdir(CACHE_DIR):
            if arq.endswith(".json"):
                os.remove(os.path.join(CACHE_DIR, arq))
