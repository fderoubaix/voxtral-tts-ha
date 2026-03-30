"""Constants for Voxtral TTS integration."""

DOMAIN = "voxtral_tts"

# Mistral API  (confirmed via curl test 2026-03)
MISTRAL_API_BASE = "https://api.mistral.ai/v1"
MISTRAL_TTS_ENDPOINT = f"{MISTRAL_API_BASE}/audio/speech"

# Available Voxtral models
MODELS = [
    "voxtral-mini-tts-2603",
]
DEFAULT_MODEL = "voxtral-mini-tts-2603"

# Supported output formats → Home Assistant extension
AUDIO_FORMATS = {
    "mp3": "mp3",
    "wav": "wav",
    "opus": "ogg",
    "flac": "flac",
    "pcm": "wav",   # raw float32 LE – lowest latency for streaming
}
DEFAULT_AUDIO_FORMAT = "mp3"

# Supported languages (ISO 639-1 codes supported by Voxtral)
SUPPORTED_LANGUAGES = ["en", "fr", "es", "pt", "it", "nl", "de", "hi", "ar"]
DEFAULT_LANGUAGE = "fr"

# -----------------------------------------------------------------------
# 20 built-in preset voice IDs exposed through the Mistral cloud API.
# Naming convention confirmed from open-weights model card (HuggingFace)
# and from live API tests (gb_oliver_excited, etc.).
# English voices have extended named variants on the cloud API.
# -----------------------------------------------------------------------

# Voix preset CONFIRMÉES par test direct sur l'API Mistral cloud.
# Seules les voix EN sont confirmées pour l'instant.
# Les autres langues (FR, ES…) n'ont pas de voice_id validé :
# Voxtral génère quand même du bon audio sans voice_id pour ces langues.
PRESET_VOICES: dict[str, list[dict[str, str]]] = {
    "en": [
        {"id": "casual_male",       "name": "Casual Male"},
        {"id": "casual_female",     "name": "Casual Female"},
        {"id": "cheerful_female",   "name": "Cheerful Female"},
        {"id": "neutral_male",      "name": "Neutral Male"},
        {"id": "neutral_female",    "name": "Neutral Female"},
        {"id": "gb_oliver_excited", "name": "Oliver – British Excited"},
        {"id": "gb_oliver_neutral", "name": "Oliver – British Neutral"},
        {"id": "gb_grace_excited",  "name": "Grace – British Excited"},
        {"id": "gb_grace_neutral",  "name": "Grace – British Neutral"},
    ],
    # Autres langues : pas de voice_id validé → liste vide (Voxtral choisit la voix)
}

# Ensemble des IDs valides pour validation rapide avant appel API
VALID_VOICE_IDS: frozenset[str] = frozenset(
    v["id"] for voices in PRESET_VOICES.values() for v in voices
)


# Config entry keys
CONF_API_KEY = "api_key"
CONF_MODEL = "model"
CONF_VOICE_ID = "voice_id"
CONF_AUDIO_FORMAT = "audio_format"

# Options keys
OPTION_VOICE_ID = "voice_id"
OPTION_MODEL = "model"
OPTION_AUDIO_FORMAT = "audio_format"
