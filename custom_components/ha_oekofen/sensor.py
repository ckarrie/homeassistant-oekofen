from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

from . import const
from .entity import OekofenHKSensorEntity, get_temperature_description, get_statetext_description, get_percentage_description, get_pump_percent_description


async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize sensor platform from config entry."""
    coordinator = hass.data[const.DOMAIN][config_entry.entry_id][const.KEY_COORDINATOR]
    ha_oekofen = hass.data[const.DOMAIN][config_entry.entry_id][const.KEY_OEKOFENHOMEASSISTANT]
    entities = []

    # TEMP_SENSORS_BY_DOMAIN
    for domain_name, attribute_names in const.TEMP_SENSORS_BY_DOMAIN.items():
        domain_indexes = ha_oekofen.api.data.get(f'{domain_name}_indexes')
        for domain_index in domain_indexes:
            for attribute_name in attribute_names:
                sensor_entity = OekofenHKSensorEntity(
                    coordinator=coordinator,
                    oekofen_entity=ha_oekofen,
                    entity_description=get_temperature_description(
                        domain_name=domain_name,
                        domain_index=domain_index,
                        attribute_key=attribute_name
                    )
                )
                entities.append(sensor_entity)

    # STATE_SENSORS_BY_DOMAIN
    for domain_name, attribute_name in const.STATE_SENSORS_BY_DOMAIN.items():
        domain_indexes = ha_oekofen.api.data.get(f'{domain_name}_indexes')
        for domain_index in domain_indexes:
            sensor_entity = OekofenHKSensorEntity(
                coordinator=coordinator,
                oekofen_entity=ha_oekofen,
                entity_description=get_statetext_description(
                    domain_name=domain_name,
                    domain_index=domain_index,
                    attribute_key=attribute_name
                )
            )
            entities.append(sensor_entity)

    # PUMP_PERCENTAGE_SENSORS_BY_DOMAIN
    for domain_name, attribute_names in const.PUMP_PERCENTAGE_SENSORS_BY_DOMAIN.items():
        domain_indexes = ha_oekofen.api.data.get(f'{domain_name}_indexes')
        for domain_index in domain_indexes:
            for attribute_name in attribute_names:
                sensor_entity = OekofenHKSensorEntity(
                    coordinator=coordinator,
                    oekofen_entity=ha_oekofen,
                    entity_description=get_pump_percent_description(
                        domain_name=domain_name,
                        domain_index=domain_index,
                        attribute_key=attribute_name
                    )
                )
                entities.append(sensor_entity)

    # Thirdparty
    thirdparty_indexes = ha_oekofen.api.data.get(f'thirdparty_indexes', [])
    for domain_index in thirdparty_indexes:
        sensor_entity = OekofenHKSensorEntity(
            coordinator=coordinator,
            oekofen_entity=ha_oekofen,
            entity_description=get_statetext_description(
                domain_name='thirdparty',
                domain_index=domain_index,
                attribute_key='L_state'
            )
        )
        entities.append(sensor_entity)

    # PE Modulation
    pe_indexes = ha_oekofen.api.data.get(f'pe_indexes', [])
    for domain_index in pe_indexes:
        mod_descr = get_percentage_description(domain_name='pe', domain_index=domain_index, attribute_key='L_modulation')
        mod_descr.icon = 'mdi:chart-line-variant'
        mod_entity = OekofenHKSensorEntity(
            coordinator=coordinator,
            oekofen_entity=ha_oekofen,
            entity_description=mod_descr,
        )
        entities.append(mod_entity)

    # add to Homeassistant
    async_add_entities(entities)
