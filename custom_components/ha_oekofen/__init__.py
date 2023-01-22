from __future__ import annotations
import asyncio
import logging
from abc import abstractmethod
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
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers import device_registry as dr
from homeassistant.exceptions import ConfigEntryNotReady

import oekofen_api
from . import const

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [
    # Platform.WATER_HEATER,
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
    await ha_client.api.update_data()

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

    async def _async_update_data():
        """Update Oekofen client via Coordinator"""
        async with async_timeout.timeout(20):
            try:
                await ha_client.async_api_update_data()
            except Exception as err:
                raise UpdateFailed(err) from err
        return ha_client

    coordinator = DataUpdateCoordinator[oekofen_api.Oekofen](
        hass,
        _LOGGER,
        name=f'{ha_client.api.get_name()} Coordinator',
        update_method=_async_update_data,
        update_interval=const.SCAN_INTERVAL,
    )

    # Fetch data first time
    await coordinator.async_config_entry_first_refresh()

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
            return await self.api.update_data()
            """
            try:
                return await self.api.update_data()
            except Exception as e:
                if self._raise_exceptions_on_update:
                    raise e
                return None
            """
            #return await self.hass.async_add_executor_job(await self.api.update_data())
            #return await self.hass.async_add_executor_job(self.api.update_data)


class HAOekofenCoordinatorEntity(CoordinatorEntity[DataUpdateCoordinator[oekofen_api.Oekofen]]):
    """Defines a base Oekofen entity."""

    def __init__(
        self, coordinator: DataUpdateCoordinator[oekofen_api.Oekofen], oekofen_entity: HAOekofenEntity
    ) -> None:
        """Initialize the Oekofen entity."""
        super().__init__(coordinator)
        self._oekofen_entity = oekofen_entity
        self._name = oekofen_entity.device_name
        self._unique_id = oekofen_entity.unique_id
        #self._api_uid = coordinator.data.api.get_uid().replace('_', '-')
        #self._attr_name = f'Oekofen {coordinator.data.api.get_model()} {domain.name} {domain.index}'
        #self._attr_unique_id = f'{self._api_uid}-{domain.name}-{domain.index}'
        #print("[HAOekofenCoordinatorEntity.__init__] _api_uid=%s" % self._api_uid)

    @abstractmethod
    @callback
    def async_update_device(self) -> None:
        """Update the Netgear device."""

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_update_device()
        super()._handle_coordinator_update()

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._unique_id

    @property
    def name(self) -> str:
        """Return the name."""
        return self._name

    @property
    def device_info(self) -> DeviceInfo:
        """Adds Entity to Device"""
        return DeviceInfo(
            identifiers={(const.DOMAIN, self._oekofen_entity.unique_id)},
        )
