from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Callable

from homeassistant.components.sensor import SensorEntityDescription, RestoreSensor, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TEMP_CELSIUS, PERCENTAGE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

from . import const, HAOekofenEntity, HAOekofenCoordinatorEntity, entity
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

    """
    for domain_name, attribute_names in const.TEMP_SENSORS_BY_DOMAIN.items():
        domains = ha_oekofen.api.domains.get(domain_name, [])
        for domain in domains:
            for attribute_name in attribute_names:
                if not domain.attributes.get(attribute_name):
                    print(f"Attribute {attribute_name} not found in domain {domain.name}")
                    continue
                entities.append(OekofenHKSensorEntity(
                    coordinator=coordinator,
                    oekofen_entity=ha_oekofen,
                    entity_description=entity.get_temperature_description(domain, attribute_name),
                    domain=domain,
                    attribute_key=attribute_name
                ))

    """

    d = entity.get_temperature_description(domain_name='pu', domain_index=1, attribute_key='L_tpo_act')
    ent = OekofenHKSensorEntity(coordinator=coordinator, oekofen_entity=ha_oekofen, entity_description=d)
    entities.append(ent)

    async_add_entities(entities)


class OekofenHKSensorEntity(HAOekofenCoordinatorEntity, RestoreSensor):
    entity_description: entity.OekofenAttributeDescription

    def __init__(
            self,
            coordinator: DataUpdateCoordinator,
            oekofen_entity: HAOekofenEntity,
            entity_description: entity.OekofenAttributeDescription,
    ) -> None:
        super().__init__(coordinator, oekofen_entity)
        self.entity_description = entity_description
        self._name = f"{oekofen_entity.device_name} {entity_description.name}"
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
        if self.coordinator.data is None:
            return

        print("[async_update_device] self.coordinator.data=%s" % self.coordinator.data)

        data = self.coordinator.data.get(self.entity_description.key)
        if data is None:
            self._value = None
            _LOGGER.debug(
                "key '%s' not in Netgear router response '%s'",
                self.entity_description.key,
                data,
            )
            return

        self._value = self.entity_description.value(data)
