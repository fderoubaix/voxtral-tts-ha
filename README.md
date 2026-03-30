# Voxtral TTS for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Intégration [Home Assistant](https://www.home-assistant.io/) pour utiliser **[Voxtral TTS](https://mistral.ai/news/voxtral-tts)** de Mistral AI comme moteur de synthèse vocale, en remplacement de Piper ou d'autres solutions locales.

Voxtral offre une voix naturelle et expressive avec clonage vocal zéro-shot, support multilingue (FR, EN, ES, DE, IT, PT, NL, HI, AR) et une latence très faible (~90 ms).

---

## Fonctionnalités

- Synthèse vocale de haute qualité via l'API Mistral Voxtral
- **Clonage vocal zéro-shot** : utilisez votre propre voix (ou une voix créée dans votre compte Mistral) via un `voice_id`
- Support multilingue natif
- Formats audio : MP3, WAV, FLAC, OPUS
- Configuration via l'interface graphique de HA (config flow)
- Options modifiables à chaud (sans redémarrage de HA)

---

## Prérequis

- Home Assistant **2024.1.0** ou plus récent
- Un compte [Mistral AI](https://console.mistral.ai) avec une clé API active
- [HACS](https://hacs.xyz/) installé sur votre instance Home Assistant

---

## Installation

### Via HACS (recommandé)

1. Ouvrez HACS dans Home Assistant.
2. Cliquez sur **Intégrations** → menu ⋮ → **Dépôts personnalisés**.
3. Ajoutez l'URL de ce dépôt : `https://github.com/YOUR_USERNAME/voxtral-tts-ha`  
   Catégorie : **Intégration**.
4. Recherchez **Voxtral TTS** dans HACS et cliquez sur **Télécharger**.
5. Redémarrez Home Assistant.

### Installation manuelle

Copiez le dossier `custom_components/voxtral_tts/` dans le répertoire `custom_components/` de votre configuration Home Assistant, puis redémarrez.

---

## Configuration

1. Allez dans **Paramètres → Appareils & Services → Ajouter une intégration**.
2. Cherchez **Voxtral TTS**.
3. Renseignez les champs :
   - **Clé API Mistral** : générée sur [console.mistral.ai/api-keys](https://console.mistral.ai/api-keys)
   - **Modèle** : `voxtral-mini-tts-2603` (seul modèle disponible actuellement)
   - **Voice ID** *(optionnel)* : ID d'une voix créée dans votre compte Mistral
   - **Format audio** : `mp3` (recommandé), `wav`, `flac`, `opus`

---

## Utilisation dans les automations

Une fois configuré, Voxtral TTS apparaît comme moteur de synthèse vocale dans toutes vos automations.

### Service `tts.speak`

```yaml
service: tts.speak
target:
  entity_id: tts.voxtral_tts
data:
  media_player_entity_id: media_player.salon
  message: "Bonjour ! Il est l'heure de partir."
  language: "fr"
  options:
    voice: "votre-voice-id"        # optionnel, remplace le défaut
    audio_format: "mp3"            # optionnel
```

### Utilisation dans une notification vocale

```yaml
automation:
  - alias: "Annonce arrivée maison"
    trigger:
      - platform: state
        entity_id: person.moi
        to: "home"
    action:
      - service: tts.speak
        target:
          entity_id: tts.voxtral_tts
        data:
          media_player_entity_id: media_player.cuisine
          message: "Bienvenue à la maison !"
          language: fr
```

---

## Clonage vocal avec Voxtral

Pour utiliser votre propre voix, créez-la d'abord via l'API Mistral :

```python
import base64, mistralai

client = mistralai.Mistral(api_key="votre-cle-api")

with open("sample_voix.mp3", "rb") as f:
    sample_b64 = base64.b64encode(f.read()).decode()

voice = client.audio.voices.create(
    name="ma-voix",
    sample_audio=sample_b64,
    sample_filename="sample_voix.mp3",
    languages=["fr", "en"],
)
print(f"Voice ID : {voice.id}")
```

Collez ensuite ce `voice_id` dans la configuration de l'intégration (ou dans les options).

> **Note légale** : Le clonage vocal ne doit être utilisé qu'avec le consentement explicite de la personne dont la voix est clonée, conformément à la politique d'usage de Mistral.

---

## Dépannage

| Problème | Solution |
|---|---|
| `invalid_api_key` | Vérifiez que votre clé API Mistral est active et copiée sans espace |
| Pas de son | Vérifiez que le `media_player` cible est disponible |
| Erreur HTTP 401 | Votre clé API a peut-être expiré — régénérez-en une |
| Erreur HTTP 422 | Le `voice_id` est invalide ou n'existe pas dans votre compte |
| Audio de mauvaise qualité | Essayez le format `wav` pour un audio non compressé |

Les logs complets sont disponibles dans **Paramètres → Journaux système**, en cherchant `voxtral_tts`.

---

## Comparaison Piper vs Voxtral

| | Piper (local) | Voxtral (cloud) |
|---|---|---|
| Confidentialité | ✅ 100% local | ☁️ Cloud Mistral |
| Qualité vocale | Bonne | Excellente |
| Clonage vocal | ❌ | ✅ |
| Multilingue | Limité | ✅ 9 langues |
| Latence | Très faible | ~0.8s (mp3) |
| Coût | Gratuit | Payant (API Mistral) |
| Hors-ligne | ✅ | ❌ |

---

## Licence

MIT – voir [LICENSE](LICENSE).
