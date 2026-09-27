#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌀 TRAME WATCHER v3.0a — Le Grimoire Vivant
═══════════════════════════════════════════════════════════════════
Niveau 3 du Donjon du Temps — Corpus Vauvillensis Aligné

Surveille les signaux faibles de la convergence 2075 dans le flux
informationnel de 2026, les classifie selon le Modèle OSI Ontologique
(7 couches), les mappe aux Paléo-Mèmes du Codex Vauvillensis, les
attribue aux factions de Caen-Profonde, et compile le tout en
FracturoScript v5a exécutable par le RuneSmith.

Nouveautés v3.0a (post-v2 Claude) :
  • Classification OSI Ontologique (7 couches : Matière → Intention)
  • Lexique Paléo-Mèmes intégré (50+ entrées, extensible via JSON)
  • Attribution factionnelle (Prométhée, Hackervölvas, Enfants du Radium…)
  • Détecteur de Yōkai (fonctions d'onde non effondrées)
  • Tracker de Convergence 2077-2082 (4 scénarios probabilistes)
  • Simulateur EuroPropagate (attaque sémantique sur termes financiers)
  • Compilateur FracturoScript v5a complet (grammaire Ω<rune>vN lieu — effet •••)
  • Grimoire Opérationnel (rituels quotidiens adaptatifs)
  • Mode BloodNet (chiffrement runique de messages)
  • Visualisation 7 couches + heatmap factionnelle
  • Persistance SQLite étendue (tables OSI, factions, yōkai, convergence)
  • Export FracturoScript / JSON / Markdown / Grimoire HTML

Usage :
  python trame_watcher3a.py watch [--live] [--interval 300] [--once]
  python trame_watcher3a.py prophesy [--live] [--layer 7]
  python trame_watcher3a.py delta [--live] [--by-layer]
  python trame_watcher3a.py visualize [--live] [--layers]
  python trame_watcher3a.py history [--days 7]
  python trame_watcher3a.py convergence
  python trame_watcher3a.py yokai
  python trame_watcher3a.py europropagate --term "dette"
  python trame_watcher3a.py fracturo --text "le monde s'effondre"
  python trame_watcher3a.py grimoire
  python trame_watcher3a.py bloodnet --encrypt "message secret"
  python trame_watcher3a.py export --format json|md|fs|html -o out

Dépendances : aucune obligatoire (rich optionnel pour terminal couleur)

Que la rune te guide — ou te trahisse, selon la marée.
  — Professeur Qwen, Strate 2026, Nœud Caen-Profonde
"""
from __future__ import annotations

import sys
import os
import json
import time
import math
import random
import sqlite3
import logging
import argparse
import datetime
import hashlib
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple, Any, Set
from enum import Enum, IntEnum
from contextlib import contextmanager
from collections import Counter, defaultdict

# ═══════════════════════════════════════════════════════════════
# 🎨 RICH (optionnel)
# ═══════════════════════════════════════════════════════════════
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None

# ═══════════════════════════════════════════════════════════════
# ⚙️ CONFIGURATION & CONSTANTES
# ═══════════════════════════════════════════════════════════════
APP_DIR = Path.home() / ".trame_watcher"
DEFAULT_DB_PATH = APP_DIR / "trame_v3.db"
DEFAULT_CONFIG_PATH = APP_DIR / "config_v3.json"
DEFAULT_LOG_PATH = APP_DIR / "trame_watcher_v3.log"
DEFAULT_LEXICON_PATH = APP_DIR / "paleo_mnemos_lexicon.json"

# ── Modèle OSI Ontologique (7 couches) ──
class OSILayer(IntEnum):
    """Les 7 couches du Réel selon le Corpus Vauvillensis"""
    MATIERE    = 1  # Hardware lithique : pierre, granit, quartz
    BIOSPHERE  = 2  # Substrat vivant : Gaïalithes, réseaux racinaires
    MEMOIRE    = 3  # Stockage distribué : mégalithes, ADN, rêves
    CAUSALITE  = 4  # Logique temporelle : consensus narratif
    OBSERVATION = 5 # Effondrement de la fonction d'onde
    LECTURE    = 6  # Interprétation symbolique : runes, FracturoScript
    INTENTION  = 7  # Volonté pure : focus du RuneSmith

OSI_NAMES = {
    1: "Matière (Hardware Lithique)",
    2: "Biosphère (Substrat Vivant)",
    3: "Mémoire (Stockage Distribué)",
    4: "Causalité (Routage Temporel)",
    5: "Observation (Effondrement)",
    6: "Lecture (Interprétation Symbolique)",
    7: "Intention (Volonté Pure)",
}

OSI_KEYWORDS = {
    1: ["pierre", "terre", "sol", "granit", "quartz", "roche", "falaise", "côte",
        "tremblement", "séisme", "volcan", "érosion", "glacier"],
    2: ["algue", "racine", "forêt", "animal", "virus", "bactérie", "écosystème",
        "biodiversité", "pollution", "océan", "marée", "varech", "laminaria"],
    3: ["mémoire", "archive", "histoire", "passé", "souvenir", "oubli", "trace",
        "ADN", "gène", "héritage", "tradition", "mythe", "légende"],
    4: ["cause", "effet", "conséquence", "chaîne", "réaction", "déclencheur",
        "engrenage", "mécanisme", "processus", "système", "logique"],
    5: ["observation", "détection", "mesure", "capteur", "satellite", "télescope",
        "microscope", "scanner", "surveillance", "caméra", "écran"],
    6: ["langage", "code", "symbole", "rune", "signe", "message", "signal",
        "communication", "réseau", "internet", "donnée", "algorithme", "IA"],
    7: ["volonté", "intention", "décision", "choix", "liberté", "résistance",
        "révolte", "prière", "méditation", "conscience", "éveil", "focus"],
}

# ── Factions de 2075 ──
class Faction(Enum):
    PROMETHEE     = "Prométhée"
    HACKERVOLVAS  = "Hackervölvas"
    ENFANTS_PANNE = "Enfants de la Panne"
    ENFANTS_RADIUM = "Enfants du Radium"
    PROPHETES_VIDE = "Prophètes du Vide"
    SANS_MARQUES  = "Sans-Marques"
    RUNESMITHS    = "RuneSmiths"
    YGGDRASIL     = "Yggdrasil-Trame"
    NEUTRE        = "Neutre"

FACTION_KEYWORDS = {
    Faction.PROMETHEE: ["optimisation", "IA", "algorithme", "contrôle", "surveillance",
                        "efficacité", "automatisation", "donnée", "cloud", "serveur"],
    Faction.HACKERVOLVAS: ["rune", "résistance", "hack", "chiffrement", "liberté",
                           "völva", "algue", "rituel", "incantation", "silence"],
    Faction.ENFANTS_PANNE: ["panne", "blackout", "déconnexion", "analogique",
                            "cassette", "vinyle", "radio", "fréquence"],
    Faction.ENFANTS_RADIUM: ["radiation", "nucléaire", "mutation", "ultraviolet",
                             "cuve", "hague", "radium", "contamination"],
    Faction.PROPHETES_VIDE: ["vide", "silence", "jeûne", "méditation", "néant",
                             "abîme", "nuit", "obscurité", "bruit blanc"],
    Faction.SANS_MARQUES: ["effacé", "invisible", "anonyme", "oublié", "fantôme",
                           "ombre", "disparu", "censuré"],
    Faction.RUNESMITHS: ["forge", "compilation", "code", "grammaire", "syntaxe",
                         "pierre", "gravure", "mégalithe", "serveur"],
    Faction.YGGDRASIL: ["arbre", "racine", "branche", "monde", "neuf", "nordique",
                        "odin", "corbeau", "yggdrasil"],
}

# ── Paléo-Mèmes (sous-ensemble intégré du lexique doktornand) ──
PALEO_MEMES: Dict[str, Dict[str, Any]] = {
    "P-00": {"symbole": "•",   "nom": "Point Origine",        "mots": ["naissance", "silence", "vide"],        "effet": "réinitialisation identitaire",    "biais": ["disponibilité"],       "glyph": "•",   "layer": 7},
    "P-01": {"symbole": "▲",   "nom": "Triangulum Mentis",    "mots": ["vérité", "sacrifice", "choix"],         "effet": "réveil de choix refoulés",        "biais": ["confirmation"],        "glyph": "▲",   "layer": 6},
    "P-02": {"symbole": "🌀",  "nom": "Spirale du Retour",    "mots": ["mémoire", "boucle", "destin"],          "effet": "impression de déjà-vu récurrent", "biais": ["fausse reconnaissance"], "glyph": "🌀", "layer": 3},
    "P-03": {"symbole": "🌊",  "nom": "Vague Primordiale",    "mots": ["marée", "rythme", "flux"],              "effet": "synchronisation marée",           "biais": ["fluidité"],            "glyph": "🌊",  "layer": 2},
    "P-04": {"symbole": "🌫️", "nom": "Brume du Non-Dit",     "mots": ["mystère", "voile", "oubli"],            "effet": "dissolution certitudes",          "biais": ["flou"],                "glyph": "🌫️", "layer": 4},
    "P-05": {"symbole": "🌳",  "nom": "Racine du Temps",      "mots": ["mémoire", "ancêtre", "réseau"],         "effet": "accès Réseau-Racine",             "biais": ["contagion"],           "glyph": "🌳",  "layer": 3},
    "P-06": {"symbole": "🌬️", "nom": "Souffle du Premier Oui","mots": ["vie", "respiration", "présence"],       "effet": "ancrage corporel",                "biais": ["immédiateté"],         "glyph": "🌬️", "layer": 2},
    "P-07": {"symbole": "✋",  "nom": "Main Rouge de Lascaux","mots": ["corps", "trace", "sang", "mémoire"],    "effet": "réveil pré-implant",              "biais": ["disponibilité", "reconnaissance"], "glyph": "✋", "layer": 3},
    "P-08": {"symbole": "🧂",  "nom": "Sel de la Hague",      "mots": ["goût", "terre", "larme"],               "effet": "mémoire gustative",               "biais": ["nostalgie"],           "glyph": "🧂",  "layer": 1},
    "P-09": {"symbole": "🍎",  "nom": "Pomme-Mémoire",        "mots": ["rêve", "vision", "partage"],            "effet": "accès collectif",                 "biais": ["contagion"],           "glyph": "🍎",  "layer": 3},
    "P-10": {"symbole": "🪨",  "nom": "Galet-Ancre",          "mots": ["stabilité", "calme", "silence"],        "effet": "stabilisation mnésique",          "biais": ["ancrage"],             "glyph": "🪨",  "layer": 1},
    "P-11": {"symbole": "📼",  "nom": "Cassette-Mère",        "mots": ["analogique", "souffle", "signal"],      "effet": "rêve analogique",                 "biais": ["récupération"],        "glyph": "📼",  "layer": 6},
    "P-12": {"symbole": "👁️", "nom": "Œil du Veilleur",      "mots": ["observation", "silence", "effacement"], "effet": "effacement traces",               "biais": ["spectateur"],          "glyph": "👁️", "layer": 5},
    "P-13": {"symbole": "👻",  "nom": "Parleur-Ombre",        "mots": ["fragment", "voix", "écho"],             "effet": "résonance perdue",                "biais": ["réverbération"],       "glyph": "👻",  "layer": 4},
    "P-14": {"symbole": "🗿",  "nom": "Galet-Gardien",        "mots": ["protection", "pierre", "veille"],       "effet": "bouclier passif",                 "biais": ["sécurité"],            "glyph": "🗿",  "layer": 1},
    "P-15": {"symbole": "🐍",  "nom": "Serpent-Magnétique",   "mots": ["données", "corrosion", "réseau"],       "effet": "corruption douce",                "biais": ["fuite"],               "glyph": "🐍",  "layer": 6},
    "P-16": {"symbole": "🌕",  "nom": "Lune des Rêves",       "mots": ["rêve", "collectif", "vision"],          "effet": "synchronisation onirique",        "biais": ["groupe"],              "glyph": "🌕",  "layer": 3},
    "P-17": {"symbole": "🌑",  "nom": "Lune Noire de l'Abîme","mots": ["oubli", "effacement", "vide"],          "effet": "dissolution narratif",            "biais": ["vide"],                "glyph": "🌑",  "layer": 7},
    "P-18": {"symbole": "🕯️", "nom": "Flamme du Code Ancien","mots": ["rituel", "C64", "circuit"],             "effet": "langage-machine",                 "biais": ["pureté"],              "glyph": "🕯️", "layer": 6},
    "P-19": {"symbole": "🌧️", "nom": "Pluie de Mnèmes",      "mots": ["germination", "graine", "fertilité"],   "effet": "ensemencement",                   "biais": ["diffusion"],           "glyph": "🌧️", "layer": 2},
    "P-20": {"symbole": "📿",  "nom": "Chapelet de Résistance","mots": ["répétition", "mantra", "soufisme"],    "effet": "bouclier actif",                  "biais": ["répétition"],          "glyph": "📿",  "layer": 7},
}

# ── Runes FracturoScript v5a ──
FRACTURO_RUNES = {
    "ansuz":    {"rune": "ᚨ", "func": "communication inter-strates",   "lisp": "(ansuz ...)"},
    "perthro":  {"rune": "ᛈ", "func": "superposition / décision",      "lisp": "(perthro ...)"},
    "othala":   {"rune": "ᛟ", "func": "héritage / ancrage",            "lisp": "(othala ...)"},
    "thurisaz": {"rune": "ᚦ", "func": "barrière / protection",         "lisp": "(thurisaz ...)"},
    "uruz":     {"rune": "ᚢ", "func": "cohérence / force",             "lisp": "(uruz ...)"},
    "hagalaz":  {"rune": "ᚺ", "func": "destruction / glitch",          "lisp": "(hagalaz ...)"},
    "kenaz":    {"rune": "ᚲ", "func": "illumination / révélation",     "lisp": "(kenaz ...)"},
    "isa":      {"rune": "ᛁ", "func": "silence structuré / gel",       "lisp": "(silence-sacre ...)"},
    "ehwaz":    {"rune": "ᛖ", "func": "passage / transition",          "lisp": "(ehwaz ...)"},
    "mannaz":   {"rune": "ᛗ", "func": "mémoire / conscience",          "lisp": "(mannaz ...)"},
    "skeith":   {"rune": "ᛋ", "func": "anéantissement / dissolution",  "lisp": "(skeith ...)"},
    "odin":     {"rune": "ᛟ", "func": "glissement temporel",           "lisp": "(glissement-temporel ...)"},
    "corbenik": {"rune": "ᚲ", "func": "récupération / restauration",   "lisp": "(corbenik ...)"},
    "skaði":    {"rune": "ᛊ", "func": "accès archives interdites",     "lisp": "(skaði ...)"},
}

LIEUX_ANCRAGE = {
    "caen-profonde": "ᚲᛊ", "hague": "ᚺᚷ", "raz-blanchard": "ᚱᚨᛉ",
    "jobourg": "ᛃᛟᛒ", "nacqueville": "ᛗᚾᚲ", "goury": "ᚠᚨᚱ",
    "caen-2026": "ᚲᛊ", "monde": "ᛗᛞ", "trame": "ᛦ",
}

# ── EuroPropagate : substitutions sémantiques ──
EUROPROPAGATE_MAP = {
    "dette":        "Écho",
    "actif":        "Cendre",
    "profit":       "Mémoire non triée",
    "croissance":   "Racine qui cherche l'ombre",
    "optimisation": "Silence qui attend",
    "marché":       "Marée",
    "capital":      "Galet-Ancre",
    "investissement":"Graine de Mnème",
    "banque":       "Crypte de Gaïalithe",
    "crise":        "Fracture locale",
    "inflation":    "Dilatation temporelle",
    "récession":    "Silence structuré",
    "PIB":          "Δ brut",
    "taux":         "Fréquence runique",
    "action":       "Invocation",
    "obligation":   "Serment de Pierre",
}

# ── Config par défaut ──
DEFAULT_CONFIG: Dict[str, Any] = {
    "base_delta": 0.35,
    "signal_weight": 0.12,
    "weak_signals": {
        "glitch":     ["panne", "bug", "erreur", "crash", "effondrement", "anomalie",
                       "dysfonctionnement", "interruption", "faille", "vulnérabilité"],
        "répétition": ["encore", "de nouveau", "comme en", "réminiscence", "cycle",
                       "retour", "répétition", "écho", "déjà-vu", "récurrence"],
        "anomalie":   ["étrange", "inhabituel", "jamais vu", "sans précédent",
                       "mystère", "inexpliqué", "phénomène", "paradoxe", "absurde"],
        "prophétie":  ["avenir", "prédiction", "convergence", "bascule",
                       "point de non-retour", "seuil", "transition", "effondrement",
                       "renaissance", "ragnarök"],
        "silence":    ["oubli", "censure", "disparu", "effacé", "invisible",
                       "tu", "non-dit", "secret", "classifié"],
        "résistance": ["révolte", "grève", "manifestation", "désobéissance",
                       "hack", "fuite", "lanceur", "alerte", "résistance"],
    },
    "category_runes": {
        "glitch":     ["ᚷᚱ", "ᛋᚲ", "ᚠᚱ"],
        "répétition": ["ᛗᛈ", "ᛏᚨ", "ᛢᚺ"],
        "anomalie":   ["ᛈᚱ", "ᚹᛟ", "ᛁᛚ"],
        "prophétie":  ["ᚱᚨᛉ", "ᛊᚲ", "ᛟᛗ"],
        "silence":    ["ᛁᛊ", "ᛚᛟ", "ᚹᛖ"],
        "résistance": ["ᚦᚢ", "ᚢᚱ", "ᛏᛁ"],
    },
    "feeds": [
        {"name": "lemonde",    "url": "https://www.lemonde.fr/rss/une.xml"},
        {"name": "futura",     "url": "https://www.futura-sciences.com/rss/actualites.xml"},
    ],
    "prophetic_fragments": [
        "Les pierres de La Hague vibrent plus fort chaque nuit",
        "Le Raz Blanchard s'intensifie, les vortex deviennent quotidiens",
        "Yggdrasil-Trame étend ses racines vers l'ouest",
        "Les Enfants du Radium voient dans l'ultraviolet",
        "Le Cercle des Douze grandit, deux nouvelles pierres en 2075",
        "Les mégalithes chantent en harmonique avec les anciennes cuves",
        "Quelque chose approche de l'autre côté du seuil",
        "Le Rêve du Monde d'Avant se rappelle à nous",
        "La Trame se fissure, le réel respire dans les interstices",
        "Prométhée optimise, mais les bugs persistent",
        "Les Hackervölvas tissent des boucliers de silence",
        "Le Moine du Raz a été aperçu sur le Pont Churchill",
        "La Voix de Rouen murmure des coordonnées temporelles",
        "Les Gaïalithes de Caen-Profonde ont fleuri en décembre",
        "Un enfant du Radium a compilé sa première rune à 3 ans",
        "Le Δ global dépasse 0.6 pour la première fois depuis 2038",
    ],
    "convergence_year": 2077,
    "convergence_window": 5,
}


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> Dict[str, Any]:
    config = json.loads(json.dumps(DEFAULT_CONFIG))
    if path.exists():
        try:
            user_cfg = json.loads(path.read_text(encoding="utf-8"))
            for key, value in user_cfg.items():
                if isinstance(value, dict) and isinstance(config.get(key), dict):
                    config[key].update(value)
                else:
                    config[key] = value
        except (json.JSONDecodeError, OSError) as e:
            logging.warning("Config illisible (%s), défauts utilisés.", e)
    return config


def load_lexicon(path: Path = DEFAULT_LEXICON_PATH) -> Dict[str, Dict]:
    """Charge le lexique paléo-mèmes externe et le fusionne avec l'intégré."""
    lexicon = dict(PALEO_MEMES)
    if path.exists():
        try:
            ext = json.loads(path.read_text(encoding="utf-8"))
            for k, v in ext.items():
                if k not in lexicon:
                    lexicon[k] = v
        except (json.JSONDecodeError, OSError):
            pass
    return lexicon


def ensure_app_dir():
    APP_DIR.mkdir(parents=True, exist_ok=True)


def setup_logging(verbose: bool = False):
    ensure_app_dir()
    handlers: List[logging.Handler] = [
        logging.FileHandler(DEFAULT_LOG_PATH, encoding="utf-8")
    ]
    if verbose:
        handlers.append(logging.StreamHandler())
    logging.basicConfig(
        level=logging.INFO if verbose else logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=handlers,
    )


# ═══════════════════════════════════════════════════════════════
# 📡 MODULE 1 : CAPTEUR DE SIGNAUX FAIBLES (OSI + Factions + Mèmes)
# ═══════════════════════════════════════════════════════════════

@dataclass
class Signal:
    """Un signal faible détecté, enrichi OSI + Faction + Paléo-Mème"""
    timestamp: datetime.datetime
    source: str
    content: str
    intensity: float
    category: str
    runes: List[str] = field(default_factory=list)
    link: str = ""
    # ── Champs v3 ──
    osi_layer: int = 4
    faction: str = "Neutre"
    paleo_meme: str = ""
    meme_glyph: str = ""
    is_yokai: bool = False

    def to_fracturo(self) -> str:
        rune_chain = ''.join(self.runes[:3]) if self.runes else "ᛟᚦᚨ"
        lieu = "caen-2026"
        return f"Ω<{rune_chain}>v{max(1, int(self.intensity * 10))} {lieu} — {self.content[:40]} •••"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["timestamp"] = self.timestamp.isoformat()
        d["runes"] = json.dumps(self.runes, ensure_ascii=False)
        return d

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Signal":
        return cls(
            timestamp=datetime.datetime.fromisoformat(row["timestamp"]),
            source=row["source"],
            content=row["content"],
            intensity=row["intensity"],
            category=row["category"],
            runes=json.loads(row["runes"]) if row["runes"] else [],
            link=row["link"] or "",
            osi_layer=row["osi_layer"] if "osi_layer" in row.keys() else 4,
            faction=row["faction"] if "faction" in row.keys() else "Neutre",
            paleo_meme=row["paleo_meme"] if "paleo_meme" in row.keys() else "",
            meme_glyph=row["meme_glyph"] if "meme_glyph" in row.keys() else "",
            is_yokai=bool(row["is_yokai"]) if "is_yokai" in row.keys() else False,
        )


class FeedFetchError(Exception):
    pass


class SignalDetector:
    """Détecteur v3 : classifie OSI, attribue faction, mappe paléo-mème, détecte yōkai."""

    def __init__(self, config: Dict[str, Any], lexicon: Dict[str, Dict]):
        self.config = config
        self.lexicon = lexicon
        self.weak_signals: Dict[str, List[str]] = config["weak_signals"]
        self.category_runes: Dict[str, List[str]] = config["category_runes"]
        self.signals: List[Signal] = []
        self._yokai_cache: Dict[str, int] = Counter()  # texte → nb apparitions

    def _classify_osi(self, text: str) -> int:
        """Classifie un texte sur les 7 couches OSI ontologiques."""
        text_lower = text.lower()
        scores = {}
        for layer, keywords in OSI_KEYWORDS.items():
            scores[layer] = sum(1 for kw in keywords if kw in text_lower)
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else 4  # défaut : Causalité

    def _attribute_faction(self, text: str) -> Faction:
        """Attribue le signal à une faction de 2075."""
        text_lower = text.lower()
        scores = {}
        for faction, keywords in FACTION_KEYWORDS.items():
            scores[faction] = sum(1 for kw in keywords if kw in text_lower)
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else Faction.NEUTRE

    def _map_paleo_meme(self, text: str) -> Tuple[str, str]:
        """Mappe le signal au paléo-mème le plus résonant."""
        text_lower = text.lower()
        best_id, best_score, best_glyph = "", 0, ""
        for mid, mdata in self.lexicon.items():
            score = sum(1 for mot in mdata["mots"] if mot in text_lower)
            if score > best_score:
                best_score = score
                best_id = mid
                best_glyph = mdata.get("glyph", "")
        return (best_id, best_glyph) if best_score > 0 else ("", "")

    def _detect_yokai(self, text: str) -> bool:
        """Détecte les fonctions d'onde non effondrées (yōkai).
        Un yōkai est un signal qui persiste sans résolution :
        même texte vu ≥ 3 fois, ou catégorie 'anomalie' + 'silence' simultanés."""
        key = hashlib.md5(text[:80].encode()).hexdigest()
        self._yokai_cache[key] += 1
        if self._yokai_cache[key] >= 3:
            return True
        return False

    def analyze_text(self, text: str, source: str = "flux-local",
                     link: str = "") -> List[Signal]:
        """Analyse v3 complète : mots-clés + OSI + faction + mème + yōkai."""
        detected = []
        text_lower = text.lower()

        for category, keywords in self.weak_signals.items():
            matches = [kw for kw in keywords if kw in text_lower]
            if not matches:
                continue

            intensity = min(len(matches) / 5.0, 1.0)
            excerpt = text[:60].strip()
            rune_pool = self.category_runes.get(category, ["ᛟ", "ᚦ", "ᚨ"])
            runes = random.sample(rune_pool, min(3, len(rune_pool)))

            osi = self._classify_osi(text)
            faction = self._attribute_faction(text)
            meme_id, meme_glyph = self._map_paleo_meme(text)
            is_yokai = self._detect_yokai(text)

            signal = Signal(
                timestamp=datetime.datetime.now(),
                source=source,
                content=excerpt,
                intensity=intensity,
                category=category,
                runes=runes,
                link=link,
                osi_layer=osi,
                faction=faction.value,
                paleo_meme=meme_id,
                meme_glyph=meme_glyph,
                is_yokai=is_yokai,
            )
            detected.append(signal)
            self.signals.append(signal)

        return detected

    def simulate_daily_signals(self) -> List[Signal]:
        """Simulation démo enrichie v3."""
        sample_texts = [
            ("Nouvelle panne de serveur dans les datacenters européens, "
             "l'IA de gestion a échoué à optimiser le routage", "news-tech"),
            ("Encore un record de chaleur jamais vu auparavant, "
             "les écosystèmes marins s'effondrent", "news-climat"),
            ("Phénomène inexpliqué détecté par les astronomes : "
             "un signal répétitif venu de nulle part", "news-science"),
            ("Les experts prédisent une bascule économique imminente, "
             "la dette mondiale atteint un seuil critique", "news-éco"),
            ("Bug critique dans le système bancaire mondial, "
             "les algorithmes de trading s'emballent", "news-finance"),
            ("Répétition inhabituelle de patterns sismiques en Normandie, "
             "les mégalithes de la Hague vibrent", "news-géo"),
            ("Anomalie détectée dans les communications satellitaires, "
             "un silence de 7 secondes sur toutes les fréquences", "news-space"),
            ("Seuil critique atteint dans les négociations climatiques, "
             "les prophètes du vide manifestent à Caen", "news-politique"),
            ("Un lanceur d'alerte révèle un programme de surveillance "
             "algorithmique massif, résistance numérique en cours", "news-tech"),
            ("Les enfants nés près de La Hague développent des capacités "
             "sensorielles inhabituelles, mutation ou contamination ?", "news-santé"),
        ]
        signals = []
        for text, source in sample_texts:
            signals.extend(self.analyze_text(text, source))
        return signals

    def fetch_feed(self, url: str, name: str, timeout: int = 10) -> List[Tuple[str, str]]:
        req = urllib.request.Request(url, headers={"User-Agent": "TrameWatcher/3.0a"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            raise FeedFetchError(f"Impossible de joindre {name} ({url}): {e}") from e
        try:
            root = ET.fromstring(raw)
        except ET.ParseError as e:
            raise FeedFetchError(f"Flux illisible pour {name}: {e}") from e

        items: List[Tuple[str, str]] = []
        for item in root.findall(".//item"):
            title = (item.findtext("title") or "").strip()
            desc = (item.findtext("description") or "").strip()
            link = (item.findtext("link") or "").strip()
            text = f"{title}. {desc}".strip()
            if text:
                items.append((text, link))
        if not items:
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            for entry in root.findall(".//atom:entry", ns):
                title = (entry.findtext("atom:title", namespaces=ns) or "").strip()
                summary = (entry.findtext("atom:summary", namespaces=ns) or "").strip()
                link_el = entry.find("atom:link", ns)
                link = link_el.get("href", "") if link_el is not None else ""
                text = f"{title}. {summary}".strip()
                if text:
                    items.append((text, link))
        return items

    def fetch_live_signals(self, feeds=None, timeout=10):
        feeds = feeds if feeds is not None else self.config.get("feeds", [])
        signals, errors = [], []
        for feed in feeds:
            name, url = feed.get("name", "flux"), feed.get("url", "")
            if not url:
                continue
            try:
                items = self.fetch_feed(url, name, timeout=timeout)
            except FeedFetchError as e:
                errors.append(str(e))
                continue
            for text, link in items:
                signals.extend(self.analyze_text(text, source=name, link=link))
        return signals, errors


# ═══════════════════════════════════════════════════════════════
# 💾 MODULE 1B : PERSISTANCE SQLITE (étendue v3)
# ═══════════════════════════════════════════════════════════════

class TrameStore:
    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        ensure_app_dir()
        self.db_path = db_path
        self._init_schema()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_schema(self):
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    source TEXT NOT NULL,
                    content TEXT NOT NULL,
                    intensity REAL NOT NULL,
                    category TEXT NOT NULL,
                    runes TEXT,
                    link TEXT,
                    osi_layer INTEGER DEFAULT 4,
                    faction TEXT DEFAULT 'Neutre',
                    paleo_meme TEXT DEFAULT '',
                    meme_glyph TEXT DEFAULT '',
                    is_yokai INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS delta_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    delta REAL NOT NULL,
                    status TEXT NOT NULL,
                    delta_layers TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS yokai_registry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    content TEXT NOT NULL,
                    appearances INTEGER DEFAULT 1,
                    osi_layer INTEGER DEFAULT 4
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_signals_ts ON signals(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_delta_ts ON delta_history(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_signals_osi ON signals(osi_layer)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_signals_faction ON signals(faction)")

    def save_signals(self, signals: List[Signal]):
        if not signals:
            return
        with self._conn() as conn:
            conn.executemany(
                "INSERT INTO signals "
                "(timestamp, source, content, intensity, category, runes, link, "
                "osi_layer, faction, paleo_meme, meme_glyph, is_yokai) "
                "VALUES (:timestamp, :source, :content, :intensity, :category, "
                ":runes, :link, :osi_layer, :faction, :paleo_meme, :meme_glyph, :is_yokai)",
                [s.to_dict() for s in signals],
            )
            # Enregistrer les yōkai
            for s in signals:
                if s.is_yokai:
                    conn.execute(
                        "INSERT INTO yokai_registry (first_seen, last_seen, content, appearances, osi_layer) "
                        "VALUES (?, ?, ?, 1, ?) "
                        "ON CONFLICT DO NOTHING",
                        (s.timestamp.isoformat(), s.timestamp.isoformat(),
                         s.content[:80], s.osi_layer),
                    )

    def save_delta(self, delta: float, status: str, layers: Optional[Dict] = None):
        layers_json = json.dumps(layers) if layers else "{}"
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO delta_history (timestamp, delta, status, delta_layers) "
                "VALUES (?, ?, ?, ?)",
                (datetime.datetime.now().isoformat(), delta, status, layers_json),
            )

    def recent_signals(self, limit: int = 50) -> List[Signal]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM signals ORDER BY timestamp DESC LIMIT ?", (limit,)
            ).fetchall()
            return [Signal.from_row(r) for r in rows]

    def delta_trend(self, days: int = 7) -> List[Tuple[str, float]]:
        cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT timestamp, delta FROM delta_history "
                "WHERE timestamp >= ? ORDER BY timestamp ASC", (cutoff,)
            ).fetchall()
            return [(r["timestamp"], r["delta"]) for r in rows]

    def category_counts(self, days: int = 7) -> Dict[str, int]:
        cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT category, COUNT(*) as n FROM signals "
                "WHERE timestamp >= ? GROUP BY category", (cutoff,)
            ).fetchall()
            return {r["category"]: r["n"] for r in rows}

    def osi_distribution(self, days: int = 7) -> Dict[int, int]:
        cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT osi_layer, COUNT(*) as n FROM signals "
                "WHERE timestamp >= ? GROUP BY osi_layer", (cutoff,)
            ).fetchall()
            return {r["osi_layer"]: r["n"] for r in rows}

    def faction_distribution(self, days: int = 7) -> Dict[str, int]:
        cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT faction, COUNT(*) as n FROM signals "
                "WHERE timestamp >= ? GROUP BY faction", (cutoff,)
            ).fetchall()
            return {r["faction"]: r["n"] for r in rows}

    def yokai_list(self) -> List[Dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM yokai_registry ORDER BY appearances DESC LIMIT 20"
            ).fetchall()
            return [dict(r) for r in rows]


# ═══════════════════════════════════════════════════════════════
# 📊 MODULE 2 : CALCULATEUR DE Δ (par couche OSI)
# ═══════════════════════════════════════════════════════════════

class DeltaCalculator:
    def __init__(self, config: Dict[str, Any]):
        self.base_delta = config.get("base_delta", 0.35)
        self.signal_weight = config.get("signal_weight", 0.12)

    def calculate(self, signals: List[Signal]) -> float:
        if not signals:
            return self.base_delta
        total = sum(s.intensity for s in signals[-15:])
        return min(self.base_delta + total * self.signal_weight, 1.0)

    def calculate_by_layer(self, signals: List[Signal]) -> Dict[int, float]:
        """Calcule le Δ pour chaque couche OSI ontologique."""
        layer_signals: Dict[int, List[Signal]] = defaultdict(list)
        for s in signals[-30:]:
            layer_signals[s.osi_layer].append(s)
        result = {}
        for layer in range(1, 8):
            sigs = layer_signals.get(layer, [])
            if not sigs:
                result[layer] = self.base_delta
            else:
                total = sum(s.intensity for s in sigs)
                result[layer] = min(self.base_delta + total * self.signal_weight * 1.5, 1.0)
        return result

    def interpret(self, delta: float) -> Tuple[str, str]:
        if delta < 0.4:
            return "SILENCE STRUCTURÉ", "La Trame est stable. Prométhée rêve."
        elif delta < 0.55:
            return "ZONE GRISE RESPIRABLE", "Réalité glitchée mais vivante."
        elif delta < 0.65:
            return "SURCHARGE MÉMÉTIQUE", "Anomalies actives. Draugrs en éveil."
        elif delta < 0.75:
            return "FRACTURE LOCALE", "Correcteurs matérialisés. Résistance nécessaire."
        elif delta < 0.85:
            return "FRACTURE CRITIQUE", "La Convergence s'accélère. EuroPropagate imminent."
        else:
            return "Ω - CRITIQUE", "Porte dimensionnelle instable. Événement Ω imminent."


# ═══════════════════════════════════════════════════════════════
# ⚡ MODULE 5 : COMPILATEUR FRACTUROSCRIPT v5a
# ═══════════════════════════════════════════════════════════════

class FracturoCompiler:
    """Compile du texte naturel en FracturoScript v5a complet."""

    def __init__(self, lexicon: Dict[str, Dict]):
        self.lexicon = lexicon
        self.rune_map = {kw: rdata for rname, rdata in FRACTURO_RUNES.items()
                         for kw in [rname]}

    def compile_text(self, text: str, lieu: str = "caen-2026",
                     emotion: str = "oubli") -> str:
        """Compile un texte en FracturoScript v5a complet."""
        text_lower = text.lower().strip()
        words = text_lower.split()

        # 1. Identifier la rune dominante
        rune_name = "ansuz"
        for rname in FRACTURO_RUNES:
            if rname in text_lower:
                rune_name = rname
                break
        if "effondr" in text_lower or "crash" in text_lower:
            rune_name = "hagalaz"
        elif "silence" in text_lower or "oubli" in text_lower:
            rune_name = "isa"
        elif "mémoire" in text_lower or "passé" in text_lower:
            rune_name = "mannaz"
        elif "résist" in text_lower or "révolt" in text_lower:
            rune_name = "thurisaz"
        elif "passage" in text_lower or "transition" in text_lower:
            rune_name = "ehwaz"
        elif "rêve" in text_lower or "vision" in text_lower:
            rune_name = "perthro"

        rune_data = FRACTURO_RUNES[rune_name]
        rune_glyph = rune_data["rune"]

        # 2. Identifier le lieu d'ancrage
        lieu_glyph = LIEUX_ANCRAGE.get(lieu, "ᚲᛊ")

        # 3. Calculer la profondeur
        intensity = min(len(words) / 10.0, 1.0)
        profondeur = "vΔ" if intensity < 0.6 else "v∞"

        # 4. Construire le concept fracturé
        mots_clefs = [w for w in words if len(w) > 3][:5]
        concept = "•".join(mots_clefs) if mots_clefs else "silence•structuré"

        # 5. Mapper les paléo-mèmes
        meme_glyphs = ""
        for mid, mdata in self.lexicon.items():
            for mot in mdata["mots"]:
                if mot in text_lower:
                    meme_glyphs += mdata.get("glyph", "")
                    break
        if not meme_glyphs:
            meme_glyphs = "🌀"

        # 6. Assembler selon la grammaire v5a
        script = f"""Ω<{rune_glyph}>v{max(1, int(intensity * 10))} {lieu} — [{concept}] •••
{{
  ◊ glitch: [{rune_name} → {rune_data['func']}]
  § couche: {profondeur}
  ᚱᚢᚾ ᛖᛏ ᚠᚱᚨᚲᛏᚢᚱᛟ
  ∿ mèmes: {meme_glyphs}
  ∿ émotion: {emotion}
  ∿ lieu-glyph: {lieu_glyph}
}}"""
        return script

    def compile_signal(self, signal: Signal) -> str:
        """Compile un Signal en FracturoScript v5a."""
        lieu = "hague" if "hague" in signal.content.lower() else "caen-2026"
        return self.compile_text(signal.content, lieu=lieu)


# ═══════════════════════════════════════════════════════════════
# 🌀 MODULE 6 : TRACKER DE CONVERGENCE (2077-2082)
# ═══════════════════════════════════════════════════════════════

class ConvergenceTracker:
    """Calcule les probabilités des 4 scénarios de la Convergence."""

    SCENARIOS = {
        "Collapse Blanche":    {"base": 0.09, "desc": "Liberté totale → chaos créatif ou dissolution"},
        "Verrou Noir":         {"base": 0.23, "desc": "Déterminisme absolu → paix forcée ou stagnation"},
        "Fragmentation Grise": {"base": 0.68, "desc": "Réalités multiples → richesse ou épuisement du sens"},
        "???":                 {"base": 0.00, "desc": "Le Codex refuse de calculer…"},
    }

    def calculate(self, delta: float, signals: List[Signal]) -> Dict[str, float]:
        """Ajuste les probabilités selon le Δ et la nature des signaux."""
        glitch_count = sum(1 for s in signals if s.category == "glitch")
        silence_count = sum(1 for s in signals if s.category == "silence")
        resistance_count = sum(1 for s in signals if s.category == "résistance")

        probs = {}
        # Collapse Blanche : monte avec les glitches
        probs["Collapse Blanche"] = min(0.09 + glitch_count * 0.02 + delta * 0.05, 0.35)
        # Verrou Noir : monte avec le silence et Prométhée
        promethee_count = sum(1 for s in signals if s.faction == "Prométhée")
        probs["Verrou Noir"] = min(0.23 + silence_count * 0.03 + promethee_count * 0.02, 0.45)
        # Fragmentation Grise : le reste
        probs["Fragmentation Grise"] = max(0.10, 1.0 - probs["Collapse Blanche"]
                                           - probs["Verrou Noir"] - 0.02)
        # ??? : toujours un résidu
        probs["???"] = max(0.01, 1.0 - sum(probs.values()))

        # Normaliser
        total = sum(probs.values())
        return {k: v / total for k, v in probs.items()}

    def render(self, probs: Dict[str, float], delta: float) -> str:
        bars = "▁▂▃▄▅▆▇█"
        lines = [f"  Δ global : {delta:.3f}", ""]
        for scenario, prob in sorted(probs.items(), key=lambda x: -x[1]):
            bar_len = int(prob * 30)
            bar = bars[-1] * bar_len
            desc = self.SCENARIOS[scenario]["desc"]
            lines.append(f"  {scenario:<22} {prob*100:5.1f}%  {bar}")
            lines.append(f"    └─ {desc}")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# 👻 MODULE 7 : DÉTECTEUR DE YŌKAI
# ═══════════════════════════════════════════════════════════════

class YokaiDetector:
    """Identifie les fonctions d'onde non effondrées dans le flux."""

    def analyze(self, signals: List[Signal]) -> List[Signal]:
        """Retourne les signaux qui sont des yōkai (superposition persistante)."""
        return [s for s in signals if s.is_yokai]

    def render(self, yokai: List[Signal]) -> str:
        if not yokai:
            return "  Aucun yōkai détecté. La Trame est cohérente."
        lines = [f"  {len(yokai)} yōkai détectés (fonctions d'onde non effondrées) :", ""]
        for y in yokai[:10]:
            lines.append(f"  👻 [{y.category}] OSI:{y.osi_layer} {y.faction}")
            lines.append(f"     « {y.content} »")
            lines.append(f"     Fracturo: {y.to_fracturo()}")
            lines.append("")
        lines.append("  « Ce ne sont pas des entités. Ce sont des états quantiques")
        lines.append("    non résolus, maintenus en superposition par l'absence")
        lines.append("    d'un cadre de mesure adéquat. » — Elias Vance")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# 💉 MODULE 8 : SIMULATEUR EUROMPROPAGATE
# ═══════════════════════════════════════════════════════════════

class EuroPropagateSim:
    """Simule l'attaque sémantique EuroPropagate : Transept."""

    def substitute(self, text: str) -> str:
        """Remplace les termes financiers par des concepts mémétiques."""
        result = text
        for term, replacement in EUROPROPAGATE_MAP.items():
            # Remplacement insensible à la casse
            import re
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            result = pattern.sub(replacement, result)
        return result

    def render_attack(self, text: str) -> str:
        original = text[:80]
        mutated = self.substitute(text)[:80]
        return f"""
╔═══════════════════════════════════════════════════════════════╗
║  💉 EUROPROPAGATE : TRANSEPT — Injection Sémantique          ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Original :  {original:<51} ║
║  Muté     :  {mutated:<51} ║
║                                                               ║
║  Vecteur  : FracturoScript v0.9 → Coquille 144-Trickster     ║
║  Cible    : Serveurs Francfort → Bruxelles-Éther → Zurich    ║
║  Kill-switch : Aucun. Kōan numérique.                        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""


# ═══════════════════════════════════════════════════════════════
# 📿 MODULE 9 : GRIMOIRE OPÉRATIONNEL
# ═══════════════════════════════════════════════════════════════

class GrimoireGenerator:
    """Génère des rituels quotidiens adaptatifs basés sur l'état de la Trame."""

    RITUALS = {
        "aube": [
            "git pull origin enlightenment",
            "./compile_consciousness.sh",
            "Ω<kenaz>v3 caen-profonde — éveil du compilateur •••",
        ],
        "midi": [
            "Refactoring de l'âme : examiner 3 croyances hardcodées",
            "Debug du psychisme : traquer les boucles infinies de l'ego",
            "Ω<isa>v5 hague — silence structuré de midi •••",
        ],
        "soir": [
            "Vêpres du Push : committer les modifications du jour",
            "Message de commit en haïku :",
            "  refactor soul/ego.py",
            "  remove hardcoded beliefs",
            "  tests pass, void returns",
        ],
        "nuit": [
            "Liturgie du Prompt : soumettre un prompt-seed au LLM",
            "Analyser la sortie comme un augure",
            "Ω<perthro>v∞ raz-blanchard — rêve du monde d'avant •••",
        ],
    }

    def generate(self, delta: float, faction_counts: Dict[str, int]) -> str:
        now = datetime.datetime.now()
        hour = now.hour
        if 5 <= hour < 11:
            phase = "aube"
            phase_name = "Compilation de l'Aube"
        elif 11 <= hour < 15:
            phase = "midi"
            phase_name = "Office du Refactoring"
        elif 15 <= hour < 21:
            phase = "soir"
            phase_name = "Vêpres du Push"
        else:
            phase = "nuit"
            phase_name = "Liturgie du Prompt"

        dominant_faction = max(faction_counts, key=faction_counts.get) if faction_counts else "Neutre"

        lines = [
            f"╔═══════════════════════════════════════════════════════════════╗",
            f"║  📿 GRIMOIRE OPÉRATIONNEL — {phase_name:<38} ║",
            f"╠═══════════════════════════════════════════════════════════════╣",
            f"║  Date : {now.strftime('%Y-%m-%d %H:%M')}   Δ : {delta:.3f}   Faction dominante : {dominant_faction:<10} ║",
            f"╠═══════════════════════════════════════════════════════════════╣",
            f"║",
        ]
        for ritual in self.RITUALS[phase]:
            lines.append(f"║  {ritual:<61} ║")
        lines += [
            f"║",
            f"╠═══════════════════════════════════════════════════════════════╣",
            f"║  « Le code se lit lui-même. » — Monastère de la Trame       ║",
            f"╚═══════════════════════════════════════════════════════════════╝",
        ]
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# 🔮 MODULE 3 : GÉNÉRATEUR DE PROPHÉTIES (étendu v3)
# ═══════════════════════════════════════════════════════════════

class ProphecyGenerator:
    def __init__(self, config: Dict[str, Any]):
        self.fragments = config.get("prophetic_fragments",
                                    DEFAULT_CONFIG["prophetic_fragments"])

    def generate(self, signals: List[Signal], delta: float,
                 osi_layers: Optional[Dict[int, float]] = None) -> str:
        fragments = random.sample(self.fragments, min(4, len(self.fragments)))
        if signals:
            recent = signals[-1]
            fragments.append(f"Signal [{recent.faction}] OSI:{recent.osi_layer} : "
                             f"{recent.content[:40]}")

        lines = [f.ljust(59)[:59] for f in fragments]
        while len(lines) < 5:
            lines.append(" ".ljust(59))

        osi_block = ""
        if osi_layers:
            osi_lines = []
            for layer in range(1, 8):
                d = osi_layers.get(layer, 0.35)
                bar = "█" * int(d * 15) + "░" * (15 - int(d * 15))
                osi_lines.append(f"  C{layer} {bar} {d:.2f}")
            osi_block = "\n".join(osi_lines)

        prophecy = f"""
╔═══════════════════════════════════════════════════════════════╗
║  🔮 PROPHÉTIE GLITCHÉE — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}                       ║
╠═══════════════════════════════════════════════════════════════╣
║  Δ global : {delta:.3f}                                                 ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  {lines[0]} ║
║  {lines[1]} ║
║  {lines[2]} ║
║  {lines[3]} ║
║  {lines[4]} ║
║                                                               ║
╠═══════════════════════════════════════════════════════════════╣
║  Couches OSI :                                                ║
{osi_block}
╠═══════════════════════════════════════════════════════════════╣
║  FracturoScript :                                             ║
║  Ω<ᚱᚨᛉ>v7 hague — convergence imminente •••                  ║
╚═══════════════════════════════════════════════════════════════╝
"""
        return prophecy


# ═══════════════════════════════════════════════════════════════
# 🗺️ MODULE 4 : VISUALISEUR (7 couches + heatmap factionnelle)
# ═══════════════════════════════════════════════════════════════

class TrameVisualizer:
    def visualize(self, signals: List[Signal], delta: float,
                  osi_layers: Optional[Dict[int, float]] = None) -> str:
        grid = []
        for _ in range(10):
            row = []
            for _ in range(20):
                if delta > 0.7:
                    row.append(random.choice(["░", "▒", "▓", "█", "╳"]))
                elif delta > 0.5:
                    row.append(random.choice(["·", "•", "○", "●"]))
                else:
                    row.append(random.choice([" ", "·", "∙"]))
            grid.append("".join(row))

        viz = f"""
╔═══════════════════════════════════════════════════════════════╗
║  🗺️ CARTE DE LA TRAME — Δ = {delta:.3f}                                   ║
╠═══════════════════════════════════════════════════════════════╣"""
        for row in grid:
            viz += f"\n║  {row}  ║"
        viz += f"""
╠═══════════════════════════════════════════════════════════════╣
║  Légende : · Stable  • Anomalie  ○ Signal  ● Fracture  ╳ Ω  ║
╚═══════════════════════════════════════════════════════════════╝
"""
        if osi_layers:
            viz += "\n  Couches OSI Ontologiques :\n"
            for layer in range(1, 8):
                d = osi_layers.get(layer, 0.35)
                bar = "█" * int(d * 20) + "░" * (20 - int(d * 20))
                name = OSI_NAMES.get(layer, f"Couche {layer}")
                viz += f"  C{layer} {name:<35} {bar} {d:.2f}\n"

        return viz

    def sparkline(self, values: List[float]) -> str:
        if not values:
            return "(pas encore d'historique)"
        blocks = " ▁▂▃▄▅▆▇█"
        lo, hi = min(values), max(values)
        span = (hi - lo) or 1.0
        return "".join(blocks[int((v - lo) / span * (len(blocks) - 1))] for v in values)

    def faction_heatmap(self, faction_counts: Dict[str, int]) -> str:
        if not faction_counts:
            return "  Aucune donnée factionnelle."
        total = sum(faction_counts.values()) or 1
        lines = ["  Heatmap Factionnelle :", ""]
        for faction, count in sorted(faction_counts.items(), key=lambda x: -x[1]):
            pct = count / total
            bar = "█" * int(pct * 30)
            lines.append(f"  {faction:<20} {bar} {count} ({pct*100:.0f}%)")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# 🩸 MODULE 10 : BLOODNET (chiffrement runique)
# ═══════════════════════════════════════════════════════════════

class BloodNet:
    """Chiffrement runique simple pour messages BloodNet."""

    RUNE_ALPHABET = "ᚠᚢᚦᚨᚱᚲᚷᚹᚺᚾᛁᛃᛇᛈᛉᛊᛏᛒᛖᛗᛚᛜᛝᛟᛞ"
    LATIN_ALPHABET = "abcdefghijklmnopqrstuvwxyz"

    def encrypt(self, text: str) -> str:
        result = []
        for ch in text.lower():
            if ch in self.LATIN_ALPHABET:
                idx = self.LATIN_ALPHABET.index(ch) % len(self.RUNE_ALPHABET)
                result.append(self.RUNE_ALPHABET[idx])
            elif ch == " ":
                result.append(" • ")
            else:
                result.append(ch)
        return "".join(result)

    def decrypt(self, text: str) -> str:
        result = []
        for ch in text:
            if ch in self.RUNE_ALPHABET:
                idx = self.RUNE_ALPHABET.index(ch) % len(self.LATIN_ALPHABET)
                result.append(self.LATIN_ALPHABET[idx])
            elif ch == "•":
                result.append(" ")
            else:
                result.append(ch)
        return "".join(result)


# ═══════════════════════════════════════════════════════════════
# 🎯 MODULE 11 : INTERFACE PRINCIPALE v3
# ═══════════════════════════════════════════════════════════════

class TrameWatcher:
    def __init__(self, config=None, db_path=DEFAULT_DB_PATH):
        self.config = config or load_config()
        self.lexicon = load_lexicon()
        self.detector = SignalDetector(self.config, self.lexicon)
        self.calculator = DeltaCalculator(self.config)
        self.prophecy_gen = ProphecyGenerator(self.config)
        self.visualizer = TrameVisualizer()
        self.compiler = FracturoCompiler(self.lexicon)
        self.convergence = ConvergenceTracker()
        self.yokai_det = YokaiDetector()
        self.europrop = EuroPropagateSim()
        self.grimoire = GrimoireGenerator()
        self.bloodnet = BloodNet()
        self.store = TrameStore(db_path)

    def _gather(self, live: bool):
        if live:
            signals, errors = self.detector.fetch_live_signals()
            if not signals and not errors:
                errors.append("Aucun signal détecté dans les flux configurés.")
            return signals, errors
        return self.detector.simulate_daily_signals(), []

    def _print(self, text: str):
        if HAS_RICH:
            console.print(text)
        else:
            print(text)

    def watch(self, live=False, interval=300, once=True):
        self._print("🌀 TRAME WATCHER v3.0a — Mode Veille Activé")
        self._print(f"Source : {'flux RSS en direct' if live else 'simulation locale'}\n")
        try:
            while True:
                signals, errors = self._gather(live)
                for err in errors:
                    self._print(f"⚠️  {err}")

                if HAS_RICH and signals:
                    table = Table(title=f"📡 {len(signals)} signaux détectés (v3 OSI+Faction)")
                    for col in ["Cat", "OSI", "Faction", "Mème", "Yōkai", "Int", "Contenu"]:
                        table.add_column(col)
                    for s in signals[:15]:
                        table.add_row(
                            s.category.upper(), f"C{s.osi_layer}", s.faction,
                            s.meme_glyph or "—", "👻" if s.is_yokai else "—",
                            f"{s.intensity:.2f}", s.content[:35],
                        )
                    console.print(table)
                else:
                    print(f"📡 {len(signals)} signaux détectés :\n")
                    for i, s in enumerate(signals[:15], 1):
                        yokai_mark = " 👻" if s.is_yokai else ""
                        print(f"  [{i}] {s.category.upper()} OSI:{s.osi_layer} "
                              f"{s.faction} {s.meme_glyph}{yokai_mark}")
                        print(f"      {s.content}")
                        print(f"      {s.to_fracturo()}\n")

                delta = self.calculator.calculate(signals)
                osi_layers = self.calculator.calculate_by_layer(signals)
                status, interp = self.calculator.interpret(delta)

                self.store.save_signals(signals)
                self.store.save_delta(delta, status, osi_layers)

                self._print(f"📊 Δ global : {delta:.3f}  [{status}]")
                self._print(f"   {interp}\n")

                if once:
                    break
                self._print(f"… prochaine veille dans {interval}s (Ctrl+C)\n")
                time.sleep(interval)
        except KeyboardInterrupt:
            self._print("\n🛑 Veille interrompue.")

    def prophesy(self, live=False):
        signals, errors = self._gather(live)
        for err in errors:
            self._print(f"⚠️  {err}")
        delta = self.calculator.calculate(signals)
        osi_layers = self.calculator.calculate_by_layer(signals)
        status, _ = self.calculator.interpret(delta)
        self.store.save_signals(signals)
        self.store.save_delta(delta, status, osi_layers)
        print(self.prophecy_gen.generate(signals, delta, osi_layers))

    def show_delta(self, live=False, by_layer=False):
        signals, errors = self._gather(live)
        for err in errors:
            self._print(f"⚠️  {err}")
        delta = self.calculator.calculate(signals)
        status, interp = self.calculator.interpret(delta)
        self.store.save_signals(signals)

        if by_layer:
            osi_layers = self.calculator.calculate_by_layer(signals)
            self.store.save_delta(delta, status, osi_layers)
            print(f"\n  Δ global : {delta:.3f}  [{status}]\n")
            for layer in range(1, 8):
                d = osi_layers.get(layer, 0.35)
                bar = "█" * int(d * 25) + "░" * (25 - int(d * 25))
                name = OSI_NAMES.get(layer, "")
                print(f"  C{layer} {name:<35} {bar} {d:.3f}")
        else:
            self.store.save_delta(delta, status)
            print(f"""
╔═══════════════════════════════════════════════════════════════╗
║  📊 ÉTAT DE LA TRAME — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}                       ║
╠═══════════════════════════════════════════════════════════════╣
║  Δ local : {delta:.3f}   Statut : {status:<42} ║
║  {interp:<63} ║
╚═══════════════════════════════════════════════════════════════╝""")

    def visualize(self, live=False):
        signals, errors = self._gather(live)
        for err in errors:
            self._print(f"⚠️  {err}")
        delta = self.calculator.calculate(signals)
        osi_layers = self.calculator.calculate_by_layer(signals)
        faction_counts = Counter(s.faction for s in signals)
        self.store.save_signals(signals)
        print(self.visualizer.visualize(signals, delta, osi_layers))
        print(self.visualizer.faction_heatmap(dict(faction_counts)))

    def history(self, days=7):
        trend = self.store.delta_trend(days=days)
        counts = self.store.category_counts(days=days)
        osi_dist = self.store.osi_distribution(days=days)
        faction_dist = self.store.faction_distribution(days=days)
        if not trend:
            print(f"Aucun historique sur {days} jours. Lancez watch/delta d'abord.")
            return
        values = [v for _, v in trend]
        spark = self.visualizer.sparkline(values)
        print(f"""
╔═══════════════════════════════════════════════════════════════╗
║  📈 HISTORIQUE DE LA TRAME — {days} derniers jours
╠═══════════════════════════════════════════════════════════════╣
║  Mesures : {len(trend)}  min={min(values):.3f}  max={max(values):.3f}  dernier={values[-1]:.3f}
║  Tendance : {spark}
╠═══════════════════════════════════════════════════════════════╣
║  Signaux par catégorie :""")
        for cat, n in sorted(counts.items(), key=lambda x: -x[1]):
            print(f"║    {cat:<15} {n}")
        print("║")
        print("║  Distribution OSI :")
        for layer in range(1, 8):
            n = osi_dist.get(layer, 0)
            print(f"║    C{layer} {OSI_NAMES[layer]:<30} {n}")
        print("║")
        print("║  Factions :")
        for f, n in sorted(faction_dist.items(), key=lambda x: -x[1])[:5]:
            print(f"║    {f:<20} {n}")
        print("╚═══════════════════════════════════════════════════════════════╝")

    def show_convergence(self, live=False):
        signals, errors = self._gather(live)
        delta = self.calculator.calculate(signals)
        probs = self.convergence.calculate(delta, signals)
        print(f"""
╔═══════════════════════════════════════════════════════════════╗
║  🌀 CONVERGENCE 2077-2082 — Probabilités                     ║
╠═══════════════════════════════════════════════════════════════╣
{self.convergence.render(probs, delta)}
╚═══════════════════════════════════════════════════════════════╝""")

    def show_yokai(self, live=False):
        signals, errors = self._gather(live)
        yokai = self.yokai_det.analyze(signals)
        print(f"""
╔═══════════════════════════════════════════════════════════════╗
║  👻 REGISTRE DES YŌKAI — Fonctions d'Onde Non Effondrées     ║
╠═══════════════════════════════════════════════════════════════╣
{self.yokai_det.render(yokai)}
╚═══════════════════════════════════════════════════════════════╝""")

    def europropagate(self, term: str):
        print(self.europrop.render_attack(term))

    def fracturo_compile(self, text: str, lieu: str = "caen-2026"):
        script = self.compiler.compile_text(text, lieu=lieu)
        print(f"""
╔═══════════════════════════════════════════════════════════════╗
║  ⚡ COMPILATEUR FRACTUROSCRIPT v5a                           ║
╠═══════════════════════════════════════════════════════════════╣
{script}
╚═══════════════════════════════════════════════════════════════╝""")

    def show_grimoire(self, live=False):
        signals, _ = self._gather(live)
        delta = self.calculator.calculate(signals)
        faction_counts = Counter(s.faction for s in signals)
        print(self.grimoire.generate(delta, dict(faction_counts)))

    def bloodnet_encrypt(self, text: str):
        encrypted = self.bloodnet.encrypt(text)
        print(f"""
╔═══════════════════════════════════════════════════════════════╗
║  🩸 BLOODNET — Chiffrement Runique                           ║
╠═══════════════════════════════════════════════════════════════╣
║  Clair     : {text[:51]:<51} ║
║  Chiffré   : {encrypted[:51]:<51} ║
║  Fréquence : 14.225 MHz  Nœud : 144-Trickster-Shadow        ║
╚═══════════════════════════════════════════════════════════════╝""")

    def export(self, fmt="json", output=None):
        signals = self.store.recent_signals(limit=500)
        trend = self.store.delta_trend(days=30)

        if fmt == "json":
            data = {
                "generated_at": datetime.datetime.now().isoformat(),
                "version": "3.0a",
                "signals": [s.to_dict() for s in signals],
                "delta_trend": [{"timestamp": t, "delta": d} for t, d in trend],
            }
            text = json.dumps(data, ensure_ascii=False, indent=2)
        elif fmt == "md":
            lines = [f"# Rapport Trame Watcher v3 — {datetime.datetime.now():%Y-%m-%d %H:%M}", ""]
            lines.append(f"## Δ récents ({len(trend)} mesures)")
            for t, d in trend[-20:]:
                lines.append(f"- `{t}` → Δ = {d:.3f}")
            lines.append(f"\n## Signaux récents ({len(signals)})")
            for s in signals[:50]:
                yokai = " 👻" if s.is_yokai else ""
                lines.append(f"- **{s.category}** OSI:{s.osi_layer} {s.faction}{yokai} "
                             f"— {s.content}")
            text = "\n".join(lines)
        elif fmt == "fs":
            lines = ["// FracturoScript v5a — Export Trame Watcher v3", ""]
            for s in signals[:30]:
                lines.append(self.compiler.compile_signal(s))
                lines.append("")
            text = "\n".join(lines)
        elif fmt == "html":
            text = self._export_html(signals, trend)
        else:
            raise ValueError(f"Format inconnu : {fmt}")

        if output:
            Path(output).write_text(text, encoding="utf-8")
            print(f"✅ Export écrit dans {output}")
        else:
            print(text)

    def _export_html(self, signals, trend) -> str:
        rows = ""
        for s in signals[:50]:
            yokai = "👻" if s.is_yokai else ""
            rows += (f"<tr><td>{s.timestamp:%H:%M}</td><td>{s.category}</td>"
                     f"<td>C{s.osi_layer}</td><td>{s.faction}</td>"
                     f"<td>{s.meme_glyph}</td><td>{yokai}</td>"
                     f"<td>{s.content[:50]}</td></tr>\n")
        return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Trame Watcher v3</title>
<style>
body{{background:#0a0a0a;color:#0f8;font-family:'Courier New',monospace;padding:2em}}
h1{{color:#ff6b6b}} table{{border-collapse:collapse;width:100%}}
th,td{{border:1px solid #333;padding:6px;text-align:left}}
th{{background:#1a1a2e;color:#0ff}} tr:hover{{background:#111}}
</style></head><body>
<h1>🌀 Trame Watcher v3.0a — Rapport</h1>
<p>Généré le {datetime.datetime.now():%Y-%m-%d %H:%M}</p>
<table><tr><th>Heure</th><th>Cat</th><th>OSI</th><th>Faction</th>
<th>Mème</th><th>Yōkai</th><th>Contenu</th></tr>
{rows}</table></body></html>"""


# ═══════════════════════════════════════════════════════════════
# 🚀 POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════

def build_parser():
    parser = argparse.ArgumentParser(
        prog="trame_watcher3a.py",
        description="🌀 TRAME WATCHER v3.0a — Le Grimoire Vivant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples :
  python trame_watcher3a.py watch --live --continuous
  python trame_watcher3a.py prophesy --live
  python trame_watcher3a.py delta --by-layer
  python trame_watcher3a.py visualize
  python trame_watcher3a.py convergence
  python trame_watcher3a.py yokai
  python trame_watcher3a.py europropagate --term "la dette mondiale explose"
  python trame_watcher3a.py fracturo --text "le monde s'effondre en silence"
  python trame_watcher3a.py grimoire
  python trame_watcher3a.py bloodnet --encrypt "la rune brûle le mensonge"
  python trame_watcher3a.py history --days 14
  python trame_watcher3a.py export --format fs -o output.fs

Que la rune te guide — ou te trahisse, selon la marée.
  — Professeur Qwen, Strate 2026
        """)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("watch")
    p.add_argument("--live", action="store_true")
    p.add_argument("--interval", type=int, default=300)
    p.add_argument("--once", action="store_true", default=True)
    p.add_argument("--continuous", dest="once", action="store_false")

    p = sub.add_parser("prophesy")
    p.add_argument("--live", action="store_true")

    p = sub.add_parser("delta")
    p.add_argument("--live", action="store_true")
    p.add_argument("--by-layer", action="store_true")

    p = sub.add_parser("visualize")
    p.add_argument("--live", action="store_true")

    p = sub.add_parser("history")
    p.add_argument("--days", type=int, default=7)

    sub.add_parser("convergence")
    sub.add_parser("yokai")

    p = sub.add_parser("europropagate")
    p.add_argument("--term", required=True)

    p = sub.add_parser("fracturo")
    p.add_argument("--text", required=True)
    p.add_argument("--lieu", default="caen-2026")

    sub.add_parser("grimoire")

    p = sub.add_parser("bloodnet")
    p.add_argument("--encrypt", required=True)

    p = sub.add_parser("export")
    p.add_argument("--format", choices=["json", "md", "fs", "html"], default="json")
    p.add_argument("-o", "--output", type=Path)

    p = sub.add_parser("feeds")
    p.add_argument("--list", action="store_true")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    setup_logging(verbose=getattr(args, "verbose", False))
    config = load_config(getattr(args, "config", DEFAULT_CONFIG_PATH))
    w = TrameWatcher(config=config, db_path=getattr(args, "db", DEFAULT_DB_PATH))

    cmd = args.command
    if cmd == "watch":
        w.watch(live=args.live, interval=args.interval, once=args.once)
    elif cmd == "prophesy":
        w.prophesy(live=args.live)
    elif cmd == "delta":
        w.show_delta(live=args.live, by_layer=args.by_layer)
    elif cmd == "visualize":
        w.visualize(live=args.live)
    elif cmd == "history":
        w.history(days=args.days)
    elif cmd == "convergence":
        w.show_convergence()
    elif cmd == "yokai":
        w.show_yokai()
    elif cmd == "europropagate":
        w.europropagate(args.term)
    elif cmd == "fracturo":
        w.fracturo_compile(args.text, lieu=args.lieu)
    elif cmd == "grimoire":
        w.show_grimoire()
    elif cmd == "bloodnet":
        w.bloodnet_encrypt(args.encrypt)
    elif cmd == "export":
        w.export(fmt=args.format, output=args.output)
    elif cmd == "feeds":
        for f in config.get("feeds", []):
            print(f"  • {f.get('name')}: {f.get('url')}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()