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
PRESET_VOICES: dict[str, list[dict[str, str]]] = {
    "en": [
        {"id": "casual_male",     "name": "Casual Male (EN)"},
        {"id": "casual_female",   "name": "Casual Female (EN)"},
        {"id": "cheerful_female", "name": "Cheerful Female (EN)"},
        {"id": "neutral_male",    "name": "Neutral Male (EN)"},
        {"id": "neutral_female",  "name": "Neutral Female (EN)"},
        # British dialect variants (confirmed on cloud API)
        {"id": "gb_oliver_excited",  "name": "Oliver – British Excited (EN)"},
        {"id": "gb_oliver_neutral",  "name": "Oliver – British Neutral (EN)"},
        {"id": "gb_grace_excited",   "name": "Grace – British Excited (EN)"},
        {"id": "gb_grace_neutral",   "name": "Grace – British Neutral (EN)"},
    ],
    "fr": [
        {"id": "fr_male",   "name": "Homme (FR)"},
        {"id": "fr_female", "name": "Femme (FR)"},
    ],
    "es": [
        {"id": "es_male",   "name": "Masculino (ES)"},
        {"id": "es_female", "name": "Femenino (ES)"},
    ],
    "de": [
        {"id": "de_male",   "name": "Männlich (DE)"},
        {"id": "de_female", "name": "Weiblich (DE)"},
    ],
    "it": [
        {"id": "it_male",   "name": "Maschile (IT)"},
        {"id": "it_female", "name": "Femminile (IT)"},
    ],
    "pt": [
        {"id": "pt_male",   "name": "Masculino (PT)"},
        {"id": "pt_female", "name": "Feminino (PT)"},
    ],
    "nl": [
        {"id": "nl_male",   "name": "Mannelijk (NL)"},
        {"id": "nl_female", "name": "Vrouwelijk (NL)"},
    ],
    "hi": [
        {"id": "hi_male",   "name": "पुरुष (HI)"},
        {"id": "hi_female", "name": "महिला (HI)"},
    ],
    "ar": [
        {"id": "ar_male",   "name": "ذكر (AR)"},
        {"id": "ar_female", "name": "أنثى (AR)"},
    ],
}


# Config entry keys
CONF_API_KEY = "api_key"
CONF_MODEL = "model"
CONF_VOICE_ID = "voice_id"
CONF_AUDIO_FORMAT = "audio_format"

# Options keys
OPTION_VOICE_ID = "voice_id"
OPTION_MODEL = "model"
OPTION_AUDIO_FORMAT = "audio_format"
