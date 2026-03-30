"""Config flow for Voxtral TTS."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    AUDIO_FORMATS,
    CONF_API_KEY,
    CONF_AUDIO_FORMAT,
    CONF_MODEL,
    CONF_VOICE_ID,
    DEFAULT_AUDIO_FORMAT,
    DEFAULT_MODEL,
    DOMAIN,
    MISTRAL_TTS_ENDPOINT,
    MODELS,
    PRESET_VOICES,
)

_LOGGER = logging.getLogger(__name__)

# Dropdown complet des voix preset, groupées par langue
_PRESET_OPTIONS: list[SelectOptionDict] = [
    SelectOptionDict(value="", label="— Sans voix preset (défaut Voxtral) —"),
] + [
    SelectOptionDict(value=v["id"], label=v["name"])
    for lang_voices in PRESET_VOICES.values()
    for v in lang_voices
]


async def _validate_api_key(session: aiohttp.ClientSession, api_key: str) -> bool:
    """Valide la clé API en faisant un appel TTS minimal (texte vide → 400/422, pas 401)."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": DEFAULT_MODEL,
        "input": ".",          # texte minimal
        "response_format": "mp3",
        "stream": False,
    }
    try:
        async with session.post(
            MISTRAL_TTS_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            # 401 = clé invalide, tout autre code = clé OK (même une erreur métier)
            return resp.status != 401
    except (aiohttp.ClientError, TimeoutError):
        return False


class VoxtralTTSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow pour Voxtral TTS."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()
            session = async_get_clientsession(self.hass)

            if not await _validate_api_key(session, api_key):
                errors[CONF_API_KEY] = "invalid_api_key"
            else:
                await self.async_set_unique_id(f"voxtral_{api_key[:12]}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="Voxtral TTS",
                    data={
                        CONF_API_KEY: api_key,
                        CONF_MODEL: user_input.get(CONF_MODEL, DEFAULT_MODEL),
                        CONF_VOICE_ID: user_input.get(CONF_VOICE_ID, ""),
                        CONF_AUDIO_FORMAT: user_input.get(
                            CONF_AUDIO_FORMAT, DEFAULT_AUDIO_FORMAT
                        ),
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.PASSWORD)
                ),
                vol.Optional(CONF_MODEL, default=DEFAULT_MODEL): SelectSelector(
                    SelectSelectorConfig(
                        options=MODELS,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(CONF_VOICE_ID, default=""): SelectSelector(
                    SelectSelectorConfig(
                        options=_PRESET_OPTIONS,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(
                    CONF_AUDIO_FORMAT, default=DEFAULT_AUDIO_FORMAT
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=list(AUDIO_FORMATS.keys()),
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "docs_url": "https://console.mistral.ai/api-keys",
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> VoxtralTTSOptionsFlow:
        return VoxtralTTSOptionsFlow(config_entry)


class VoxtralTTSOptionsFlow(config_entries.OptionsFlow):
    """Options flow – modification sans suppression de l'intégration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self._config_entry.options or self._config_entry.data

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_MODEL,
                    default=current.get(CONF_MODEL, DEFAULT_MODEL),
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=MODELS,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(
                    CONF_VOICE_ID,
                    default=current.get(CONF_VOICE_ID, ""),
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=_PRESET_OPTIONS,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(
                    CONF_AUDIO_FORMAT,
                    default=current.get(CONF_AUDIO_FORMAT, DEFAULT_AUDIO_FORMAT),
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=list(AUDIO_FORMATS.keys()),
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)

_LOGGER = logging.getLogger(__name__)

# Flat list of all preset voices for the setup dropdown
# (custom voices added via the Mistral console are entered as free text)
_PRESET_OPTIONS: list[SelectOptionDict] = [
    SelectOptionDict(value="", label="— Aucune voix preset (sans voice_id) —"),
] + [
    SelectOptionDict(value=v["id"], label=v["name"])
    for lang_voices in PRESET_VOICES.values()
    for v in lang_voices
]


async def _validate_api_key(session: aiohttp.ClientSession, api_key: str) -> bool:
    """Valide la clé API via un appel TTS minimal sur l'endpoint speech.

    HTTP 401  → clé invalide
    Tout autre code (200, 400, 422…) → clé authentifiée
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {"model": DEFAULT_MODEL, "input": ".", "response_format": "mp3", "stream": False}
    try:
        async with session.post(
            MISTRAL_TTS_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            return resp.status != 401
    except (aiohttp.ClientError, TimeoutError):
        return False


class VoxtralTTSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Voxtral TTS."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()
            session = async_get_clientsession(self.hass)

            if not await _validate_api_key(session, api_key):
                errors[CONF_API_KEY] = "invalid_api_key"
            else:
                await self.async_set_unique_id(f"voxtral_{api_key[:12]}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="Voxtral TTS",
                    data={
                        CONF_API_KEY: api_key,
                        CONF_MODEL: user_input.get(CONF_MODEL, DEFAULT_MODEL),
                        CONF_VOICE_ID: user_input.get(CONF_VOICE_ID, ""),
                        CONF_AUDIO_FORMAT: user_input.get(
                            CONF_AUDIO_FORMAT, DEFAULT_AUDIO_FORMAT
                        ),
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.PASSWORD)
                ),
                vol.Optional(CONF_MODEL, default=DEFAULT_MODEL): SelectSelector(
                    SelectSelectorConfig(
                        options=MODELS,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(CONF_VOICE_ID, default=""): SelectSelector(
                    SelectSelectorConfig(
                        options=_PRESET_OPTIONS,
                        mode=SelectSelectorMode.DROPDOWN,
                        custom_value=True,  # allows pasting a custom voice_id
                    )
                ),
                vol.Optional(
                    CONF_AUDIO_FORMAT, default=DEFAULT_AUDIO_FORMAT
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=list(AUDIO_FORMATS.keys()),
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "docs_url": "https://console.mistral.ai/api-keys",
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> VoxtralTTSOptionsFlow:
        """Create the options flow."""
        return VoxtralTTSOptionsFlow(config_entry)


class VoxtralTTSOptionsFlow(config_entries.OptionsFlow):
    """Handle options (reconfiguration) for Voxtral TTS."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialise options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle options step."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self._config_entry.options or self._config_entry.data

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_MODEL,
                    default=current.get(CONF_MODEL, DEFAULT_MODEL),
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=MODELS,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(
                    CONF_VOICE_ID,
                    default=current.get(CONF_VOICE_ID, ""),
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=_PRESET_OPTIONS,
                        mode=SelectSelectorMode.DROPDOWN,
                        custom_value=True,
                    )
                ),
                vol.Optional(
                    CONF_AUDIO_FORMAT,
                    default=current.get(CONF_AUDIO_FORMAT, DEFAULT_AUDIO_FORMAT),
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=list(AUDIO_FORMATS.keys()),
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
