"""Coordinator for Oekofen integration."""

import logging

import aiohttp
import oekofen_api

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, SCAN_INTERVAL

_LOGGER: logging.Logger = logging.getLogger(__package__)


class OekofenDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, client: oekofen_api.Oekofen) -> None:
        """Initialize."""
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)
        self.api = client
        self.update_method = self._async_update_data
        self.data = {}

    async def _async_update_data(self):
        """Update data via library."""
        try:
            await self.api.update_data()
            data = self.api._data
            if data:
                self.data.update(**self.api._data)
            return self.data
        except (
            aiohttp.ClientConnectorError,
            aiohttp.ClientResponseError,
        ) as error:
            raise UpdateFailed(error) from error
