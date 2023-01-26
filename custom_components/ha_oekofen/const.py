import datetime

from homeassistant.components.water_heater import STATE_ECO, STATE_OFF, STATE_PERFORMANCE
from homeassistant.const import Platform

DOMAIN = "ha_oekofen"
UPDATE_INTERVAL = 20
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

L_PUMP_BINARY_SENSORS_BY_DOMAIN = {
    'hk': ['L_pump'],
    # 'pu',  # is % not bool
    'ww': ['L_pump'],
    'circ': ['L_pummp'],
}

PUMP_PERCENTAGE_SENSORS_BY_DOMAIN = {
    'pu': ['L_pump']
}

TEMP_SENSORS_BY_DOMAIN = {
    'system': ['L_ambient'],
    'weather': ['L_temp'],
    'hk': ['L_roomtemp_act', 'L_roomtemp_set', 'L_flowtemp_act', 'L_flowtemp_set'],
    'pu': ['L_tpo_act', 'L_tpo_set', 'L_tpm_act', 'L_tpm_set', 'L_pump_release'],
    'ww': ['L_temp_set', 'L_ontemp_act', 'L_offtemp_act'],
    'circ': ['L_ret_temp', 'L_release_temp'],
    'pe': ['L_temp_act', 'L_temp_set', 'L_ext_temp', 'L_frt_temp_act', 'L_frt_temp_set', 'L_frt_temp_end', 'L_uw_release'],
}

STATE_SENSORS_BY_DOMAIN = {
    'hk': 'L_statetext',
    #'thirdparty': 'L_state',
    'pu': 'L_statetext',
    'ww': 'L_statetext',
    'pe': 'L_statetext'
}

#
STATE_CHOICE_SENSORS_BY_DOMAIN = {
    'weather': ['oekomode_choice'],
    'hk': ['L_pump_choice', 'mode_auto_choice', 'oekomode_choice'],
    'ww': [
        'L_pump_choice', 'time_prg_choice', 'mode_auto_choice',
        'mode_dhw_choice', 'use_boiler_heat_choice', 'sensor_on_choice',
        'sensor_off_choice', 'heat_once_choice', 'oekomode_choice'],
    'circ': ['L_pummp_choice', 'time_prg_choice', 'mode_choice', ],
    'pe': ['mode_choice']

}

# Unit: EH
PRESSURE_SENSORS_BY_DOMAIN = {
    'pe': ['L_lowpressure', 'L_lowpressure_set']
}

# Unit: zs (0,1 seconds)
TIME_SENSORS_BY_DOMAIN = {
    'pe': ['L_runtimeburner', 'L_resttimeburner']
}

# Unit: %
NON_PUMP_PERCENTAGE_SENSORS_BY_DOMAIN = {
    'pe': ['L_currentairflow', 'L_fluegas', 'L_uw_speed', 'L_uw', 'L_modulation']
}

WEIGHT_SENSORS_BY_DOMAIN = {
    'pe': ['L_storage_fill', 'L_storage_min', 'L_storage_max', 'L_storage_popper', 'storage_fill_today', 'storage_fill_yesterday']
}

TOTAL_SENSORS_HOURS_BY_DOMAIN = {
    'pe': ['L_runtime']
}

TOTAL_SENSORS_MINUTES_BY_DOMAIN = {
    'pe': ['L_avg_runtime']
}

WATER_HEATER_SENSORS_OPERATION_LIST = [STATE_OFF, STATE_ECO, STATE_PERFORMANCE]
WATER_HEATER_SENSORS_BY_DOMAIN = {
    'hk': {
        'min_temp': 'temp_heat',
        'max_temp': 'temp_heat',
        'current_temp': 'temp_heat',
        'current_operation': 'mode_auto',
        'set_temp': 'temp_heat',
        'target_temp': 'temp_heat'
    }
}



