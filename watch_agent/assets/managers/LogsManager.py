import os
import gzip
import shutil
from datetime import datetime

from assets.managers.ConfigManager import CONFIG

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class LogsManager:
    def __init__(self):
        self.log_file : str = os.path.join(BASE_DIR, CONFIG.LOGS_PATH)
        self.max_size_kb : int = CONFIG.LOGS_MAX_SIZE_KB
        self.max_backups : int = CONFIG.LOGS_MAX_BACKUPS
        
        self.COLORS = {
            "INFO": "\033[94m",     # Blu
            "SUCCESS": "\033[92m",  # Verde
            "WARNING": "\033[93m",  # Giallo
            "ERROR": "\033[91m",    # Rosso
            "RESET": "\033[0m"      # Reset colore
        }

    def format_message(self, message : str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] {message}"

    def write(self, message : str, level : str = "INFO"):
        level = level.upper()
        formatted_msg = self.format_message(message)
        
        color = self.COLORS.get(level, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]
        print(f"{color}{formatted_msg}{reset}")
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(formatted_msg + "\n")
        except Exception as e:
            print(f"{self.COLORS["ERROR"]}[LOGGER ERROR] Impossibile scrivere sul file di log: {e}{reset}")

    def info(self, msg : str): self.write(msg, "INFO")
    def success(self, msg : str): self.write(msg, "SUCCESS")
    def warning(self, msg : str): self.write(msg, "WARNING")
    def error(self, msg : str): self.write(msg, "ERROR")

    def cleanup_old_archives(self) -> bool:
        prefix = os.path.splitext(CONFIG.LOGS_PATH)[0]

        gz_files = [
            os.path.join(os.path.join(BASE_DIR, "logs"), f)
            for f in os.listdir(os.path.join(BASE_DIR, "logs"))
            if f.startswith(prefix) and f.endswith(".gz")
        ]

        gz_files.sort(key=os.path.getmtime)

        while len(gz_files) > self.max_backups:
            oldest_file = gz_files.pop(0)
            try:
                os.remove(oldest_file)
                self.info(f"[LOGS] Eliminato vecchio archivio: {oldest_file}")
                return True
            except Exception as e:
                self.error(f"[LOGS] Errore eliminazione vecchio log: {e}")
                return False

    def rotate_and_compress_logs(self) -> bool:
        if not os.path.exists(self.log_file): return False

        size_kb = os.path.getsize(self.log_file) / 1024

        if size_kb >= self.max_size_kb:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                compressed_filename = f"{os.path.splitext(CONFIG.LOGS_PATH)[0]}_{timestamp}.txt.gz"

                compressed_path = os.path.join(os.path.join(BASE_DIR, "logs"), compressed_filename)

                with open(self.log_file, "rb") as f_in:
                    with gzip.open(compressed_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)

                open(self.log_file, "w").close()

                self.info(f"[LOGS] Log compresso con successo in {compressed_path} (Soglia {self.max_size_kb} KB superata).")

                return self.cleanup_old_archives()

            except Exception as e:
                self.error(f"[LOGS] Errore durante la rotazione e compressione del log: {e}")
                return False
        else: 
            return True

LOGS = LogsManager()