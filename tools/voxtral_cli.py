#!/usr/bin/env python3
"""
voxtral_cli.py — Outil CLI pour tester Voxtral TTS depuis le terminal.

Usage :
  export MISTRAL_API_KEY="votre_cle"

  python voxtral_cli.py speak "Bonjour !" --voice gb_oliver_excited -o test.mp3
  python voxtral_cli.py presets

Dépendance : pip install httpx
"""
from __future__ import annotations

import argparse
import base64
import sys
from pathlib import Path

try:
    import httpx
except ImportError:
    print("httpx requis : pip install httpx", file=sys.stderr)
    sys.exit(1)

API_BASE = "https://api.mistral.ai/v1"

PRESET_VOICES: dict[str, list[dict[str, str]]] = {
    "en": [
        {"id": "casual_male",        "name": "Casual Male (EN)"},
        {"id": "casual_female",      "name": "Casual Female (EN)"},
        {"id": "cheerful_female",    "name": "Cheerful Female (EN)"},
        {"id": "neutral_male",       "name": "Neutral Male (EN)"},
        {"id": "neutral_female",     "name": "Neutral Female (EN)"},
        {"id": "gb_oliver_excited",  "name": "Oliver – British Excited (EN)"},
        {"id": "gb_oliver_neutral",  "name": "Oliver – British Neutral (EN)"},
        {"id": "gb_grace_excited",   "name": "Grace – British Excited (EN)"},
        {"id": "gb_grace_neutral",   "name": "Grace – British Neutral (EN)"},
    ],
    "fr": [{"id": "fr_male",   "name": "Homme (FR)"},
           {"id": "fr_female", "name": "Femme (FR)"}],
    "es": [{"id": "es_male",   "name": "Masculino (ES)"},
           {"id": "es_female", "name": "Femenino (ES)"}],
    "de": [{"id": "de_male",   "name": "Männlich (DE)"},
           {"id": "de_female", "name": "Weiblich (DE)"}],
    "it": [{"id": "it_male",   "name": "Maschile (IT)"},
           {"id": "it_female", "name": "Femminile (IT)"}],
    "pt": [{"id": "pt_male",   "name": "Masculino (PT)"},
           {"id": "pt_female", "name": "Feminino (PT)"}],
    "nl": [{"id": "nl_male",   "name": "Mannelijk (NL)"},
           {"id": "nl_female", "name": "Vrouwelijk (NL)"}],
    "hi": [{"id": "hi_male",   "name": "पुरुष (HI)"},
           {"id": "hi_female", "name": "महिला (HI)"}],
    "ar": [{"id": "ar_male",   "name": "ذكر (AR)"},
           {"id": "ar_female", "name": "أنثى (AR)"}],
}


def get_api_key() -> str:
    import os
    key = os.environ.get("MISTRAL_API_KEY", "")
    if not key:
        print("Définissez la variable MISTRAL_API_KEY", file=sys.stderr)
        sys.exit(1)
    return key


def cmd_speak(args: argparse.Namespace) -> None:
    api_key = get_api_key()
    output = Path(args.output)

    payload: dict = {
        "model": args.model,
        "input": args.text,
        "response_format": args.format,
        "stream": False,
    }
    if args.voice:
        payload["voice_id"] = args.voice

    print(f"▶  « {args.text[:70]}{'…' if len(args.text) > 70 else ''} »")
    print(f"   Modèle : {args.model}  |  Voix : {args.voice or '(aucune)'}  |  Format : {args.format}")

    with httpx.Client(timeout=30) as client:
        resp = client.post(
            f"{API_BASE}/audio/speech",
            json=payload,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        )

    if resp.status_code != 200:
        print(f"✗ Erreur HTTP {resp.status_code} : {resp.text}", file=sys.stderr)
        sys.exit(1)

    audio_b64 = resp.json().get("audio_data")
    if not audio_b64:
        print(f"✗ Champ 'audio_data' absent dans la réponse.", file=sys.stderr)
        sys.exit(1)

    output.write_bytes(base64.b64decode(audio_b64))
    print(f"✓ Sauvegardé : {output}")


def cmd_presets(_: argparse.Namespace) -> None:
    print(f"{'Voice ID':<30}  Langue  Nom")
    print("-" * 60)
    for lang, voices in PRESET_VOICES.items():
        for v in voices:
            print(f"{v['id']:<30}  {lang:<6}  {v['name']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Voxtral TTS CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_speak = sub.add_parser("speak", help="Synthétiser du texte en audio")
    p_speak.add_argument("text", help="Texte à synthétiser")
    p_speak.add_argument("-v", "--voice", default="", help="voice_id preset")
    p_speak.add_argument("-o", "--output", default="output.mp3")
    p_speak.add_argument("-f", "--format", default="mp3",
                         choices=["mp3", "wav", "flac", "opus", "pcm"])
    p_speak.add_argument("-m", "--model", default="voxtral-mini-tts-2603")
    p_speak.set_defaults(func=cmd_speak)

    p_presets = sub.add_parser("presets", help="Lister les voix preset disponibles")
    p_presets.set_defaults(func=cmd_presets)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
