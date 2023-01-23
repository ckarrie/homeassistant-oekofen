from dataclasses import dataclass
from typing import Callable

from homeassistant.components.binary_sensor import BinarySensorEntityDescription, BinarySensorDeviceClass
from homeassistant.components.sensor import SensorEntityDescription, SensorDeviceClass
from homeassistant.const import PERCENTAGE, TEMP_CELSIUS
from homeassistant.helpers.entity import EntityCategory


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
