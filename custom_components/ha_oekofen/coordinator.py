"""Coordinator for Oekofen integration."""

import logging
from abc import abstractmethod

import oekofen_api
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity

from . import HAOekofenEntity
from .const import DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)


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
            identifiers={(DOMAIN, self._oekofen_entity.unique_id)},
        )
