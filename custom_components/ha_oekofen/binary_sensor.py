import oekofen_api
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import HAOekofenCoordinatorEntity, entity, HAOekofenEntity
from .const import KEY_COORDINATOR, DOMAIN, KEY_OEKOFENHOMEASSISTANT


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entries: AddEntitiesCallback
) -> None:
    """Set up the binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id][KEY_COORDINATOR]
    ha_oekofen = hass.data[DOMAIN][entry.entry_id][KEY_OEKOFENHOMEASSISTANT]
    entities = []

    # HK-Sensors
    heating_circuits = ha_oekofen.api.domains.get('hk', [])
    for hc in heating_circuits:
        entities.append(OekofenBinarySensor(
            coordinator=coordinator,
            oekofen_entity=ha_oekofen,
            entity_description=entity.get_statetext_description(hc, 'L_pump'),
            domain=hc,
            attribute_key='L_pump'
        ))
    async_add_entries(entities)


class OekofenBinarySensor(HAOekofenCoordinatorEntity, BinarySensorEntity):
    entity_description: entity.OekofenAttributeDescription

    def __init__(
            self,
            coordinator: DataUpdateCoordinator,
            oekofen_entity: HAOekofenEntity,
            entity_description: entity.OekofenAttributeDescription,
            domain: oekofen_api.Domain,
            attribute_key: str,
    ) -> None:
        super().__init__(coordinator, oekofen_entity)
        self.domain = domain
        self.attribute_key = attribute_key
        self.entity_description = entity_description
        self._name = f'{oekofen_entity.api.get_name()} {entity_description.name}'
        self._unique_id = f"{oekofen_entity.unique_id}-{domain.name}-{domain.index}-{attribute_key.lower()}"
        self._attr_is_on: bool = False
        self.async_update_device()

    @callback
    def async_update_device(self) -> None:
        """Update the Netgear device."""
        if self.domain is None:
            return

        data = self.domain.attributes.get(self.attribute_key).get_value()
        self._attr_is_on = self.entity_description.value(data)
