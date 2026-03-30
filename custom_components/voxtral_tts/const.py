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

# Voix preset CONFIRMÉES par test direct sur l'API Mistral cloud (2026-03).
# Les voix EN (Paul), GB (Oliver, Jane) et FR (Marie) sont validées.
PRESET_VOICES: dict[str, list[dict[str, str]]] = {
    "en": [
        # Paul - US English (8 variants)
        {"id": "en_paul_neutral",     "name": "Paul - Neutral"},
        {"id": "en_paul_happy",       "name": "Paul - Happy"},
        {"id": "en_paul_sad",         "name": "Paul - Sad"},
        {"id": "en_paul_excited",     "name": "Paul - Excited"},
        {"id": "en_paul_confident",   "name": "Paul - Confident"},
        {"id": "en_paul_cheerful",    "name": "Paul - Cheerful"},
        {"id": "en_paul_frustrated",  "name": "Paul - Frustrated"},
        {"id": "en_paul_angry",       "name": "Paul - Angry"},
        
        # Oliver - British English (7 variants)
        {"id": "gb_oliver_neutral",   "name": "Oliver - Neutral (British)"},
        {"id": "gb_oliver_excited",   "name": "Oliver - Excited (British)"},
        {"id": "gb_oliver_cheerful",  "name": "Oliver - Cheerful (British)"},
        {"id": "gb_oliver_confident", "name": "Oliver - Confident (British)"},
        {"id": "gb_oliver_curious",   "name": "Oliver - Curious (British)"},
        {"id": "gb_oliver_sad",       "name": "Oliver - Sad (British)"},
        {"id": "gb_oliver_angry",     "name": "Oliver - Angry (British)"},
        
        # Jane - British English (9 variants)
        {"id": "gb_jane_neutral",     "name": "Jane - Neutral (British)"},
        {"id": "gb_jane_confident",   "name": "Jane - Confident (British)"},
        {"id": "gb_jane_curious",     "name": "Jane - Curious (British)"},
        {"id": "gb_jane_confused",    "name": "Jane - Confused (British)"},
        {"id": "gb_jane_frustrated",  "name": "Jane - Frustrated (British)"},
        {"id": "gb_jane_sad",         "name": "Jane - Sad (British)"},
        {"id": "gb_jane_shameful",    "name": "Jane - Shameful (British)"},
        {"id": "gb_jane_jealousy",    "name": "Jane - Jealousy (British)"},
        {"id": "gb_jane_sarcasm",     "name": "Jane - Sarcasm (British)"},
    ],
    "fr": [
        # Marie - French (6 variants)
        {"id": "fr_marie_neutral",    "name": "Marie - Neutre"},
        {"id": "fr_marie_happy",      "name": "Marie - Joyeuse"},
        {"id": "fr_marie_excited",    "name": "Marie - Excitée"},
        {"id": "fr_marie_curious",    "name": "Marie - Curieuse"},
        {"id": "fr_marie_sad",        "name": "Marie - Triste"},
        {"id": "fr_marie_angry",      "name": "Marie - En colère"},
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
