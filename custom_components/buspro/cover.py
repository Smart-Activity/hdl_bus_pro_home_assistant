"""HDL Buspro curtain support."""

import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.cover import (
    PLATFORM_SCHEMA,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.const import CONF_DEVICES, CONF_NAME

from . import DATA_BUSPRO
from .pybuspro.devices.generic import Generic

_LOGGER = logging.getLogger(__name__)

OPERATE_CODE_CURTAIN_CONTROL = [0xE3, 0xE0]
COMMAND_STOP = 0
COMMAND_OPEN = 1
COMMAND_CLOSE = 2

DEVICE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Optional("open_command", default=COMMAND_OPEN): vol.In((1, 2)),
        vol.Optional("close_command", default=COMMAND_CLOSE): vol.In((1, 2)),
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_DEVICES): {cv.string: DEVICE_SCHEMA}}
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up HDL Buspro curtain entities from YAML."""
    hdl = hass.data[DATA_BUSPRO].hdl
    entities = []

    for address, device_config in config[CONF_DEVICES].items():
        parts = address.split(".")
        if len(parts) != 3:
            raise vol.Invalid(
                f"Cover address '{address}' must use subnet.device.curtain format"
            )

        subnet_id, device_id, curtain_number = (int(part) for part in parts)
        if not 1 <= curtain_number <= 255:
            raise vol.Invalid("Curtain number must be between 1 and 255")

        entities.append(
            BusproCover(
                hass=hass,
                hdl=hdl,
                device_address=(subnet_id, device_id),
                curtain_number=curtain_number,
                name=device_config[CONF_NAME],
                open_command=device_config["open_command"],
                close_command=device_config["close_command"],
            )
        )

    async_add_entities(entities)


class BusproCover(CoverEntity):
    """Representation of an HDL Buspro curtain."""

    _attr_should_poll = False
    _attr_assumed_state = True
    _attr_is_closed = None
    _attr_supported_features = (
        CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP
    )

    def __init__(
        self,
        hass,
        hdl,
        device_address,
        curtain_number,
        name,
        open_command,
        close_command,
    ):
        self._hass = hass
        self._hdl = hdl
        self._device_address = device_address
        self._curtain_number = curtain_number
        self._open_command = open_command
        self._close_command = close_command
        self._attr_name = name
        # HDL curtain control does not report a dependable position yet.
        # Explicitly initialize the state expected by Home Assistant's
        # CoverEntity base class and expose it as an assumed state.
        self._attr_is_closed = None
        self._attr_unique_id = (
            f"buspro_cover_{device_address[0]}_{device_address[1]}_{curtain_number}"
        )

    @property
    def available(self):
        """Return whether the Buspro connection is active."""
        return self._hass.data[DATA_BUSPRO].connected

    async def _send_command(self, command):
        message = Generic(
            self._hdl,
            self._device_address,
            [self._curtain_number, command],
            OPERATE_CODE_CURTAIN_CONTROL,
            self._attr_name,
        )
        await message.run()

    async def async_open_cover(self, **kwargs):
        """Open the curtain."""
        await self._send_command(self._open_command)

    async def async_close_cover(self, **kwargs):
        """Close the curtain."""
        await self._send_command(self._close_command)

    async def async_stop_cover(self, **kwargs):
        """Stop the curtain."""
        await self._send_command(COMMAND_STOP)
