import logging

from . import const
from .entity import get_switch_description, OekofenSwitchEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Fritzbox smarthome switch from config_entry."""
    entities = []
    coordinator = hass.data[const.DOMAIN][config_entry.entry_id][const.KEY_COORDINATOR]
    ha_oekofen = hass.data[const.DOMAIN][config_entry.entry_id][
        const.KEY_OEKOFENHOMEASSISTANT
    ]

    for domain_name, attribute_names in const.SWITCHES_BY_DOMAIN.items():
        domain_indexes = ha_oekofen.api.data.get(f"{domain_name}_indexes", [""])
        for domain_index in domain_indexes:
            for attribute_name in attribute_names:
                switch_entity = OekofenSwitchEntity(
                    coordinator=coordinator,
                    oekofen_entity=ha_oekofen,
                    entity_description=get_switch_description(
                        domain_name=domain_name,
                        domain_index=domain_index,
                        attribute_key=attribute_name,
                    ),
                    oekofen_domain=domain_name,
                    oekofen_attribute=attribute_name,
                    oekofen_domain_index=domain_index,
                )
                entities.append(switch_entity)
                _LOGGER.debug("Added Switch entitiy %s", switch_entity)

    async_add_entities(entities)
