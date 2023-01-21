from __future__ import annotations
import asyncio
import logging
from datetime import timedelta
from typing import Any

import async_timeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    Platform,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers import device_registry as dr

import oekofen_api
from . import const

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.WATER_HEATER, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Atag integration from a config entry."""

    async def _async_update_data():
        """Update Oekofen client via Coordinator"""
        async with async_timeout.timeout(20):
            try:
                await ha_client.async_api_update_data()
            except Exception as err:
                raise UpdateFailed(err) from err
        return ha_client

    assert entry.unique_id

    ha_client = HomeAssistantOekofenEntity(hass=hass, entry=entry)

    coordinator = DataUpdateCoordinator[oekofen_api.Oekofen](
        hass,
        _LOGGER,
        name=const.DOMAIN.title(),
        update_method=_async_update_data,
        update_interval=const.SCAN_INTERVAL,
    )

    # Fetch data first time
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(const.DOMAIN, {})[entry.entry_id] = coordinator

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(const.DOMAIN, entry.unique_id)},
        manufacturer="Oekofen",
        name=ha_client.host,
        model=ha_client.api.get_model(),
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Atag config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[const.DOMAIN].pop(entry.entry_id)
    return unload_ok


class HomeAssistantOekofenEntity(object):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        assert entry.unique_id
        self.hass = hass
        self.entry = entry
        self.entry_id = entry.entry_id
        self.unique_id = entry.unique_id
        self.host: str = entry.data[CONF_HOST]
        self._password = entry.data[CONF_PASSWORD]
        self._port = entry.data[CONF_PORT]
        self._update_interval = entry.data[CONF_SCAN_INTERVAL]

        self.api: oekofen_api.Oekofen | None = None
        self.api_lock = asyncio.Lock()

    def _setup(self) -> bool:
        self.api = oekofen_api.Oekofen(
            host=self.host,
            json_password=self._password,
            port=self._port,
            update_interval=self._update_interval,
        )
        return True

    async def async_setup(self) -> bool:
        async with self.api_lock:
            if not await self.hass.async_add_executor_job(self._setup):
                return False
        return True

    async def async_api_update_data(self) -> dict[str, Any] | None:
        async with self.api_lock:
            return await self.hass.async_add_executor_job(self.api.update_data)


class OekofenCoordinatorEntity(
    CoordinatorEntity[DataUpdateCoordinator[oekofen_api.Oekofen]]
):
    """Defines a base Atag entity."""

    def __init__(
        self, coordinator: DataUpdateCoordinator[oekofen_api.Oekofen], atag_id: str
    ) -> None:
        """Initialize the Atag entity."""
        super().__init__(coordinator)

        self._id = atag_id  # changeme
        self._attr_name = const.DOMAIN.title()  # changeme
        self._attr_unique_id = f"{coordinator.data.id}-{atag_id}"  # changeme

    @property
    def device_info(self) -> DeviceInfo:
        """Return info for device registry."""
        return DeviceInfo(
            identifiers={(const.DOMAIN, self.coordinator.data.id)},  # changeme
            manufacturer="Atag",  # changeme
            model="Atag One",  # changeme
            name="Atag Thermostat",  # changeme
            sw_version=self.coordinator.data.apiversion,  # changeme
        )
