import json
import os
from pathlib import Path

import log

DATA_DIR = Path(__file__).resolve().parent / "data"
WATCHES_FILE = DATA_DIR / "watches.json"


def loadKnownWatches() -> dict[str, int]:
    if not WATCHES_FILE.exists():
        return {}
    try:
        with open(WATCHES_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        watches = {str(mac).strip().upper(): int(uid) for mac, uid in raw.items()}
        log.stampaInfo(f"STORAGE: caricati {len(watches)} orologi da {WATCHES_FILE}")
        return watches
    except Exception as e:
        log.stampaAllarme(f"STORAGE: errore lettura {WATCHES_FILE} ({e}), parto con mappa vuota")
        return {}


def saveKnownWatches(watches: dict[str, int]):
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        tmpFile = WATCHES_FILE.with_suffix(".tmp")
        with open(tmpFile, "w", encoding="utf-8") as f:
            json.dump(watches, f, indent=2, sort_keys=True)
        os.replace(tmpFile, WATCHES_FILE)
    except Exception as e:
        log.stampaAllarme(f"STORAGE: errore salvataggio {WATCHES_FILE} ({e})")