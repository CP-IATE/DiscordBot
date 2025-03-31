from dotenv import dotenv_values

cfg = dotenv_values("config.env")

TOKEN = cfg.get("TOKEN")
TARGET_API_URL = cfg.get("TARGET_API_URL")
TARGET_API_URL2 = cfg.get("TARGET_API_URL2")