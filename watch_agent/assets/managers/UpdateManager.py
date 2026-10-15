import os
import shutil
import sys
from urllib.request import Request, urlopen
import zipfile
from pathlib import Path

PROJECT_DIR = Path("/usr/share/watch_agent").resolve()

from assets.managers.ConfigManager import CONFIG
from assets.managers.LogsManager import LOGS
from assets.managers.SettingsManager import SETTINGS

from assets.managers.AppManager import appManager
from assets.controllers.WiFiController import wifiController

from assets.lib.threading import ThreadWithReturnValue

class UpdateManager:
	def __init__(self):
		self.update_url : str = CONFIG.UPDATE_URL
		self.app_dir : str = CONFIG.APP_DIR
		self.backup_dir : str = CONFIG.UPDATE_BACKUP_DIR
		self.tmp_dir : str = CONFIG.UPDATE_TMP_DIR
		self.zip_path : str = CONFIG.UPDATE_ZIP_PATH

	def make_backup(self) -> bool:
		LOGS.info(f"[UpdateManager] Creo backup della versione attuale in {self.backup_dir}.")

		try:
			if Path(self.backup_dir).exists():
				shutil.rmtree(Path(self.backup_dir))

			shutil.copytree(PROJECT_DIR, Path(self.backup_dir))

			return True
		except Exception as e:
			LOGS.error(f"[UpdateManager] Errore la creazione del backup: {e}")
			return False

	def download_and_unzip(self) -> bool:
		LOGS.info(f"[UpdateManager] Scarico la nuova versione da {self.update_url}.")

		try:
			req = Request(
				self.update_url, 
				headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
			)

			with urlopen(req) as response, open(self.zip_path, 'wb') as out_file:
				out_file.write(response.read())
		except Exception as e:
			LOGS.error(f"[UpdateManager] Non è stato possibile scaricare il file: {e}")
			return False

		try:
			if Path(self.tmp_dir).exists():
				shutil.rmtree(Path(self.tmp_dir))

			with zipfile.ZipFile(self.zip_path, "r") as zip_ref:
				zip_ref.extractall(self.tmp_dir)

			return True
		except Exception as e:
			LOGS.error(f"[UpdateManager] Non è stato possibile unzippare il file scaricato: {e}")
			return False

	def update_files(self) -> bool:
		LOGS.info("[UpdateManager] Aggiorno i file scaricati.")

		try:
			shutil.copytree(self.tmp_dir, PROJECT_DIR, dirs_exist_ok=True)
			return True
		except Exception as e:
			LOGS.error(f"[UpdateManager] Errore durante l'aggiornamento dei file: {e}")

	def remove_tmp_file(self) -> bool:
		LOGS.info("[UpdateManager] Pulizia file temporanei...")

		try: 
			if Path(self.zip_path).exists():
				Path(self.zip_path).unlink()
			if Path(self.tmp_dir).exists():
				shutil.rmtree(Path(self.tmp_dir))

			return True
		except Exception as e:
			LOGS.error(f"[UpdateManager] Errore nella pulizia dei file temporanei: {e}")
			return False

	def reload_app(self):
		LOGS.warning("[UpdateManager] Reloading app...")

		appManager.close_app()

		os.execv(sys.executable, [sys.executable] + sys.argv)

	def rollback(self) -> bool:
		if os.path.exists(self.backup_dir):
			try:
				shutil.copytree(self.backup_dir, PROJECT_DIR, dirs_exist_ok=True)
				LOGS.success("[UpdateManager] Rollback eseguito con successo.")

				return True
			except Exception as e:
				LOGS.error(f"[UpdateManager] Rollback non eseguito: {e}")
				return False
		else:
			LOGS.error("[UpdateManager] Rollback non eseguito: il file di backup non esiste.")
			return False

	def update(self):
		LOGS.info("[UpdateManager] Updating...")
		try:
			wifi_thread = ThreadWithReturnValue(target=wifiController.connect_wifi, args=(SETTINGS.WIFI_SSID, SETTINGS.WIFI_PASSWORD), daemon=True)
			wifi_thread.start()
			
			connected = wifi_thread.join()

			if not connected: 
				LOGS.error(f"[UpdateManager] Errore durante l'aggiornamento: non è stato possibile connettersi al WiFi.")
				return False

			if not self.make_backup(): return False
			if not self.download_and_unzip(): return False
			if not self.update_files(): return False
			if not self.remove_tmp_file(): return self.rollback()	
			if not self.reload_app(): return False
	
		except Exception as e:
			LOGS.error(f"[UpdateManager] Errore durante l'aggiornamento: {e}")
			self.rollback()


updateManager = UpdateManager()