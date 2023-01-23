from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Callable

from homeassistant.components.binary_sensor import BinarySensorEntityDescription, BinarySensorDeviceClass
from homeassistant.components.sensor import SensorEntityDescription, SensorDeviceClass, RestoreSensor
from homeassistant.const import PERCENTAGE, TEMP_CELSIUS
from homeassistant.core import callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import HAOekofenEntity
from .coordinator import HAOekofenCoordinatorEntity

_LOGGER = logging.getLogger(__name__)


@dataclass
class OekofenAttributeDescription(SensorEntityDescription):
    value: Callable = lambda data: data
    index: int = 0


@dataclass
class OekofenBinaryAttributeDescription(BinarySensorEntityDescription):
    value: Callable = lambda data: data
    index: int = 0


def get_temperature_description(domain_name, domain_index, attribute_key):
    return OekofenAttributeDescription(
        key=f'{domain_name}{domain_index}.{attribute_key}',
        name=f'{domain_name.upper()} {domain_index} {attribute_key}',
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
    )


def get_statetext_description(domain, attribute_key):
    return OekofenAttributeDescription(
        key=f'{domain.name}{domain.index}.{attribute_key}',
        name=f'{domain.name.upper()} {domain.index}',
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=None,
        device_class=None,
        icon="mdi:text",
    )


def get_pump_description(domain, attribute_key):
    return OekofenAttributeDescription(
        key=f'{domain.name}{domain.index}.{attribute_key}',
        name=f'{domain.name.upper()} {domain.index} Pump',
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.POWER_FACTOR,
        icon="mdi:pump",
    )


def get_pump_binary_description(domain, attribute_key) -> OekofenBinaryAttributeDescription:
    return OekofenBinaryAttributeDescription(
        key=f'{domain.name}{domain.index}.{attribute_key}',
        name=f'{domain.name.upper()} {domain.index} Pump',
        device_class=BinarySensorDeviceClass.POWER,
        icon="mdi:pump",
    )


class OekofenHKSensorEntity(HAOekofenCoordinatorEntity, RestoreSensor):
    entity_description: OekofenAttributeDescription

    def __init__(
            self,
            coordinator: DataUpdateCoordinator,
            oekofen_entity: HAOekofenEntity,
            entity_description: OekofenAttributeDescription,
    ) -> None:
        super().__init__(coordinator, oekofen_entity)
        self.entity_description = entity_description
        self._name = f"{oekofen_entity.device_name} {entity_description.name}"
        self._unique_id = f"{oekofen_entity.unique_id}-{entity_description.key}-{entity_description.index}"
        self._value: StateType | date | datetime | Decimal = None
        self.async_update_device()

        print(f"[OekofenHKSensorEntity] _name={self._name} _unique_id={self._unique_id}")

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
