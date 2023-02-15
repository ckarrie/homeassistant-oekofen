from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Callable, Any

from homeassistant.components.binary_sensor import BinarySensorEntityDescription, BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.components.sensor import SensorEntityDescription, SensorDeviceClass, RestoreSensor, SensorStateClass
from homeassistant.components.water_heater import WaterHeaterEntity, WaterHeaterEntityEntityDescription, STATE_OFF, STATE_ON
from homeassistant.const import PERCENTAGE, TEMP_CELSIUS, UnitOfTemperature, ATTR_TEMPERATURE, UnitOfTime, \
    MASS_KILOGRAMS
from homeassistant.core import callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import HAOekofenEntity
from .coordinator import HAOekofenCoordinatorEntity
from .const import WATER_HEATER_SENSORS_OPERATION_LIST

_LOGGER = logging.getLogger(__name__)


@dataclass
class OekofenAttributeDescription(SensorEntityDescription):
    value: Callable = lambda data: data
    index: int = 0


@dataclass
class OekofenBinaryAttributeDescription(BinarySensorEntityDescription):
    value: Callable = lambda data: data
    index: int = 0

    device_class: SensorDeviceClass | None = None
    suggested_unit_of_measurement: str | None = None
    last_reset: datetime | None = None
    native_unit_of_measurement: str | None = None
    state_class: SensorStateClass | str | None = None
    options: list[str] | None = None
    unit_of_measurement: None = None
    native_precision = None


@dataclass
class OekofenWaterHeaterAttributeDescription(WaterHeaterEntityEntityDescription):
    attr_config: dict = None


def get_temperature_description(domain_name, domain_index, attribute_key):
    return OekofenAttributeDescription(
        key=f'{domain_name}{domain_index}.{attribute_key}',
        name=f'{domain_name.upper()} {domain_index} {attribute_key}',
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
    )


def get_statetext_description(domain_name, domain_index, attribute_key):
    return OekofenAttributeDescription(
        key=f'{domain_name}{domain_index}.{attribute_key}',
        name=f'{domain_name.upper()} {domain_index} {attribute_key}',
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=None,
        device_class=None,
        icon="mdi:text",
    )


def get_pump_percent_description(domain_name, domain_index, attribute_key):
    return OekofenAttributeDescription(
        key=f'{domain_name}{domain_index}.{attribute_key}',
        name=f'{domain_name.upper()} {domain_index} {attribute_key} Pump',
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.POWER_FACTOR,
        icon="mdi:pump",
    )


def get_percentage_description(domain_name, domain_index, attribute_key):
    return OekofenAttributeDescription(
        key=f'{domain_name}{domain_index}.{attribute_key}',
        name=f'{domain_name.upper()} {domain_index} {attribute_key}',
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.POWER_FACTOR,
    )

def get_weight_description(domain_name, domain_index, attribute_key):
    return OekofenAttributeDescription(
        key=f'{domain_name}{domain_index}.{attribute_key}',
        name=f'{domain_name.upper()} {domain_index} {attribute_key}',
        native_unit_of_measurement=MASS_KILOGRAMS,
        device_class=SensorDeviceClass.WEIGHT,
    )

def get_pump_binary_description(domain_name, domain_index, attribute_key) -> OekofenBinaryAttributeDescription:
    return OekofenBinaryAttributeDescription(
        key=f'{domain_name}{domain_index}.{attribute_key}',
        name=f'{domain_name.upper()} {domain_index} {attribute_key} Pump',
        device_class=BinarySensorDeviceClass.POWER,
        icon="mdi:pump",
    )


def get_binary_description(domain_name, domain_index, attribute_key) -> OekofenBinaryAttributeDescription:
    return OekofenBinaryAttributeDescription(
        key=f'{domain_name}{domain_index}.{attribute_key}',
        name=f'{domain_name.upper()} {domain_index} {attribute_key}',
        device_class=BinarySensorDeviceClass.POWER,
        icon="mdi:electric-switch",
    )


def get_waterheater_description(domain_name, domain_index, attribute_key, attr_config) -> OekofenWaterHeaterAttributeDescription:
    return OekofenWaterHeaterAttributeDescription(
        key=f'{domain_name}{domain_index}.{attribute_key}',
        name=f'{domain_name.upper()} {domain_index} {attribute_key} Pump',
        #device_class=BinarySensorDeviceClass.POWER,
        icon="mdi:pump",
        attr_config=attr_config,
    )


def get_zs_description(domain_name, domain_index, attribute_key):
    return OekofenAttributeDescription(
        key=f'{domain_name}{domain_index}.{attribute_key}',
        name=f'{domain_name.upper()} {domain_index} {attribute_key}',
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        icon="mdi:clock",
    )


def get_total_hour_description(domain_name, domain_index, attribute_key):
    return OekofenAttributeDescription(
        key=f'{domain_name}{domain_index}.{attribute_key}',
        name=f'{domain_name.upper()} {domain_index} {attribute_key}',
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        icon="mdi:timeline",
    )


def get_total_minute_description(domain_name, domain_index, attribute_key):
    return OekofenAttributeDescription(
        key=f'{domain_name}{domain_index}.{attribute_key}',
        name=f'{domain_name.upper()} {domain_index} {attribute_key}',
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        icon="mdi:metronome",
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


class OekofenBinarySensorEntity(HAOekofenCoordinatorEntity, BinarySensorEntity):
    entity_description: OekofenBinaryAttributeDescription

    def __init__(
            self,
            coordinator: DataUpdateCoordinator,
            oekofen_entity: HAOekofenEntity,
            entity_description: OekofenBinaryAttributeDescription
    ) -> None:
        super().__init__(coordinator, oekofen_entity)
        self.entity_description = entity_description
        self._name = f"{oekofen_entity.device_name} {entity_description.name}"
        self._unique_id = f"{oekofen_entity.unique_id}-{entity_description.key}-{entity_description.index}"
        self._attr_is_on: bool = False
        self.async_update_device()

    @callback
    def async_update_device(self) -> None:
        if self.coordinator.data is None:
            return

        data = self.coordinator.data.get(self.entity_description.key)
        self._attr_is_on = self.entity_description.value(data)


class HAOekofenWaterHeaterEntity(HAOekofenCoordinatorEntity, WaterHeaterEntity):
    """Representation of an ATAG water heater."""

    _attr_operation_list = WATER_HEATER_SENSORS_OPERATION_LIST
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    entity_description: OekofenWaterHeaterAttributeDescription

    def __init__(
            self,
            coordinator: DataUpdateCoordinator,
            oekofen_entity: HAOekofenEntity,
            entity_description: OekofenWaterHeaterAttributeDescription
    ) -> None:
        super().__init__(coordinator, oekofen_entity)
        self.entity_description = entity_description
        self._name = f"{oekofen_entity.device_name} {entity_description.name}"
        self._unique_id = f"{oekofen_entity.unique_id}-{entity_description.key}-waterheater"
        self.async_update_device()

    def _get_value_from_other_key(self, attr):
        current_operation_attr = self.entity_description.attr_config.get(attr)  # > mode_auto
        domain, attr = self.entity_description.key.split('.')  # > hk1, temp_heat
        new_key = f'{domain}.{current_operation_attr}'  # hk1.mode_auto
        value = self.coordinator.data.get(new_key)
        return value

    @property
    def current_temperature(self):
        """Return the current temperature."""
        value = self._get_value_from_other_key('current_temp')
        return value

    @property
    def current_operation(self):
        """Return current operation."""
        value = self._get_value_from_other_key('current_operation')
        print("current_operation=", value)
        return STATE_ON

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        print("[water_heater.HAOekofenWaterHeater.async_set_temperature] with kwags %s" % kwargs)
        if await self.coordinator.data.api.set_heating_circuit_temp(celsius=kwargs.get(ATTR_TEMPERATURE)):
            self.async_write_ha_state()

    @property
    def target_temperature(self):
        """Return the setpoint if water demand, otherwise return base temp (comfort level)."""
        value = self._get_value_from_other_key('target_temp')
        return value

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        return 40.0

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        return 15.0

