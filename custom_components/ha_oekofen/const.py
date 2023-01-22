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
CONF_RAISE_EXCEPTION_ON_UPDATE = 'raise_exception_on_update'
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

L_PUMP_DOMAINS = {
    'hk': 'L_pump',
    #'pu',  # is % not bool
    'ww': 'L_pump',
    'circ': 'L_pummp'
}

TEMP_SENSORS_BY_DOMAIN = {
    'hk': ['L_roomtemp_act', 'L_roomtemp_set', 'L_flowtemp_act', 'L_flowtemp_set'],
    'pu': ['L_tpo_act', 'L_tpo_set', 'L_tpm_act', 'L_tpm_set', 'L_pump_release'],
    'ww': ['L_temp_set', 'L_ontemp_act', 'L_offtemp_act'],
    'circ': ['L_ret_temp', 'L_release_temp'],
    'pe': ['L_temp_act', 'L_temp_set', 'L_ext_temp', 'L_frt_temp_act', 'L_frt_temp_set', 'L_frt_temp_end', 'L_uw_release'],
}
