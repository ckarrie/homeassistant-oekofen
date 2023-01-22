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
SW_VERSION = '1.0 Unknown Version'
MANUFACTURER = 'ÖkoFEN'
MODEL_ABBR = {
    'PE': 'Pellematic PE',
    'PES': 'Pellematic PES',
    'PEK': 'Pellematic PEK',
    'PESK': 'Pellematic PESK',
    'SMART V1': 'Pellematic Smart V1',
    'SMART V2': 'Pellematic Smart V2',
    'CONDENS': 'Pellematic Condens',
    'SMART XS': 'Pellematic Smart XS',
    'SMART V3': 'Pellematic Smart V3',
    'COMPACT': 'Pellematic Compact',
    'AIR': 'Pellematic Air',
}

