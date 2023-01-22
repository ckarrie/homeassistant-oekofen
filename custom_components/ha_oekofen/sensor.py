from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription, RestoreSensor
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.typing import StateType
from datetime import date, datetime
from decimal import Decimal

_LOGGER = logging.getLogger(__name__)

from . import const, HAOekofenEntity, HAOekofenCoordinatorEntity
import oekofen_api


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize sensor platform from config entry."""
    coordinator = hass.data[const.DOMAIN][config_entry.entry_id][const.KEY_COORDINATOR]
    ha_oekofen = hass.data[const.DOMAIN][config_entry.entry_id][const.KEY_OEKOFENHOMEASSISTANT]
    entities = []

    # HK-Sensors
    heating_circuits = ha_oekofen.api.domains.get('hk', [])
    for hc in heating_circuits:
        entities.append(
            OekofenHKSensorEntity(
                coordinator=coordinator,
                oekofen_entity=ha_oekofen,
                domain=hc,
                attribute_key='L_statetext'
            )
        )

    async_add_entities(entities)


@dataclass
class OekofenAttributeDescription(SensorEntityDescription):
    value: Callable = lambda data: data
    index: int = 0


class OekofenHKSensorEntity(HAOekofenCoordinatorEntity, RestoreSensor):
    entity_description: OekofenAttributeDescription

    def __init__(
            self,
            coordinator: DataUpdateCoordinator,
            oekofen_entity: HAOekofenEntity,
            domain: oekofen_api.Domain,
            attribute_key: str
    ):
        entity_description = OekofenAttributeDescription(
            key=f'{domain.name}{domain.index}.{attribute_key}',
            name=f'{domain.name.upper()} {domain.index}',
            entity_category=EntityCategory.DIAGNOSTIC,
        )
        self.domain = domain
        self.attribute_key = attribute_key
        super().__init__(coordinator, oekofen_entity)
        self.entity_description = entity_description
        self._name = f'{oekofen_entity.api.get_name()} {entity_description.name}'
        self._unique_id = f"{oekofen_entity.unique_id}-{entity_description.key}-{entity_description.index}"
        self._value: StateType | date | datetime | Decimal = None
        self.async_update_device()


    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._value

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        if self.coordinator.data is None:
            sensor_data = await self.async_get_last_sensor_data()
            if sensor_data is not None:
                self._value = sensor_data.native_value

    @callback
    def async_update_device(self) -> None:
        """Update the Netgear device."""
        if self.domain is None:
            return

        data = self.domain.attributes.get(self.attribute_key).get_value()
        if data is None:
            self._value = None
            _LOGGER.debug(
                "key '%s' not in Netgear router response '%s'",
                self.entity_description.key,
                data,
            )
            return

        self._value = self.entity_description.value(data)