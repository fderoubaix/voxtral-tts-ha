"""Voxtral TTS platform for Home Assistant."""
from __future__ import annotations

import asyncio
import base64
import logging
from typing import Any

import aiohttp
import async_timeout

from homeassistant.components.tts import (
    ATTR_VOICE,
    TextToSpeechEntity,
    TtsAudioType,
    Voice,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    AUDIO_FORMATS,
    CONF_API_KEY,
    CONF_AUDIO_FORMAT,
    CONF_MODEL,
    CONF_VOICE_ID,
    DEFAULT_AUDIO_FORMAT,
    DEFAULT_LANGUAGE,
    DEFAULT_MODEL,
    DOMAIN,
    MISTRAL_TTS_ENDPOINT,
    PRESET_VOICES,
    SUPPORTED_LANGUAGES,
    VALID_VOICE_IDS,
)

_LOGGER = logging.getLogger(__name__)

API_TIMEOUT = 30


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Voxtral TTS entity from config entry."""
    async_add_entities([VoxtralTTSEntity(hass, config_entry)])


class VoxtralTTSEntity(TextToSpeechEntity):
    """Voxtral TTS entity.

    API confirmée par test curl (2026-03) :
        POST https://api.mistral.ai/v1/audio/speech
        { model, input, response_format, stream, voice_id }
        → { audio_data: "<base64>" }
    """

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        self.hass = hass
        self._config_entry = config_entry
        self._api_key: str = config_entry.data[CONF_API_KEY]
        self._model: str = config_entry.options.get(
            CONF_MODEL, config_entry.data.get(CONF_MODEL, DEFAULT_MODEL)
        )
        self._voice_id: str | None = (
            config_entry.options.get(CONF_VOICE_ID)
            or config_entry.data.get(CONF_VOICE_ID)
            or None
        )
        self._audio_format: str = config_entry.options.get(
            CONF_AUDIO_FORMAT,
            config_entry.data.get(CONF_AUDIO_FORMAT, DEFAULT_AUDIO_FORMAT),
        )
        self._attr_unique_id = f"{config_entry.entry_id}_tts"
        self._attr_name = "Voxtral TTS"

    @property
    def default_language(self) -> str:
        return DEFAULT_LANGUAGE

    @property
    def supported_languages(self) -> list[str]:
        return SUPPORTED_LANGUAGES

    @property
    def supported_options(self) -> list[str]:
        return [ATTR_VOICE, CONF_MODEL, CONF_AUDIO_FORMAT]

    @property
    def default_options(self) -> dict[str, Any]:
        opts: dict[str, Any] = {
            CONF_MODEL: self._model,
            CONF_AUDIO_FORMAT: self._audio_format,
        }
        if self._voice_id:
            opts[ATTR_VOICE] = self._voice_id
        return opts

    # ------------------------------------------------------------------
    # Voice list – données statiques, méthode synchrone
    # (une méthode async non-awaited dans le handler websocket HA
    #  provoque un RuntimeWarning ; données statiques = pas besoin d'async)
    # ------------------------------------------------------------------

    def async_get_supported_voices(self, language: str) -> list[Voice] | None:
        """Retourne les voix preset pour la langue demandée. Aucun appel API."""
        voices = [
            Voice(voice_id=v["id"], name=v["name"])
            for v in PRESET_VOICES.get(language, [])
        ]
        return voices or None

    async def async_get_tts_audio(
        self,
        message: str,
        language: str,
        options: dict[str, Any] | None = None,
    ) -> TtsAudioType:
        """Appelle l'API Voxtral et retourne (extension, bytes)."""
        options = options or {}

        model = options.get(CONF_MODEL, self._model)
        audio_format = options.get(CONF_AUDIO_FORMAT, self._audio_format)

        # Validation du voice_id : on n'envoie à l'API que des IDs connus.
        # Cela évite que HA transmette un ancien ID Piper (ex: fr_FR-siwis-medium)
        # et obtienne un 404 de Mistral.
        raw_voice = options.get(ATTR_VOICE, self._voice_id) or ""
        voice_id: str | None = raw_voice if raw_voice in VALID_VOICE_IDS else None

        if raw_voice and not voice_id:
            _LOGGER.debug(
                "Voxtral: voice_id '%s' non reconnu dans les presets → ignoré", raw_voice
            )

        payload: dict[str, Any] = {
            "model": model,
            "input": message,
            "response_format": audio_format,
            "stream": False,
        }
        if voice_id:
            payload["voice_id"] = voice_id

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        _LOGGER.debug(
            "Voxtral request: model=%s format=%s voice=%s len=%d",
            model, audio_format, voice_id, len(message),
        )

        session = async_get_clientsession(self.hass)
        try:
            async with async_timeout.timeout(API_TIMEOUT):
                async with session.post(
                    MISTRAL_TTS_ENDPOINT, json=payload, headers=headers
                ) as resp:
                    if resp.status != 200:
                        body = await resp.text()
                        _LOGGER.error("Voxtral HTTP %s: %s", resp.status, body)
                        return None, None
                    data = await resp.json()
        except asyncio.TimeoutError:
            _LOGGER.error("Voxtral TTS timeout (%s s)", API_TIMEOUT)
            return None, None
        except aiohttp.ClientError as err:
            _LOGGER.error("Voxtral TTS erreur réseau: %s", err)
            return None, None

        audio_b64: str | None = data.get("audio_data")
        if not audio_b64:
            _LOGGER.error(
                "Voxtral: 'audio_data' absent. Clés reçues: %s", list(data.keys())
            )
            return None, None

        try:
            audio_bytes = base64.b64decode(audio_b64)
        except Exception as err:  # noqa: BLE001
            _LOGGER.error("Voxtral: échec décodage base64: %s", err)
            return None, None

        extension = AUDIO_FORMATS.get(audio_format, "mp3")
        _LOGGER.debug("Voxtral OK: %d octets, ext=%s", len(audio_bytes), extension)
        return extension, audio_bytes
