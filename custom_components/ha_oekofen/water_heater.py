"""water heater component."""
from typing import Any

from homeassistant.components.water_heater import (
    STATE_ECO,
    STATE_PERFORMANCE,
    WaterHeaterEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, STATE_OFF, Platform, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, KEY_OEKOFENHOMEASSISTANT, KEY_COORDINATOR, WATER_HEATER_SENSORS_BY_DOMAIN
from .entity import HAOekofenWaterHeaterEntity, get_waterheater_description


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize device from config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][KEY_COORDINATOR]
    ha_oekofen = hass.data[DOMAIN][config_entry.entry_id][KEY_OEKOFENHOMEASSISTANT]

    """
    # Pump Sensors
    for domain_name, attribute_names in L_PUMP_BINARY_SENSORS_BY_DOMAIN.items():
        domain_indexes = ha_oekofen.api.data.get(f'{domain_name}_indexes')
        for domain_index in domain_indexes:
            for attribute_name in attribute_names:
                sensor_entity = OekofenBinarySensorEntity(
                    coordinator=coordinator,
                    oekofen_entity=ha_oekofen,
                    entity_description=get_pump_binary_description(
                        domain_name=domain_name,
                        domain_index=domain_index,
                        attribute_key=attribute_name
                    )
                )
                entities.append(sensor_entity)
    """

    entities = []

    for domain_name, domain_config in WATER_HEATER_SENSORS_BY_DOMAIN.items():
        domain_indexes = ha_oekofen.api.data.get(f'{domain_name}_indexes')
        for domain_index in domain_indexes:
            attribute_key = domain_config.get('current_temp')
            entity_description = get_waterheater_description(domain_name, domain_index, attribute_key, domain_config)
            entity = HAOekofenWaterHeaterEntity(coordinator=coordinator, oekofen_entity=ha_oekofen, entity_description=entity_description)
            entities.append(entity)

    async_add_entities(entities)
    print("[water_heater.async_setup_entry] done %s" % coordinator)


