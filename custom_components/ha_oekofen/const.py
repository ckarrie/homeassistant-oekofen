import datetime

from homeassistant.const import Platform

DOMAIN = "ha_oekofen"
UPDATE_INTERVAL = 10
SCAN_INTERVAL = datetime.timedelta(seconds=UPDATE_INTERVAL)
PLATFORMS = [Platform.SENSOR, Platform.WATER_HEATER]
KEY_COORDINATOR = "ha_oekofen_coordinator"
KEY_OEKOFENHOMEASSISTANT = "ha_oekofen_hass"
ENTRY_KEY_HOST = "host"
ENTRY_KEY_JSON_PASSWORD = "json_password"
ENTRY_KEY_PORT = "port"
ENTRY_KEY_UPDATE_INTERVAL = "update_interval"
