from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import KEY_COORDINATOR, DOMAIN, KEY_OEKOFENHOMEASSISTANT, L_PUMP_BINARY_SENSORS_BY_DOMAIN
from .entity import get_pump_binary_description, OekofenBinarySensorEntity, get_binary_description


async def async_setup_entry(
        hass: HomeAssistant, entry: ConfigEntry, async_add_entries: AddEntitiesCallback
) -> None:
    """Set up the binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id][KEY_COORDINATOR]
    ha_oekofen = hass.data[DOMAIN][entry.entry_id][KEY_OEKOFENHOMEASSISTANT]
    entities = []

    # Pump Sensors
    for domain_name, attribute_names in L_PUMP_BINARY_SENSORS_BY_DOMAIN.items():
        domain_indexes = ha_oekofen.api.data.get(f'{domain_name}_indexes', [])
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

    PE_ATTRIBUTES = ['L_br', 'L_ak', 'L_not', 'L_stb']  # move to const
    pe_domain_indexes = ha_oekofen.api.data.get(f'pe_indexes', [])
    for pe_index in pe_domain_indexes:
        for attribute_name in PE_ATTRIBUTES:
            sensor_entity = OekofenBinarySensorEntity(
                coordinator=coordinator,
                oekofen_entity=ha_oekofen,
                entity_description=get_binary_description(
                    domain_name='pe',
                    domain_index=pe_index,
                    attribute_key=attribute_name
                )
            )
            entities.append(sensor_entity)

    async_add_entries(entities)
