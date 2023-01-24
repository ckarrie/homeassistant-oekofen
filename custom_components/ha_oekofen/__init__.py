from __future__ import annotations

import asyncio
import logging
from typing import Any

import async_timeout
import oekofen_api
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    Platform,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from . import const

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [
    #Platform.WATER_HEATER,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Oekofen integration from a config entry."""
    ha_client = HAOekofenEntity(hass, entry)

    try:
        if not await ha_client.async_setup():
            raise ConfigEntryNotReady
    except Exception as ex:
        raise ex

    hass.data.setdefault(const.DOMAIN, {})
    entry.async_on_unload(entry.add_update_listener(update_listener))

    assert entry.unique_id

    # Fetch data
    # await ha_client.api.update_data()

    async def _async_update_data():
        """Update Oekofen client via Coordinator"""
        async with async_timeout.timeout(20):
            try:
                return await ha_client.async_api_update_data()
            except Exception as err:

                raise UpdateFailed(err) from err

    coordinator = DataUpdateCoordinator[oekofen_api.Oekofen](
        hass,
        _LOGGER,
        name=f'{ha_client.api.get_name()} Coordinator',
        update_method=_async_update_data,
        update_interval=const.SCAN_INTERVAL,
    )

    # Fetch data first time
    await coordinator.async_config_entry_first_refresh()

    device_registry = dr.async_get(hass)
    model = ha_client.api.get_model()
    model_long = const.MODEL_ABBR.get(model, model)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(const.DOMAIN, entry.unique_id)},
        manufacturer=const.MANUFACTURER,
        name=ha_client.api.get_name(),
        model=model_long,
    )

    hass.data.setdefault(const.DOMAIN, {})[entry.entry_id] = {
        const.KEY_OEKOFENHOMEASSISTANT: ha_client,
        const.KEY_COORDINATOR: coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Atag config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[const.DOMAIN].pop(entry.entry_id)
    return unload_ok


async def update_listener(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_migrate_entry(hass, config_entry: ConfigEntry):
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version == 1:
        new = {**config_entry.data}
        new.update({const.CONF_RAISE_EXCEPTION_ON_UPDATE: False})

        config_entry.version = 2
        hass.config_entries.async_update_entry(config_entry, data=new)

    _LOGGER.info("Migration to version %s successful", config_entry.version)

    return True


class HAOekofenEntity(object):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        assert entry.unique_id
        self.hass = hass
        self.entry = entry
        self.entry_id = entry.entry_id
        self.unique_id = entry.unique_id
        self.device_name = entry.title
        self.host: str = entry.data[CONF_HOST]
        self._password = entry.data[CONF_PASSWORD]
        self._port = entry.data[CONF_PORT]
        self._update_interval = entry.data[CONF_SCAN_INTERVAL]
        self._raise_exceptions_on_update = entry.data.get(const.CONF_RAISE_EXCEPTION_ON_UPDATE, False)
        self._data_from_api = {}

        self.api: oekofen_api.Oekofen | None = None
        self.api_lock = asyncio.Lock()

    def _setup(self) -> bool:
        self.api = oekofen_api.Oekofen(
            host=self.host,
            json_password=self._password,
            port=self._port,
            update_interval=self._update_interval,
        )
        #asyncio.run(self.api.update_data())
        return True

    def update_data(self):
        return asyncio.run(self.api.update_data())

    async def async_setup(self) -> bool:
        async with self.api_lock:
            if not await self.hass.async_add_executor_job(self._setup):
                return False
        return True

    async def async_api_update_data(self) -> dict[str, Any] | None:
        print("[HAOekofenEntity.async_api_update_data] called, is this the auto-update? self._raise_exceptions_on_update=", self._raise_exceptions_on_update)
        async with self.api_lock:
            try:
                self._data_from_api = await self.hass.async_add_executor_job(self.update_data)
                return self._data_from_api
            except Exception as e:
                if self._raise_exceptions_on_update:
                    raise e
                print("[HAOekofenEntity.async_api_update_data] Returning old data (self._data_from_api)")
                return self._data_from_api
