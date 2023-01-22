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

from . import const, OekofenCoordinatorEntity

OPERATION_LIST = [STATE_OFF, STATE_ECO, STATE_PERFORMANCE]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize device from config entry."""
    coordinator = hass.data[const.DOMAIN][config_entry.entry_id][const.KEY_COORDINATOR]
    async_add_entities([OekofenWaterHeater(coordinator, Platform.WATER_HEATER)])
    print("[water_heater.async_setup_entry] done %s" % coordinator)


class OekofenWaterHeater(OekofenCoordinatorEntity, WaterHeaterEntity):
    """Representation of an ATAG water heater."""

    _attr_operation_list = OPERATION_LIST
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self.coordinator.data.api.get_heating_circuit_temp()

    @property
    def current_operation(self):
        """Return current operation."""
        operation = self.coordinator.data.api.get_heating_circuit_state()
        return operation if operation in self.operation_list else STATE_OFF

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        print("[water_heater.OekofenWaterHeater.async_set_temperature] with kwags %s" % kwargs)
        if await self.coordinator.data.api.set_heating_circuit_temp(celsius=kwargs.get(ATTR_TEMPERATURE)):
            self.async_write_ha_state()

    @property
    def target_temperature(self):
        """Return the setpoint if water demand, otherwise return base temp (comfort level)."""
        attr = self.coordinator.data.api.get_attribute('hk', 'L_flowtemp_set')
        return attr.get_value()

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        return 40.0

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        return 15.0
