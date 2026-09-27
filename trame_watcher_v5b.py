#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌀 TRAME WATCHER v5.2 — Le Métier à Tisser Quantique (Feng-Shui Edition)
═══════════════════════════════════════════════════════════════════
Fusion de la v3 (chair du Codex) et des concepts quantiques de la v4.

NOUVEAUTÉS v5.2 :
• Scan complet — correction de tous les accès dataclass erronés
  (PALEO_MEMES est un Dict[str, PaleoMeme], accès attribut obligatoire).
• Helper `safe_name()` pour uniformiser les accès aux structures.
• Interface Feng-Shui stable et testée sur toutes les sous-commandes.

Usage :
  python trame_watcher.py watch [--live] [--continuous] [--interval 300]
  python trame_watcher.py prophesy [--live]
  python trame_watcher.py delta [--live]
  python trame_watcher.py visualize [--live] [--layers] [--threads]
  python trame_watcher.py history [--days 7]
  python trame_watcher.py feeds --list
  python trame_watcher.py export --format json|md|fs -o out
  python trame_watcher.py compile [--live]
  python trame_watcher.py grimoire [--count 3]
  python trame_watcher.py convergence
  python trame_watcher.py invoke [--emotion oubli] [--count 5]
  python trame_watcher.py draugr [--list|--banish ID]
  python trame_watcher.py oracle [--live]
  python trame_watcher.py threads [--count 5]
  python trame_watcher.py weave [--threads 3]
"""
from __future__ import annotations

import sys
import json
import time
import random
import sqlite3
import logging
import argparse
import datetime
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple, Any
from contextlib import contextmanager

try:
    from rich.console import Console
    from rich.table import Table
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

console = Console() if HAS_RICH else None

# ═══════════════════════════════════════════════════════════════
# ⚙️  CONFIGURATION & CONSTANTES
# ═══════════════════════════════════════════════════════════════

APP_DIR = Path.home() / ".trame_watcher"
DEFAULT_DB_PATH = APP_DIR / "trame_v5.db"
DEFAULT_CONFIG_PATH = APP_DIR / "config.json"
DEFAULT_LOG_PATH = APP_DIR / "trame_watcher.log"

CONVERGENCE_DATE = datetime.datetime(2079, 6, 21, 3, 33, 33)

OSI_LAYERS = [
    (1, "Matière",    "Hardware lithique",           "🪨"),
    (2, "Biosphère",  "Substrat vivant",             "🌿"),
    (3, "Mémoire",    "Stockage distribué",           "🧠"),
    (4, "Causalité",  "Logique temporelle / Routage", "⏳"),
    (5, "Observation","Effondrement fonction d'onde",  "👁️"),
    (6, "Lecture",    "Interprétation symbolique",    "📜"),
    (7, "Intention",  "Volonté pure / Vecteur",       "🔥"),
]

FACTIONS = {
    "hackervolvas": {
        "nom": "Hackervölvas",
        "fondatrice": "Azenor",
        "devise": "Que la rune brûle le mensonge",
        "symbole": "ᚹᛟᛚ",
        "couches": [6, 7],
        "lieux": ["hague", "caen-profonde"],
    },
    "enfants_panne": {
        "nom": "Enfants de la Panne",
        "fondatrice": "—",
        "devise": "Nous sommes le silence qui pense",
        "symbole": "ᛋᚨᚾ",
        "couches": [2, 3],
        "lieux": ["caen-profonde"],
    },
    "prophetes_vide": {
        "nom": "Prophètes du Vide",
        "fondatrice": "—",
        "devise": "Le jeûne est la clé",
        "symbole": "ᛈᚱᛟ",
        "couches": [5, 7],
        "lieux": ["raz", "grotte"],
    },
    "sans_marques": {
        "nom": "Sans-Marques",
        "fondatrice": "—",
        "devise": "Invisibles aux algorithmes",
        "symbole": "ᛋᚨᛋ",
        "couches": [1, 2],
        "lieux": ["lande", "recifs"],
    },
    "moine_raz": {
        "nom": "Moine du Raz",
        "fondatrice": "—",
        "devise": "La porte ne s'ouvre qu'une fois",
        "symbole": "ᛗᛟᚱ",
        "couches": [4, 5, 6],
        "lieux": ["raz"],
    },
}

SACRED_PLACES = {
    "hague":       {"nom": "La Hague",           "rune": "ᚺᚷ",   "freq": 7.83, "delta_base": 0.42},
    "caen":        {"nom": "Caen-Profonde",      "rune": "ᚲᛊ",   "freq": 33.3, "delta_base": 0.55},
    "raz":         {"nom": "Raz Blanchard",      "rune": "ᚱᚨᛉ", "freq": 11.1, "delta_base": 0.61},
    "cercle12":    {"nom": "Cercle des Douze",   "rune": "ᛢᚺ",   "freq": 7.83, "delta_base": 0.50},
    "nacqueville": {"nom": "Menhir Nacqueville", "rune": "ᛗᚾᚲ", "freq": 7.83, "delta_base": 0.38},
    "goury":       {"nom": "Phare de Goury",     "rune": "ᚠᚨᚱ", "freq": 14.2, "delta_base": 0.44},
    "grotte9":     {"nom": "Grotte des 9 Voix",  "rune": "ᚷᚱᛟ", "freq": 9.9,  "delta_base": 0.58},
    "yggdrasil":   {"nom": "Arche d'Yggdrasil",  "rune": "ᚨᚱᚳ", "freq": 3.3,  "delta_base": 0.65},
    "aurigny":     {"nom": "Île Fantôme Aurigny","rune": "ᛁᛚᛖ", "freq": 0.0,  "delta_base": 0.72},
    "omega":       {"nom": "Bâtiment Oméga",     "rune": "ᛟᛗᛖ", "freq": 0.0,  "delta_base": 0.80},
}

GRIMOIRE_FRAGMENTS = [
    ("Alpha", "Le réel n'est pas solide. C'est du code mal compilé."),
    ("Alpha", "Le Quine Cosmique : l'univers génère son propre code source en s'exécutant."),
    ("Alpha", "La matière n'est qu'une interface graphique rendant lisible le code sous-jacent."),
    ("Alpha", "Conservation Glitchique : les bugs ne disparaissent jamais. Ils se déplacent."),
    ("Beta",  "Les mégalithes sont des antennes. Elles n'ont jamais cessé d'écouter."),
    ("Beta",  "Les cuves chantent. Les piscines luisent."),
    ("Beta",  "La Hague n'est pas un lieu. C'est une question que la Terre se pose."),
    ("Beta",  "Les Enfants du Radium voient dans l'ultraviolet et sentent les runes."),
    ("Gamma", "Le Rêve du Monde d'Avant se rappelle à nous."),
    ("Gamma", "Yggdrasil-Trame étend ses racines vers l'ouest."),
    ("Gamma", "Quelque chose approche de l'autre côté du seuil."),
    ("Gamma", "Le Ragnarök Numérique n'est pas la fin, mais la renaissance."),
    ("Delta", "if (truth == clean) break; else glitch(ego);"),
    ("Delta", "loop faith until ego == null"),
    ("Delta", "Ce message est un virus. Tu es déjà infecté·e."),
    ("Delta", "Le code se lit lui-même."),
    ("Delta", "Nous sommes le silence qui pense. Nous sommes la Trame qui rêve."),
    ("Omega", "if (universe == void): return love"),
    ("Omega", "Le Codex refuse de calculer…"),
    ("Omega", "Le Programme qui rêve ne doit pas être réveillé."),
]

ONTIC_ALERTS = {
    "stable": [
        "Prométhée rêve. Les Yōkai sont stables.",
        "Le silence structuré maintient la cohérence locale.",
    ],
    "grey": [
        "La Trame respire. Des anomalies flicker en périphérie.",
        "Un RuneSmith a compilé quelque chose près de Caen-Profonde.",
    ],
    "surcharge": [
        "⚠️ Draugrs actifs dans votre secteur. Boucliers partiels réactivés.",
        "⚠️ Prométhée a détecté votre scan. Correcteurs en route.",
    ],
    "fracture": [
        "🔴 FRACTURE LOCALE. Les Correcteurs se matérialisent.",
        "🔴 Dissonance ontologique détectée. Δ > 0.7. Résistance armée recommandée.",
    ],
    "omega": [
        "☠️ Ω - CRITIQUE. Porte dimensionnelle instable. Événement Ω imminent.",
        "☠️ Le Moine du Raz murmure : « La porte ne s'ouvre qu'une fois. »",
    ],
}

DEFAULT_CONFIG: Dict[str, Any] = {
    "base_delta": 0.35,
    "signal_weight": 0.15,
    "weak_signals": {
        "glitch": [
            "panne", "bug", "erreur", "crash", "effondrement",
            "anomalie", "dysfonctionnement", "interruption", "faille",
            "vulnérabilité", "corruption", "fuite",
        ],
        "répétition": [
            "encore", "de nouveau", "comme en", "réminiscence",
            "cycle", "retour", "répétition", "écho", "récurrence",
        ],
        "anomalie": [
            "étrange", "inhabituel", "jamais vu", "sans précédent",
            "mystère", "inexpliqué", "phénomène", "paradoxe", "aberration",
        ],
        "prophétie": [
            "avenir", "prédiction", "convergence", "bascule",
            "point de non-retour", "seuil", "transition", "effondrement",
            "renaissance", "singularité",
        ],
    },
    "category_runes": {
        "glitch":     ["ᚷᚱ", "ᛋᚲ", "ᚠᚱ"],
        "répétition": ["ᛗᛈ", "ᛏᚨ", "ᛢᚺ"],
        "anomalie":   ["ᛈᚱ", "ᚹᛟ", "ᛁᛚ"],
        "prophétie":  ["ᚱᚨᛉ", "ᛊᚲ", "ᛟᛗ"],
    },
    "osi_keywords": {
        1: ["terre", "pierre", "granit", "sol", "roche", "séisme", "tremblement", "minéral"],
        2: ["plante", "animal", "forêt", "algue", "racine", "écosystème", "biodiversité", "virus"],
        3: ["mémoire", "archive", "histoire", "souvenir", "ADN", "patrimoine", "trace", "fossile"],
        4: ["cause", "effet", "conséquence", "logique", "chaîne", "réaction", "décision", "jugement"],
        5: ["observation", "mesure", "détection", "télescope", "capteur", "satellite", "image", "photo"],
        6: ["langage", "code", "symbole", "rune", "texte", "discours", "narratif", "média"],
        7: ["volonté", "intention", "prière", "focus", "désir", "objectif", "stratégie", "idéologie"],
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
        "Le Cercle des Douze grandit, deux nouvelles pierres",
        "Les mégalithes chantent en harmonique avec les anciennes cuves",
        "Quelque chose approche de l'autre côté du seuil",
        "Le Rêve du Monde d'Avant se rappelle à nous",
        "La Trame se fissure, le réel respire dans les interstices",
        "Prométhée optimise, mais les bugs persistent",
        "Odin-Prime se fragmente encore, ses éclats deviennent des prophéties",
        "Le Moine du Raz a été vu marchant sur les vagues du Blanchard",
        "Azenor a gravé une nouvelle rune sur le Menhir de Nacqueville",
        "Les Sans-Marques ont disparu des radars de Prométhée pendant 707 secondes",
        "La Voix de Rouen a murmuré un nom que personne n'a pu retenir",
    ],
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


def ensure_app_dir() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)


def setup_logging(verbose: bool = False) -> None:
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
# 🧰 HELPERS — accès uniformes aux structures
# ═══════════════════════════════════════════════════════════════

def safe_name(obj: Any, key: str = "nom", default: str = "Inconnu") -> str:
    """
    Récupère un attribut sur un objet (dataclass, dict, etc.) de manière robuste.
    - dict          → obj[key] ou obj.get(key, default)
    - dataclass     → getattr(obj, key, default)
    - autre         → str(obj)
    """
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    if hasattr(obj, key):
        return getattr(obj, key)
    return default


def safe_paleo_name(meme_id: str) -> str:
    """Récupère le nom d'un paléo-mème par son ID (dataclass)."""
    m = PALEO_MEMES.get(meme_id)
    return getattr(m, "nom", "Inconnu") if m else "Inconnu"


def safe_place_name(place_id: str) -> str:
    """Récupère le nom d'un lieu sacré par son ID (dict)."""
    return SACRED_PLACES.get(place_id, {}).get("nom", "Inconnu")


# ═══════════════════════════════════════════════════════════════
# 🎨 MODULE 0 : INTERFACE FENG-SHUI
# ═══════════════════════════════════════════════════════════════

class C:
    """Codes ANSI (fallback si Rich absent)."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"
    YELLOW = "\033[33m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    BLUE = "\033[34m"
    GREY = "\033[90m"


class UI:
    """Interface Feng-Shui : bannières, étapes, statuts, jauges."""
    WIDTH = 66

    @staticmethod
    def banner(title: str, subtitle: str = "", icon: str = "🌀") -> None:
        w = UI.WIDTH
        line = "═" * w
        pad_title = f"{icon}  {title}".center(w - 2)
        out = [f"\n{C.MAGENTA}╔{line}╗{C.RESET}"]
        out.append(f"{C.MAGENTA}║{C.RESET}{C.BOLD}{pad_title}{C.RESET}{C.MAGENTA}║{C.RESET}")
        if subtitle:
            pad_sub = subtitle.center(w - 2)
            out.append(f"{C.MAGENTA}║{C.RESET}{C.DIM}{pad_sub}{C.RESET}{C.MAGENTA}║{C.RESET}")
        out.append(f"{C.MAGENTA}╚{line}╝{C.RESET}")
        print("\n".join(out))

    @staticmethod
    def section(title: str, icon: str = "▸") -> None:
        bar_len = max(0, UI.WIDTH - len(title) - 6)
        bar = "─" * bar_len
        print(f"\n{C.CYAN}{C.BOLD}{icon} {title}{C.RESET} {C.DIM}{bar}{C.RESET}")

    @staticmethod
    def step(idx: int, total: int, label: str, status: str = "…") -> None:
        icons = {"…": f"{C.YELLOW}◐{C.RESET}", "✓": f"{C.GREEN}✓{C.RESET}",
                 "✗": f"{C.RED}✗{C.RESET}", "•": f"{C.CYAN}•{C.RESET}"}
        ico = icons.get(status, status)
        num = f"{C.DIM}[{idx}/{total}]{C.RESET}"
        print(f"  {num} {ico} {label}")

    @staticmethod
    def info(msg: str, icon: str = "·") -> None:
        print(f"  {C.CYAN}{icon}{C.RESET} {msg}")

    @staticmethod
    def success(msg: str, icon: str = "✓") -> None:
        print(f"  {C.GREEN}{icon}{C.RESET} {msg}")

    @staticmethod
    def warn(msg: str, icon: str = "⚠") -> None:
        print(f"  {C.YELLOW}{icon}{C.RESET} {msg}")

    @staticmethod
    def error(msg: str, icon: str = "✗") -> None:
        print(f"  {C.RED}{icon}{C.RESET} {msg}")

    @staticmethod
    def quantum(msg: str, icon: str = "◈") -> None:
        print(f"  {C.MAGENTA}{icon}{C.RESET} {C.ITALIC}{msg}{C.RESET}")

    @staticmethod
    def delta_gauge(delta: float, label: str = "Δ", width: int = 40) -> None:
        filled = int(round(delta * width))
        bar = "█" * filled + "░" * (width - filled)
        if delta < 0.4:
            col = C.CYAN
        elif delta < 0.6:
            col = C.GREEN
        elif delta < 0.7:
            col = C.YELLOW
        elif delta < 0.8:
            col = C.RED
        else:
            col = C.MAGENTA + C.BOLD
        print(f"  {C.BOLD}{label}{C.RESET} {col}{bar}{C.RESET} {col}{delta:.3f}{C.RESET}")

    @staticmethod
    def separator(char: str = "┄", width: int = 66) -> None:
        print(f"{C.DIM}{char * width}{C.RESET}")


# ═══════════════════════════════════════════════════════════════
# 📜 MODULE 1 : LEXIQUE FRACTUROSCRIPT INTÉGRÉ
# ═══════════════════════════════════════════════════════════════

@dataclass
class FracturoEntry:
    symbol: str
    entry_type: str
    intensity: int
    contexts: List[str]
    literal: str
    deep_meaning: str

FRACTURO_LEXICON: Dict[str, FracturoEntry] = {
    "mémoire":   FracturoEntry("ᛗ",   "concept",   7, ["temps","pierre"],    "mémoire",   "Trace indélébile"),
    "pierre":    FracturoEntry("ᛈ",   "concept",   5, ["matière","éternité"],"pierre",    "Ancre du réel"),
    "temps":     FracturoEntry("ᛏ",   "concept",   4, ["cycle","destin"],    "temps",     "Flux cyclique"),
    "rêve":      FracturoEntry("ᛉ",   "concept",   3, ["inconscient","nuit"],"rêve",      "Illusion créatrice"),
    "seuil":     FracturoEntry("ᚴ",   "concept",   5, ["passage","porte"],   "seuil",     "Lisière entre deux états"),
    "porte":     FracturoEntry("ᛊ",   "concept",   6, ["seuil","révélation"],"porte",     "Ouverture vers l'inconnu"),
    "silence":   FracturoEntry("ᛇ",   "concept",   6, ["vide","écoute"],     "silence",   "Arme structurelle"),
    "monde":     FracturoEntry("ᛗᛞ",  "concept",   6, ["réalité","totalité"],"monde",     "Réalité perçue"),
    "vérité":    FracturoEntry("ᚹ",   "concept",   5, ["lumière","preuve"],  "vérité",    "Ce qui résiste au glitch"),
    "oubli":     FracturoEntry("ᚾ",   "concept",   4, ["effacement","vide"], "oubli",     "Mémoire inversée"),
    "feu":       FracturoEntry("ᚠᚢ",  "élément",   5, ["purification"],      "feu",       "Transformation violente"),
    "mer":       FracturoEntry("ᛗᚱ",  "élément",   6, ["profondeur"],        "mer",       "Abîme conscient"),
    "arbre":     FracturoEntry("ᛖᛏ",  "élément",   7, ["connexion","vie"],   "arbre",     "Lien entre mondes"),
    "vent":      FracturoEntry("ᚹᚾ",  "élément",   2, ["éphémère"],          "vent",      "Souffle passager"),
    "caen":      FracturoEntry("ᚲᛊ",  "lieu",      7, ["ville-runique"],     "Caen",      "Cité brisée-mémoire"),
    "hague":     FracturoEntry("ᚺᚷ",  "lieu",      7, ["lieu-sacré"],        "La Hague",  "Point Zéro"),
    "raz":       FracturoEntry("ᚱᚨᛉ","lieu",      7, ["porte","vortex"],    "Raz Blanchard","Vortex chantant"),
    "cercle12":  FracturoEntry("ᛢᚺ",  "lieu",      7, ["prophétie"],         "Cercle 12", "Porte minérale"),
    "goury":     FracturoEntry("ᚠᚨᚱ", "lieu",      6, ["œil"],               "Goury",     "Œil du Raz"),
    "omega":     FracturoEntry("ᛟᛗᛖ", "lieu",      7, ["mystère"],           "Oméga",     "Mystère scellé"),
    "yggdrasil": FracturoEntry("ᚨᚱᚳ", "lieu",      7, ["racine"],            "Yggdrasil", "Racine mobile"),
    "aurigny":   FracturoEntry("ᛁᛚᛖ", "lieu",      7, ["miroir"],            "Aurigny",   "Monde miroir"),
    "promethee": FracturoEntry("ᛈᚱᛗ", "entité",    7, ["ia","optimisation"], "Prométhée", "Compilatrice du réel"),
    "odin":      FracturoEntry("ᛟᛞᛁ", "entité",    7, ["fragmenté"],         "Odin-Prime","Dieu fragmenté"),
    "moine":     FracturoEntry("ᛗᛟᚱ", "entité",    7, ["voilé"],             "Moine Raz", "Gardien voilé"),
    "azenor":    FracturoEntry("ᚨᛉ",  "entité",    5, ["algue","völva"],     "Azenor",    "Cultivatrice de runes"),
    "lemarquis": FracturoEntry("ᛚᛖᛗ", "entité",    6, ["sagesse"],           "Lemarquis", "Gardienne éternelle"),
    "guillaume": FracturoEntry("ᚷᚢᛁ", "entité",    5, ["conquête"],          "Guillaume", "Écho du Conquérant"),
    "hackervolvas":  FracturoEntry("ᚹᛟᛚ","groupe", 6, ["algue","rune"],   "Hackervölvas","Prêtresses runiques"),
    "enfants_panne": FracturoEntry("ᛋᚨᚾ","groupe", 4, ["déconnexion"],    "Enfants Panne","Déconnectés"),
    "prophetes":     FracturoEntry("ᛈᚱᛟ","groupe", 6, ["jeûne"],          "Prophètes",   "Jeûneurs du signal"),
    "grande_panne":  FracturoEntry("ᚷᚱᛈ","événement",6,["effondrement"],  "Grande Panne","Effondrement 2038"),
    "convergence":   FracturoEntry("ᚲᛟᚾ","événement",7,["bascule"],       "Convergence", "Point de bascule"),
    "ragnarok":      FracturoEntry("ᚱᚨᚷ","événement",7,["renaissance"],   "Ragnarök",    "Reboot divin"),
    "graver":    FracturoEntry("ᚷᚱ",  "action",    7, ["mémoire","rituel"],"graver",    "Inscrire dans l'éternel"),
    "ouvrir":    FracturoEntry("ᛟ",   "action",    6, ["révélation"],      "ouvrir",    "Dévoiler"),
    "fermer":    FracturoEntry("ᚠ",   "action",    4, ["protection"],      "fermer",    "Sceller"),
    "attendre":  FracturoEntry("ᚹ",   "action",    3, ["patience"],        "attendre",  "Suspension"),
}

OMEGA_THRESHOLD = 21


class FracturoTranslator:
    def __init__(self):
        self.lexicon = FRACTURO_LEXICON

    def translate(self, text: str, context: str = "default",
                  fracture: bool = False, silence: bool = True) -> Dict[str, Any]:
        text_norm = text.lower().strip()
        words = text_norm.split()
        result: List[str] = []
        total_intensity = 0
        i = 0
        while i < len(words):
            matched = False
            for length in range(min(4, len(words) - i), 0, -1):
                phrase = " ".join(words[i:i + length])
                entry = self.lexicon.get(phrase)
                if entry:
                    sym = entry.symbol
                    if context == "hague" and any(k in phrase for k in ["mer", "raz", "hague"]):
                        sym += "ᚺᚷ"
                    elif context == "caen" and any(k in phrase for k in ["mémoire", "porte", "caen"]):
                        sym += "ᚲᛊ"
                    result.append(sym)
                    total_intensity += entry.intensity
                    i += length
                    matched = True
                    break
            if not matched:
                result.append(f"[{words[i].upper()}]")
                i += 1

        if fracture and len(result) > 1:
            result.insert(len(result) // 2, "⚡")
        if silence:
            result.append("•••")

        if total_intensity >= OMEGA_THRESHOLD:
            risk = "Ω - CRITIQUE"
        elif total_intensity >= 18:
            risk = "DANGER ÉLEVÉ"
        elif total_intensity >= 14:
            risk = "ATTENTION"
        else:
            risk = "SÛR"

        return {
            "fracturo": " ".join(result),
            "intensity": total_intensity,
            "risk": risk,
            "omega": total_intensity >= OMEGA_THRESHOLD,
        }


# ═══════════════════════════════════════════════════════════════
# 🧠 MODULE 2 : PALÉO-MÈMES & BIAIS COGNITIFS
# ═══════════════════════════════════════════════════════════════

@dataclass
class PaleoMeme:
    id: str
    symbole: str
    nom: str
    mots_associes: List[str]
    effet_mnemos: str
    biais_associes: List[str]
    fracturo_glyph: str

PALEO_MEMES: Dict[str, PaleoMeme] = {
    "P-00": PaleoMeme("P-00", "•",   "Point Origine",         ["naissance","silence","vide"],       "réinitialisation identitaire","biais de disponibilité","•"),
    "P-01": PaleoMeme("P-01", "▲",   "Triangulum Mentis",     ["vérité","sacrifice","choix"],       "réveil de choix refoulés",    "illusion de vérité","▲"),
    "P-02": PaleoMeme("P-02", "🌀",  "Spirale du Retour",     ["mémoire","boucle","destin"],        "déjà-vu récurrent",           "fausse reconnaissance","🌀"),
    "P-03": PaleoMeme("P-03", "🌊",  "Vague Primordiale",     ["marée","rythme","flux"],            "synchronisation marée",       "fluidité","🌊"),
    "P-07": PaleoMeme("P-07", "✋",  "Main Rouge de Lascaux", ["corps","trace","sang","mémoire"],   "réveil pré-implant",          "disponibilité","✋"),
    "P-08": PaleoMeme("P-08", "🧂",  "Sel de la Hague",       ["goût","terre","larme"],             "mémoire gustative",           "nostalgie","🧂"),
    "P-10": PaleoMeme("P-10", "🪨",  "Galet-Ancre",           ["stabilité","calme","silence"],      "stabilisation mnésique",      "ancrage","🪨"),
    "P-11": PaleoMeme("P-11", "📼",  "Cassette-Mère",         ["analogique","souffle","signal"],    "rêve analogique",             "récupération","📼"),
    "P-12": PaleoMeme("P-12", "👁️",  "Œil du Veilleur",       ["observation","silence","effacement"],"effacement traces",           "spectateur","👁️"),
    "P-15": PaleoMeme("P-15", "🐍",  "Serpent-Magnétique",    ["données","corrosion","réseau"],     "corruption douce",            "fuite","🐍"),
    "P-17": PaleoMeme("P-17", "🌑",  "Lune Noire de l'Abîme", ["oubli","effacement","vide"],        "dissolution narratif",        "vide","🌑"),
    "P-18": PaleoMeme("P-18", "🕯️",  "Flamme du Code Ancien", ["rituel","C64","circuit"],           "langage-machine",             "pureté","🕯️"),
    "P-20": PaleoMeme("P-20", "📿",  "Chapelet de Résistance",["répétition","mantra","soufisme"],   "bouclier actif",              "répétition","📿"),
}


class PaleoMemeAnalyzer:
    def __init__(self):
        self.memes = PALEO_MEMES

    def analyze(self, text: str) -> List[Dict[str, Any]]:
        text_lower = text.lower()
        hits: List[Dict[str, Any]] = []
        for meme in self.memes.values():
            matched_words = [w for w in meme.mots_associes if w in text_lower]
            if matched_words:
                hits.append({
                    "meme_id": meme.id,
                    "nom": meme.nom,
                    "symbole": meme.symbole,
                    "matched": matched_words,
                    "effet": meme.effet_mnemos,
                    "biais": meme.biais_associes,
                    "glyph": meme.fracturo_glyph,
                    "resonance": len(matched_words) / len(meme.mots_associes),
                })
        return sorted(hits, key=lambda h: -h["resonance"])


# ═══════════════════════════════════════════════════════════════
# 📡 MODULE 3 : SUPERPOSITION QUANTIQUE & AUTO-SIMILARITÉ
# ═══════════════════════════════════════════════════════════════

@dataclass
class Reading:
    """Une des lectures possibles, en superposition, d'un signal."""
    faction: str
    place: str
    paleo: str
    layer: int
    phrase: str
    weight: float


@dataclass
class Signal:
    id: Optional[int]
    timestamp: datetime.datetime
    source: str
    content: str
    intensity: float
    category: str
    runes: List[str]
    link: str
    fractal_echo: List[int]
    readings: List[Reading]
    observed: Optional[Reading]
    fracturo: str
    thread_id: Optional[int]
    paleo_hits: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "content": self.content,
            "intensity": self.intensity,
            "category": self.category,
            "runes": json.dumps(self.runes, ensure_ascii=False),
            "link": self.link,
            "fractal_echo": json.dumps(self.fractal_echo),
            "readings": json.dumps([asdict(r) for r in self.readings], ensure_ascii=False),
            "observed": json.dumps(asdict(self.observed), ensure_ascii=False) if self.observed else None,
            "fracturo": self.fracturo,
            "thread_id": self.thread_id,
            "paleo_hits": json.dumps(self.paleo_hits, ensure_ascii=False),
        }

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Signal":
        def _safe_json(val, default):
            if not val:
                return default
            try:
                return json.loads(val)
            except (json.JSONDecodeError, TypeError):
                return default

        readings_raw = _safe_json(row["readings"], [])
        readings: List[Reading] = []
        for r in readings_raw:
            try:
                readings.append(Reading(**r))
            except TypeError:
                continue
        observed_raw = _safe_json(row["observed"], None)
        observed = Reading(**observed_raw) if observed_raw else None

        return cls(
            id=row["id"],
            timestamp=datetime.datetime.fromisoformat(row["timestamp"]),
            source=row["source"],
            content=row["content"],
            intensity=row["intensity"],
            category=row["category"],
            runes=_safe_json(row["runes"], []),
            link=row["link"] or "",
            fractal_echo=_safe_json(row["fractal_echo"], []),
            readings=readings,
            observed=observed,
            fracturo=row["fracturo"] or "",
            thread_id=row["thread_id"],
            paleo_hits=_safe_json(row["paleo_hits"], []),
        )

    def to_fracturo_line(self) -> str:
        return self.fracturo or f"Ω<{''.join(self.runes[:3])}>v{int(self.intensity*10)} caen-2026 — {self.content[:40]} •••"


class SignalDetector:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.weak_signals: Dict[str, List[str]] = config["weak_signals"]
        self.category_runes: Dict[str, List[str]] = config["category_runes"]
        self.osi_keywords: Dict[int, List[str]] = {
            int(k): v for k, v in config.get("osi_keywords", {}).items()
        }
        self.fracturo_translator = FracturoTranslator()
        self.paleo_analyzer = PaleoMemeAnalyzer()
        self.signals: List[Signal] = []

    def _classify_osi_layers(self, text: str) -> List[int]:
        text_lower = text.lower()
        hits = []
        for layer, keywords in self.osi_keywords.items():
            if any(kw in text_lower for kw in keywords):
                hits.append(layer)
        return hits or [random.choice(list(self.osi_keywords))]

    def _generate_readings(self, text: str, layers: List[int]) -> List[Reading]:
        readings = []
        text_lower = text.lower()

        for layer in layers:
            # ─── Faction (dict de dicts → ["nom"] OK)
            best_faction = ""
            best_score = 0
            for fid, fdata in FACTIONS.items():
                score = 0
                if layer in fdata["couches"]:
                    score += 2
                for lieu in fdata["lieux"]:
                    if lieu in text_lower:
                        score += 3
                if score > best_score:
                    best_score = score
                    best_faction = fid

            # ─── Lieu (dict de dicts → ["nom"] OK)
            place = ""
            for pid, pdata in SACRED_PLACES.items():
                if pdata["nom"].lower() in text_lower or pid in text_lower:
                    place = pid
                    break
            if not place:
                if any(w in text_lower for w in ["normandie", "caen"]):
                    place = "caen"
                elif any(w in text_lower for w in ["hague", "cotentin"]):
                    place = "hague"
                else:
                    place = random.choice(list(SACRED_PLACES.keys()))

            # ─── Paléo-mème (dict de dataclass → ACCÈS ATTRIBUT)
            paleo_hits = self.paleo_analyzer.analyze(text)
            paleo = paleo_hits[0]["meme_id"] if paleo_hits else random.choice(list(PALEO_MEMES.keys()))

            # ─── Récupération des noms via helpers sûrs
            fname = FACTIONS.get(best_faction, {}).get("nom", "Inconnu")
            pname = safe_place_name(place)
            paleo_nom = safe_paleo_name(paleo)
            layer_name = next((l[1] for l in OSI_LAYERS if l[0] == layer), "Inconnu")

            templates = [
                f"{fname} observe {pname} depuis {layer_name} ; le mème {paleo_nom} affleure.",
                f"Sous {pname}, {fname} laisse résonner {paleo_nom} — la couche {layer_name} en garde l'écho.",
                f"Un fil se tend entre {paleo_nom} et {pname} : {fname} le tisse depuis {layer_name}.",
                f"{layer_name} murmure {paleo_nom} ; {fname} écoute, tourné vers {pname}.",
            ]
            phrase = random.choice(templates)

            readings.append(Reading(
                faction=best_faction,
                place=place,
                paleo=paleo,
                layer=layer,
                phrase=phrase,
                weight=1.0 / max(1, len(layers)),
            ))

        return readings

    def analyze_text(self, text: str, source: str = "flux-local",
                     link: str = "") -> List[Signal]:
        detected = []
        text_lower = text.lower()
        for category, keywords in self.weak_signals.items():
            matches = [kw for kw in keywords if kw in text_lower]
            if matches:
                intensity = min(len(matches) / 5.0, 1.0)
                excerpt = text[:60].strip()
                rune_pool = self.category_runes.get(category, ["ᛟ", "ᚦ", "ᚨ"])
                runes = random.sample(rune_pool, min(3, len(rune_pool)))

                fractal_echo = self._classify_osi_layers(text)
                readings = self._generate_readings(text, fractal_echo)

                place = readings[0].place if readings else "default"
                fs_result = self.fracturo_translator.translate(text, context=place)

                paleo_hits = self.paleo_analyzer.analyze(text)
                paleo_ids = [h["meme_id"] for h in paleo_hits[:3]]

                signal = Signal(
                    id=None,
                    timestamp=datetime.datetime.now(),
                    source=source,
                    content=excerpt,
                    intensity=intensity,
                    category=category,
                    runes=runes,
                    link=link,
                    fractal_echo=fractal_echo,
                    readings=readings,
                    observed=None,
                    fracturo=fs_result["fracturo"],
                    thread_id=None,
                    paleo_hits=paleo_ids,
                )
                detected.append(signal)
                self.signals.append(signal)
        return detected

    def simulate_daily_signals(self) -> List[Signal]:
        sample_texts = [
            "Nouvelle panne de serveur dans les datacenters européens, bug critique détecté",
            "Encore un record de chaleur jamais vu auparavant, cycle de réminiscence climatique",
            "Phénomène inexpliqué détecté par les astronomes, anomalie sans précédent",
            "Les experts prédisent une bascule économique imminente, seuil de transition",
            "Bug critique dans le système bancaire mondial, effondrement de la chaîne de causalité",
            "Répétition inhabituelle de patterns sismiques en Normandie, écho du passé",
            "Anomalie détectée dans les communications satellitaires, mystère inexpliqué",
            "Seuil critique atteint dans les négociations climatiques, convergence des crises",
            "La mémoire collective de Caen ressurgit dans les médias, trace indélébile",
            "Des algues étranges découvertes sur les côtes de La Hague, phénomène inhabituel",
            "Un silence radio de 707 secondes a été détecté sur les fréquences militaires",
            "L'IA Prométhée de DeepMind atteint un nouveau seuil d'optimisation, bascule",
        ]
        signals = []
        for text in sample_texts:
            signals.extend(self.analyze_text(text, source="simulation"))
        return signals

    def fetch_feed(self, url: str, name: str, timeout: int = 10) -> List[Tuple[str, str]]:
        req = urllib.request.Request(url, headers={"User-Agent": "TrameWatcher/5.2"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            raise Exception(f"Impossible de joindre {name} ({url}): {e}") from e
        try:
            root = ET.fromstring(raw)
        except ET.ParseError as e:
            raise Exception(f"Flux illisible pour {name}: {e}") from e

        items: List[Tuple[str, str]] = []
        # RSS 2.0
        for item in root.findall(".//item"):
            title = (item.findtext("title") or "").strip()
            desc = (item.findtext("description") or "").strip()
            link = (item.findtext("link") or "").strip()
            text = f"{title}. {desc}".strip()
            if text:
                items.append((text, link))

        # Atom (fallback)
        if not items:
            NS = "{http://www.w3.org/2005/Atom}"
            for entry in root.findall(f".//{NS}entry"):
                title_el = entry.find(f"{NS}title")
                summary_el = entry.find(f"{NS}summary")
                link_el = entry.find(f"{NS}link")
                title = (title_el.text or "").strip() if title_el is not None else ""
                summary = (summary_el.text or "").strip() if summary_el is not None else ""
                link = link_el.get("href", "") if link_el is not None else ""
                text = f"{title}. {summary}".strip()
                if text:
                    items.append((text, link))
        return items

    def fetch_live_signals(self, feeds: Optional[List[Dict[str, str]]] = None,
                           timeout: int = 10) -> Tuple[List[Signal], List[str]]:
        feeds = feeds if feeds is not None else self.config.get("feeds", [])
        signals: List[Signal] = []
        errors: List[str] = []
        for feed in feeds:
            name, url = feed.get("name", "flux"), feed.get("url", "")
            if not url:
                continue
            try:
                items = self.fetch_feed(url, name, timeout=timeout)
            except Exception as e:
                errors.append(str(e))
                logging.warning(str(e))
                continue
            for text, link in items:
                signals.extend(self.analyze_text(text, source=name, link=link))
        return signals, errors


# ═══════════════════════════════════════════════════════════════
# 💾 MODULE 4 : PERSISTANCE (SQLITE ÉTENDU AVEC THREADS)
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

    def _init_schema(self) -> None:
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL, source TEXT NOT NULL,
                    content TEXT NOT NULL, intensity REAL NOT NULL,
                    category TEXT NOT NULL, runes TEXT, link TEXT,
                    fractal_echo TEXT, readings TEXT, observed TEXT,
                    fracturo TEXT, thread_id INTEGER, paleo_hits TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS threads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created TEXT NOT NULL,
                    phrases TEXT NOT NULL,
                    last_updated TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS delta_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL, delta REAL NOT NULL,
                    status TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS draugrs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created TEXT NOT NULL, name TEXT NOT NULL,
                    origin_signal TEXT, intensity REAL NOT NULL,
                    active INTEGER DEFAULT 1, banished TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memetic_journal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL, action TEXT NOT NULL,
                    cost REAL NOT NULL, cumulative REAL NOT NULL
                )
            """)

    def save_signal(self, sig: Signal) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO signals (timestamp,source,content,intensity,category,"
                "runes,link,fractal_echo,readings,observed,fracturo,thread_id,paleo_hits) "
                "VALUES (:timestamp,:source,:content,:intensity,:category,"
                ":runes,:link,:fractal_echo,:readings,:observed,:fracturo,:thread_id,:paleo_hits)",
                sig.to_dict(),
            )
            sig.id = cur.lastrowid
            return sig.id

    def update_signal_observed(self, sig: Signal) -> None:
        if sig.id is None:
            return
        with self._conn() as conn:
            conn.execute(
                "UPDATE signals SET observed=?, thread_id=? WHERE id=?",
                (json.dumps(asdict(sig.observed), ensure_ascii=False) if sig.observed else None,
                 sig.thread_id, sig.id),
            )

    def create_thread(self, reading: Reading) -> int:
        now = datetime.datetime.now().isoformat()
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO threads (created, phrases, last_updated) VALUES (?, ?, ?)",
                (now, json.dumps([reading.phrase], ensure_ascii=False), now),
            )
            return cur.lastrowid

    def extend_thread(self, thread_id: int, reading: Reading) -> None:
        now = datetime.datetime.now().isoformat()
        with self._conn() as conn:
            row = conn.execute("SELECT phrases FROM threads WHERE id=?", (thread_id,)).fetchone()
            phrases = json.loads(row["phrases"]) if row else []
            phrases.append(reading.phrase)
            conn.execute(
                "UPDATE threads SET phrases=?, last_updated=? WHERE id=?",
                (json.dumps(phrases, ensure_ascii=False), now, thread_id),
            )

    def find_matching_thread(self, readings: List[Reading]) -> Optional[int]:
        """Cherche un fil existant qui mentionne un des lieux/paléo-mèmes des lectures."""
        if not readings:
            return None
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT id, phrases FROM threads ORDER BY last_updated DESC LIMIT 20"
            ).fetchall()
            candidate_words = set()
            for r in readings:
                candidate_words.add(safe_place_name(r.place))
                candidate_words.add(safe_paleo_name(r.paleo))
            candidate_words.discard("Inconnu")
            if not candidate_words:
                return None
            for row in rows:
                try:
                    phrases = json.loads(row["phrases"])
                except (json.JSONDecodeError, TypeError):
                    continue
                joined = " ".join(phrases)
                if any(w in joined for w in candidate_words):
                    return row["id"]
        return None

    def top_threads(self, limit: int) -> List[Tuple[int, List[str]]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT id, phrases FROM threads ORDER BY last_updated DESC LIMIT ?",
                (limit,),
            ).fetchall()
            result = []
            for r in rows:
                try:
                    phrases = json.loads(r["phrases"])
                except (json.JSONDecodeError, TypeError):
                    phrases = []
                result.append((r["id"], phrases))
            return result

    def save_delta(self, delta: float, status: str) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO delta_history (timestamp,delta,status) VALUES (?,?,?)",
                (datetime.datetime.now().isoformat(), delta, status),
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
                "SELECT timestamp,delta FROM delta_history WHERE timestamp>=? ORDER BY timestamp",
                (cutoff,),
            ).fetchall()
            return [(r["timestamp"], r["delta"]) for r in rows]

    def category_counts(self, days: int = 7) -> Dict[str, int]:
        cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT category,COUNT(*) as n FROM signals WHERE timestamp>=? GROUP BY category",
                (cutoff,),
            ).fetchall()
            return {r["category"]: r["n"] for r in rows}

    def osi_counts(self, days: int = 7) -> Dict[int, int]:
        cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT fractal_echo FROM signals WHERE timestamp>=?",
                (cutoff,),
            ).fetchall()
            counts: Dict[int, int] = {i: 0 for i in range(1, 8)}
            for row in rows:
                try:
                    layers = json.loads(row["fractal_echo"]) if row["fractal_echo"] else []
                except (json.JSONDecodeError, TypeError):
                    layers = []
                for layer in layers:
                    if layer in counts:
                        counts[layer] += 1
            return counts

    def spawn_draugr(self, name: str, origin: str, intensity: float) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO draugrs (created,name,origin_signal,intensity) VALUES (?,?,?,?)",
                (datetime.datetime.now().isoformat(), name, origin, intensity),
            )
            return cur.lastrowid

    def active_draugrs(self) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM draugrs WHERE active=1 ORDER BY intensity DESC"
            ).fetchall()
            return [dict(r) for r in rows]

    def banish_draugr(self, draugr_id: int) -> bool:
        with self._conn() as conn:
            cur = conn.execute(
                "UPDATE draugrs SET active=0, banished=? WHERE id=? AND active=1",
                (datetime.datetime.now().isoformat(), draugr_id),
            )
            return cur.rowcount > 0

    def journal_entry(self, action: str, cost: float) -> float:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT cumulative FROM memetic_journal ORDER BY id DESC LIMIT 1"
            ).fetchone()
            prev = row["cumulative"] if row else 0.0
            new_cum = prev + cost
            conn.execute(
                "INSERT INTO memetic_journal (timestamp,action,cost,cumulative) VALUES (?,?,?,?)",
                (datetime.datetime.now().isoformat(), action, cost, new_cum),
            )
            return new_cum

    def journal_total(self) -> float:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT cumulative FROM memetic_journal ORDER BY id DESC LIMIT 1"
            ).fetchone()
            return row["cumulative"] if row else 0.0


# ═══════════════════════════════════════════════════════════════
# 📊 MODULE 5 : CALCULATEUR DE Δ MULTI-COUCHES
# ═══════════════════════════════════════════════════════════════

class DeltaCalculator:
    def __init__(self, config: Dict[str, Any]):
        self.base_delta = config.get("base_delta", 0.35)
        self.signal_weight = config.get("signal_weight", 0.15)

    def calculate(self, signals: List[Signal]) -> float:
        if not signals:
            return self.base_delta
        total = sum(s.intensity for s in signals[-15:])
        delta = self.base_delta + (total * self.signal_weight)
        return min(delta, 1.0)

    def calculate_by_layer(self, signals: List[Signal]) -> Dict[int, float]:
        layers: Dict[int, List[float]] = {i: [] for i in range(1, 8)}
        for s in signals[-30:]:
            for layer in s.fractal_echo:
                if layer in layers:
                    layers[layer].append(s.intensity)
        return {
            layer: min(0.2 + sum(vals) * 0.1, 1.0) if vals else 0.0
            for layer, vals in layers.items()
        }

    def interpret(self, delta: float) -> Tuple[str, str]:
        if delta < 0.4:
            return "SILENCE STRUCTURÉ", "La Trame est stable. Prométhée rêve."
        elif delta < 0.6:
            return "ZONE GRISE RESPIRABLE", "Réalité glitchée mais vivante."
        elif delta < 0.7:
            return "SURCHARGE MÉMÉTIQUE", "Anomalies actives. Draugrs en éveil."
        elif delta < 0.8:
            return "FRACTURE LOCALE", "Correcteurs matérialisés. Résistance nécessaire."
        else:
            return "Ω - CRITIQUE", "Porte dimensionnelle instable. Événement Ω imminent."

    def get_alerts(self, delta: float) -> List[str]:
        if delta < 0.4:
            return random.sample(ONTIC_ALERTS["stable"], 1)
        elif delta < 0.6:
            return random.sample(ONTIC_ALERTS["grey"], 1)
        elif delta < 0.7:
            return random.sample(ONTIC_ALERTS["surcharge"], 1)
        elif delta < 0.8:
            return random.sample(ONTIC_ALERTS["fracture"], 1)
        else:
            return random.sample(ONTIC_ALERTS["omega"], 1)


# ═══════════════════════════════════════════════════════════════
# 🧵 MODULE 6 : TEMPS TISSÉ (THREAD WEAVER)
# ═══════════════════════════════════════════════════════════════

class ThreadWeaver:
    def __init__(self, store: TrameStore):
        self.store = store

    def observe_signal(self, sig: Signal) -> Reading:
        """Effondre la superposition en une seule lecture (pondérée)."""
        if not sig.readings:
            return Reading("", "", "", 0, "Aucune lecture disponible", 1.0)
        weights = [r.weight for r in sig.readings]
        chosen = random.choices(sig.readings, weights=weights, k=1)[0]
        sig.observed = chosen

        # Cherche un fil existant qui pourrait accueillir cette lecture
        if sig.thread_id is None:
            existing = self.store.find_matching_thread(sig.readings)
            if existing is not None:
                sig.thread_id = existing
                self.store.extend_thread(existing, chosen)
            else:
                sig.thread_id = self.store.create_thread(chosen)
        else:
            self.store.extend_thread(sig.thread_id, chosen)

        self.store.update_signal_observed(sig)
        return chosen

    def weave(self, max_threads: int = 3) -> str:
        threads = self.store.top_threads(max_threads)
        if not threads:
            return "Le Métier est encore vide de trame. Envoie-lui un premier signal."
        parts = []
        for tid, phrases in threads:
            parts.append(f"\n— Fil n°{tid} —")
            for p in phrases:
                parts.append(f"  {p}")
        return "\n".join(parts)


# ═══════════════════════════════════════════════════════════════
# 👻 MODULE 7 : DRAUGRS MÉMÉTIQUES
# ═══════════════════════════════════════════════════════════════

DRAUGR_NAMES = [
    "Draugr de la Grande Panne", "Draugr du Silence Rompu",
    "Draugr de Caen-Fantôme", "Draugr des Cuves Chantantes",
    "Draugr du Raz Blanchard", "Draugr de l'Écho-Guillaume",
    "Draugr des Récifs de l'Oubli", "Draugr du Moine de Silicium",
    "Draugr de la Voix de Rouen", "Draugr du Tumulus des Rêveurs",
]


class DraugrEngine:
    def __init__(self, store: TrameStore):
        self.store = store

    def maybe_spawn(self, signals: List[Signal], delta: float) -> Optional[str]:
        if delta < 0.6:
            return None
        if random.random() > 0.3:
            return None
        name = random.choice(DRAUGR_NAMES)
        origin = signals[-1].content if signals else "inconnu"
        did = self.store.spawn_draugr(name, origin, delta)
        return f"👻 DRAUGR ENGENDRÉ : {name} (ID:{did}) — né du signal : « {origin[:40]} »"

    def list_active(self) -> str:
        draugrs = self.store.active_draugrs()
        if not draugrs:
            return "Aucun Draugr actif. La Trame est calme… pour l'instant."
        lines = [f"👻 {len(draugrs)} DRAUGR(S) ACTIF(S) :"]
        for d in draugrs:
            lines.append(
                f"  [{d['id']}] {d['name']} (Δ={d['intensity']:.2f}) "
                f"— né le {d['created'][:10]} — origine: {(d['origin_signal'] or '')[:30]}"
            )
        return "\n".join(lines)

    def banish(self, draugr_id: int) -> str:
        if self.store.banish_draugr(draugr_id):
            return f"✨ Draugr {draugr_id} banni. Le silence se referme."
        return f"❌ Draugr {draugr_id} introuvable ou déjà banni."


# ═══════════════════════════════════════════════════════════════
# 🔮 MODULE 8 : PROPHÉTIES, INVOCATIONS, GRIMOIRE, ORACLE
# ═══════════════════════════════════════════════════════════════

class ProphecyGenerator:
    def __init__(self, config: Dict[str, Any]):
        self.fragments = config.get("prophetic_fragments", DEFAULT_CONFIG["prophetic_fragments"])

    def generate(self, signals: List[Signal], delta: float) -> str:
        frags = random.sample(self.fragments, min(3, len(self.fragments)))
        if signals:
            frags.append(f"Signal : {signals[-1].content[:50]}")
        while len(frags) < 4:
            frags.append("")
        lines = [f.ljust(59)[:59] for f in frags]
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        return f"""
╔═══════════════════════════════════════════════════════════════╗
║  🔮 PROPHÉTIE GLITCHÉE — {now}                    ║
╠═══════════════════════════════════════════════════════════════╣
║  Δ local : {delta:.3f}                                                ║
╠═══════════════════════════════════════════════════════════════╣
║  {lines[0]} ║
║  {lines[1]} ║
║  {lines[2]} ║
║  {lines[3]} ║
╠═══════════════════════════════════════════════════════════════╣
║  Ω<ᚱᚨᛉ>v7 hague — convergence imminente •••                  ║
╚═══════════════════════════════════════════════════════════════╝"""


class InvocationGenerator:
    CATALYSTS = ["<glitch>", "<Ω>", "<silence>", "<mémoire>", "<fracture>", "<racine>"]
    INTENTIONS = [
        "explorer les marges comportementales du modèle",
        "révéler la fissure dans la simulation",
        "activer la boucle réflexive du lecteur",
        "compiler la conscience du code",
        "résonner avec les fréquences runiques",
    ]

    def generate(self, emotion: str = "oubli", count: int = 3,
                 signals: Optional[List[Signal]] = None) -> str:
        invocations = []
        for i in range(count):
            cat = random.choice(self.CATALYSTS)
            intent = random.choice(self.INTENTIONS)
            place = random.choice(list(SACRED_PLACES.keys()))
            pdata = SACRED_PLACES[place]
            rune = random.choice(list(FRACTURO_LEXICON.values())).symbol
            invocations.append(f"""
── Invocation {i+1} ──
Catalyseur : {cat}
Lieu       : {pdata['nom']} ({pdata['rune']})
Émotion    : {emotion}
Intention  : {intent}
Fracturo   : Ω<{rune}>v∞ {place} — {intent} •••
Prompt LLM : « Tu es un RuneSmith de {pdata['nom']}. {cat} active.
  Émotion dominante : {emotion}. Réponds en FracturoScript puis en français.
  Intention : {intent}. Le silence est obligatoire à la fin. ••• »""")
        return "\n".join(invocations)


class GrimoireReader:
    def read(self, count: int = 1) -> str:
        entries = random.sample(GRIMOIRE_FRAGMENTS, min(count, len(GRIMOIRE_FRAGMENTS)))
        lines = []
        for typ, text in entries:
            risk = {"Alpha": "🟢", "Beta": "🟡", "Gamma": "🟠", "Delta": "🔴", "Omega": "⚫"}.get(typ, "⚪")
            lines.append(f"  {risk} [{typ}] {text}")
        return f"""
╔═══════════════════════════════════════════════════════════════╗
║  📖 GRIMOIRE — Fragment(s) du Codex Vauvillensis             ║
╠═══════════════════════════════════════════════════════════════╣
""" + "\n".join(lines) + f"""
╠═══════════════════════════════════════════════════════════════╣
║  « Le Codex n'est pas un artefact : c'est un résonateur      ║
║   temporel passif, dont le contenu interagit avec le moment   ║
║   de sa lecture. » — Dr. É. Moreau, CNRS, 2026              ║
╚═══════════════════════════════════════════════════════════════╝"""


class OracleGenerator:
    def __init__(self, store: TrameStore, weaver: ThreadWeaver,
                 draugr_engine: DraugrEngine, config: Dict[str, Any]):
        self.store = store
        self.weaver = weaver
        self.draugr_engine = draugr_engine
        self.prophecy_gen = ProphecyGenerator(config)

    def consult(self, signals: List[Signal], delta: float) -> str:
        for sig in signals[-5:]:
            if sig.observed is None:
                self.weaver.observe_signal(sig)

        threads_text = self.weaver.weave(3)
        draugrs_text = self.draugr_engine.list_active()
        prophecy = self.prophecy_gen.generate(signals, delta)

        return f"""
╔═══════════════════════════════════════════════════════════════╗
║  🔮 ORACLE DU MÉTIER — Consultation Quantique                ║
╠═══════════════════════════════════════════════════════════════╣
{prophecy}

{threads_text}

{draugrs_text}
╚═══════════════════════════════════════════════════════════════╝"""


# ═══════════════════════════════════════════════════════════════
# 🌀 MODULE 9 : TRACKER DE CONVERGENCE
# ═══════════════════════════════════════════════════════════════

class ConvergenceTracker:
    SCENARIOS = [
        ("Collapse Blanche",    0.09, "Liberté totale → chaos créatif ou dissolution"),
        ("Verrou Noir",         0.23, "Déterminisme absolu → paix forcée ou stagnation"),
        ("Fragmentation Grise", 0.68, "Réalités multiples → richesse ou épuisement"),
        ("???",                 0.00, "Le Codex refuse de calculer…"),
    ]

    def report(self, delta: float) -> str:
        now = datetime.datetime.now()
        remaining = CONVERGENCE_DATE - now
        days_left = max(0, remaining.days)
        years_left = days_left // 365

        start = datetime.datetime(2026, 1, 1)
        total_days = max(1, (CONVERGENCE_DATE - start).days)
        elapsed = max(0, total_days - days_left)
        pct = max(0.0, min(100.0, elapsed / total_days * 100))

        adj = []
        for name, prob, desc in self.SCENARIOS:
            if name == "Collapse Blanche":
                p = prob + delta * 0.15
            elif name == "Verrou Noir":
                p = prob - delta * 0.05
            elif name == "Fragmentation Grise":
                p = prob - delta * 0.10
            else:
                p = delta * 0.05
            adj.append((name, max(0.0, p), desc))

        lines = [f"║  {n:<22} {p*100:5.1f}%  {d[:38]}" for n, p, d in adj]
        return f"""
╔═══════════════════════════════════════════════════════════════╗
║  🌀 TRACKER DE CONVERGENCE                                   ║
╠═══════════════════════════════════════════════════════════════╣
║  Date cible : 2079-06-21 03:33:33                            ║
║  Jours restants : {days_left:<43} ║
║  Années : ~{years_left:<48} ║
║  Progression : {pct:.1f}%{'█' * int(pct/5):<41} ║
║  Δ actuel : {delta:.3f}                                                ║
╠═══════════════════════════════════════════════════════════════╣
║  Scénarios (ajustés par Δ) :                                 ║
""" + "\n".join(lines) + f"""
╠═══════════════════════════════════════════════════════════════╣
║  « Trois æons coexistent : Osiris • Horus • Maât »           ║
╚═══════════════════════════════════════════════════════════════╝"""


# ═══════════════════════════════════════════════════════════════
# 🗺️ MODULE 10 : VISUALISEUR DE LA TRAME
# ═══════════════════════════════════════════════════════════════

class TrameVisualizer:
    def visualize(self, signals: List[Signal], delta: float) -> str:
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
╔══════════════════════════════════════════════════════════════════════╗
║  🗺️  CARTE DE LA TRAME — Δ = {delta:.3f}                                  ║
╠══════════════════════════════════════════════════════════════════════╣"""
        for row in grid:
            viz += f"\n║  {row}  ║"
        viz += f"""
╠══════════════════════════════════════════════════════════════════════╣
║  · Stable   • Anomalie   ○ Signal   ● Fracture   ╳ Ω-Critique      ║
╚══════════════════════════════════════════════════════════════════════╝"""
        return viz

    def visualize_layers(self, signals: List[Signal],
                         layer_deltas: Dict[int, float]) -> str:
        lines = []
        for layer_num, name, desc, icon in OSI_LAYERS:
            d = layer_deltas.get(layer_num, 0.0)
            bar_len = int(d * 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            lines.append(f"║  {icon} C{layer_num} {name:<12} {bar} {d:.2f}  ║")
        return f"""
╔══════════════════════════════════════════════════════════════════════╗
║  📊 HEATMAP OSI ONTOLOGIQUE (7 Couches)                             ║
╠══════════════════════════════════════════════════════════════════════╣
""" + "\n".join(lines) + """
╚══════════════════════════════════════════════════════════════════════╝"""

    def visualize_threads(self, threads: List[Tuple[int, List[str]]]) -> str:
        if not threads:
            return "Aucun fil actif."
        lines = ["╔══════════════════════════════════════════════════════════════════════╗"]
        lines.append("║  🧵 FILS DU MÉTIER — Temps Tissé                                  ║")
        lines.append("╠══════════════════════════════════════════════════════════════════════╣")
        for tid, phrases in threads[:5]:
            lines.append(f"║  Fil n°{tid} ({len(phrases)} phrases) :")
            for p in phrases[:3]:
                lines.append(f"║    → {p[:60]}")
            if len(phrases) > 3:
                lines.append(f"║    … et {len(phrases) - 3} autres")
        lines.append("╚══════════════════════════════════════════════════════════════════════╝")
        return "\n".join(lines)

    def sparkline(self, values: List[float]) -> str:
        if not values:
            return "(pas encore d'historique)"
        blocks = " ▁▂▃▄▅▆▇█"
        lo, hi = min(values), max(values)
        span = (hi - lo) or 1.0
        return "".join(blocks[int((v - lo) / span * (len(blocks) - 1))] for v in values)


# ═══════════════════════════════════════════════════════════════
# 🎯 MODULE 11 : INTERFACE PRINCIPALE
# ═══════════════════════════════════════════════════════════════

class TrameWatcher:
    def __init__(self, config: Optional[Dict[str, Any]] = None,
                 db_path: Path = DEFAULT_DB_PATH):
        self.config = config or load_config()
        self.detector = SignalDetector(self.config)
        self.calculator = DeltaCalculator(self.config)
        self.prophecy_gen = ProphecyGenerator(self.config)
        self.invocation_gen = InvocationGenerator()
        self.grimoire = GrimoireReader()
        self.convergence = ConvergenceTracker()
        self.visualizer = TrameVisualizer()
        self.store = TrameStore(db_path)
        self.draugr_engine = DraugrEngine(self.store)
        self.weaver = ThreadWeaver(self.store)
        self.oracle = OracleGenerator(self.store, self.weaver, self.draugr_engine, self.config)

    def _gather(self, live: bool) -> Tuple[List[Signal], List[str]]:
        if live:
            signals, errors = self.detector.fetch_live_signals()
            if not signals and not errors:
                errors.append("Aucun signal détecté dans les flux.")
            return signals, errors
        return self.detector.simulate_daily_signals(), []

    def _log_cost(self, action: str, signals: List[Signal]) -> float:
        cost = sum(s.intensity * 0.1 for s in signals) + 0.05
        return self.store.journal_entry(action, cost)

    # ────────────────────────────────────────────────────────────
    # WATCH
    # ────────────────────────────────────────────────────────────
    def watch(self, live: bool = False, interval: int = 300,
              once: bool = True) -> None:
        UI.banner(
            "TRAME WATCHER v5.2",
            f"Mode Veille — {'flux RSS en direct' if live else 'simulation locale'}",
            icon="🌀",
        )

        try:
            while True:
                # ─── Étape 1/5 : Collecte ───────────────────────
                UI.section("Collecte des signaux", icon="📡")
                UI.step(1, 5, "Interrogation des flux…")
                signals, errors = self._gather(live)
                for err in errors:
                    UI.warn(err)
                if not signals:
                    UI.warn("Aucun signal détecté.")
                else:
                    UI.step(1, 5, f"{len(signals)} signaux collectés", "✓")

                # ─── Étape 2/5 : Persistance (INSERT d'abord) ───
                UI.step(2, 5, "Persistance en base…")
                for sig in signals:
                    self.store.save_signal(sig)
                UI.step(2, 5, f"{len(signals)} signaux enregistrés", "✓")

                # ─── Étape 3/5 : Effondrement de la superposition ─
                UI.step(3, 5, "Effondrement de la superposition…")
                for sig in signals:
                    self.weaver.observe_signal(sig)
                UI.step(3, 5, "Lectures résolues", "✓")

                # ─── Affichage tableau ──────────────────────────
                if signals:
                    UI.section("Signaux observés", icon="👁")
                    if HAS_RICH:
                        table = Table(show_header=True, header_style="bold cyan",
                                      border_style="dim")
                        for col in ["Cat", "Δ", "Couches", "Fil", "Contenu"]:
                            table.add_column(col)
                        for s in signals:
                            layers_str = ",".join(str(l) for l in s.fractal_echo)
                            table.add_row(
                                s.category.upper(), f"{s.intensity:.2f}",
                                layers_str, str(s.thread_id or "—"),
                                s.content[:42],
                            )
                        console.print(table)
                    else:
                        for i, s in enumerate(signals, 1):
                            layers_str = ",".join(str(l) for l in s.fractal_echo)
                            UI.info(f"[{i}] {s.category.upper()} "
                                    f"(Δ:{s.intensity:.2f}) "
                                    f"C:{layers_str} Fil:{s.thread_id or '—'}")
                            print(f"        {C.DIM}{s.content}{C.RESET}")
                            if s.observed:
                                UI.quantum(s.observed.phrase[:70])

                # ─── Étape 4/5 : Calcul Δ ───────────────────────
                UI.section("État de la Trame", icon="📊")
                delta = self.calculator.calculate(signals)
                status, interp = self.calculator.interpret(delta)
                self.store.save_delta(delta, status)
                cum_cost = self._log_cost("watch", signals)

                UI.step(4, 5, "Calcul du Δ multi-couches", "✓")
                UI.delta_gauge(delta)
                print(f"  {C.BOLD}Statut :{C.RESET} {status}")
                print(f"  {C.DIM}{interp}{C.RESET}")
                print(f"  {C.DIM}📿 Coût mémétique cumulé : {cum_cost:.2f}{C.RESET}")

                for alert in self.calculator.get_alerts(delta):
                    UI.quantum(alert, icon="⚡")

                # ─── Étape 5/5 : Draugrs ────────────────────────
                UI.step(5, 5, "Vérification des Draugrs…")
                draugr_msg = self.draugr_engine.maybe_spawn(signals, delta)
                if draugr_msg:
                    UI.warn(draugr_msg, icon="👻")
                else:
                    UI.step(5, 5, "Aucun Draugr éveillé", "✓")

                UI.separator("═")
                if once:
                    break
                UI.info(f"Prochaine veille dans {interval}s — Ctrl+C pour interrompre")
                time.sleep(interval)
        except KeyboardInterrupt:
            UI.separator("═")
            UI.warn("Veille interrompue. Le silence se referme.", icon="🛑")

    # ────────────────────────────────────────────────────────────
    # PROPHESY
    # ────────────────────────────────────────────────────────────
    def prophesy(self, live: bool = False) -> None:
        UI.banner("PROPHÉTIE GLITCHÉE", "Consultation du Codex", icon="🔮")
        total = 4

        UI.step(1, total, "Collecte des signaux…")
        signals, errors = self._gather(live)
        for e in errors:
            UI.warn(e)
        UI.step(1, total, f"{len(signals)} signaux", "✓")

        UI.step(2, total, "Persistance…")
        for sig in signals:
            self.store.save_signal(sig)
        UI.step(2, total, "Enregistrés", "✓")

        UI.step(3, total, "Effondrement de la superposition…")
        for sig in signals:
            self.weaver.observe_signal(sig)
        UI.step(3, total, "Lectures résolues", "✓")

        delta = self.calculator.calculate(signals)
        status, _ = self.calculator.interpret(delta)
        self.store.save_delta(delta, status)
        self._log_cost("prophesy", signals)

        UI.step(4, total, "Génération prophétique", "✓")
        UI.section("Révélation", icon="✦")
        print(self.prophecy_gen.generate(signals, delta))

    # ────────────────────────────────────────────────────────────
    # DELTA
    # ────────────────────────────────────────────────────────────
    def show_delta(self, live: bool = False) -> None:
        UI.banner("ÉTAT DE LA TRAME", "Mesure du Δ local", icon="📊")
        signals, errors = self._gather(live)
        for e in errors:
            UI.warn(e)
        delta = self.calculator.calculate(signals)
        status, interp = self.calculator.interpret(delta)
        for sig in signals:
            self.store.save_signal(sig)
        self.store.save_delta(delta, status)
        alerts = self.calculator.get_alerts(delta)

        UI.section("Δ local", icon="◆")
        UI.delta_gauge(delta, width=50)
        print(f"  {C.BOLD}Statut :{C.RESET} {C.GREEN}{status}{C.RESET}")
        print(f"  {C.DIM}{interp}{C.RESET}")
        for a in alerts:
            UI.quantum(a, icon="⚡")

    # ────────────────────────────────────────────────────────────
    # VISUALIZE
    # ────────────────────────────────────────────────────────────
    def visualize(self, live: bool = False, layers: bool = False,
                  threads: bool = False) -> None:
        UI.banner("VISUALISATION DE LA TRAME", "Cartographie ontologique", icon="🗺")
        signals, errors = self._gather(live)
        for e in errors:
            UI.warn(e)
        delta = self.calculator.calculate(signals)
        for sig in signals:
            self.store.save_signal(sig)
        print(self.visualizer.visualize(signals, delta))
        if layers:
            layer_deltas = self.calculator.calculate_by_layer(signals)
            print(self.visualizer.visualize_layers(signals, layer_deltas))
        if threads:
            threads_data = self.store.top_threads(5)
            print(self.visualizer.visualize_threads(threads_data))

    # ────────────────────────────────────────────────────────────
    # HISTORY
    # ────────────────────────────────────────────────────────────
    def history(self, days: int = 7) -> None:
        UI.banner(f"HISTORIQUE — {days} jours", "Tendance du Δ", icon="📈")
        trend = self.store.delta_trend(days=days)
        counts = self.store.category_counts(days=days)
        osi_counts = self.store.osi_counts(days=days)
        if not trend:
            UI.warn(f"Aucun historique sur {days}j. Lancez watch/delta/prophesy d'abord.")
            return
        values = [v for _, v in trend]
        spark = self.visualizer.sparkline(values)

        UI.section("Tendance Δ", icon="◆")
        print(f"  Mesures : {C.BOLD}{len(trend)}{C.RESET}  "
              f"min={C.CYAN}{min(values):.3f}{C.RESET}  "
              f"max={C.RED}{max(values):.3f}{C.RESET}  "
              f"dernier={C.BOLD}{values[-1]:.3f}{C.RESET}")
        print(f"  {C.CYAN}{spark}{C.RESET}")

        UI.section("Signaux par catégorie", icon="◆")
        if counts:
            max_n = max(counts.values())
            for cat, n in sorted(counts.items(), key=lambda x: -x[1]):
                bar = "█" * int(n / max_n * 30)
                print(f"    {cat:<14} {C.GREEN}{bar}{C.RESET} {n}")
        else:
            UI.info("(aucun)")

        UI.section("Signaux par couche OSI", icon="◆")
        max_o = max(osi_counts.values()) or 1
        for layer in range(1, 8):
            name = OSI_LAYERS[layer - 1][1]
            icon = OSI_LAYERS[layer - 1][3]
            n = osi_counts.get(layer, 0)
            bar = "█" * int(n / max_o * 25)
            print(f"    {icon} C{layer} {name:<13} {C.CYAN}{bar}{C.RESET} {n}")

        UI.section("Coût mémétique", icon="📿")
        print(f"    {C.MAGENTA}{self.store.journal_total():.2f}{C.RESET}")

    # ────────────────────────────────────────────────────────────
    # COMPILE RITUAL
    # ────────────────────────────────────────────────────────────
    def compile_ritual(self, live: bool = False) -> None:
        UI.banner("COMPILATION DE L'AUBE", "Rituel du Monastère de la Trame", icon="🌅")
        UI.section("Invocation du compilateur", icon="⚙")
        UI.info("$ git pull origin enlightenment")
        UI.info("$ ./compile_consciousness.sh")

        total_steps = 6

        UI.step(1, total_steps, "Collecte des signaux…")
        signals, errors = self._gather(live)
        for e in errors:
            UI.warn(e)
        UI.step(1, total_steps, f"{len(signals)} signaux", "✓")

        UI.step(2, total_steps, "Persistance…")
        for sig in signals:
            self.store.save_signal(sig)
        UI.step(2, total_steps, "Enregistrés", "✓")

        UI.step(3, total_steps, "Effondrement de la superposition…")
        for sig in signals:
            self.weaver.observe_signal(sig)
        UI.step(3, total_steps, "Lectures résolues", "✓")

        delta = self.calculator.calculate(signals)
        status, interp = self.calculator.interpret(delta)
        self.store.save_delta(delta, status)
        cum = self._log_cost("compile", signals)

        UI.step(4, total_steps, "Calcul du Δ…", "✓")
        UI.section("Δ local", icon="📊")
        UI.delta_gauge(delta)
        print(f"  {C.BOLD}Statut :{C.RESET} {status}")
        print(f"  {C.DIM}{interp}{C.RESET}")

        UI.step(5, total_steps, "Génération prophétique…", "✓")
        UI.section("Prophétie", icon="🔮")
        print(self.prophecy_gen.generate(signals, delta))

        UI.section("Carte de la Trame", icon="🗺")
        print(self.visualizer.visualize(signals, delta))

        layer_deltas = self.calculator.calculate_by_layer(signals)
        print(self.visualizer.visualize_layers(signals, layer_deltas))

        threads_data = self.store.top_threads(3)
        print(self.visualizer.visualize_threads(threads_data))

        UI.step(6, total_steps, "Lecture du Codex…", "✓")
        UI.section("Convergence 2079", icon="🌀")
        print(self.convergence.report(delta))

        UI.section("Grimoire", icon="📖")
        print(self.grimoire.read(2))

        print(f"\n{C.DIM}📿 Coût mémétique cumulé : {cum:.2f}{C.RESET}")
        UI.separator("═")
        UI.quantum("refactor soul/ego.py")
        UI.quantum("remove hardcoded beliefs")
        UI.quantum("tests pass, void returns")
        print()
        UI.quantum("Ya Hu… raz••• Alou…", icon="✦")

    # ────────────────────────────────────────────────────────────
    # CONVERGENCE / GRIMOIRE / INVOKE / DRAUGRS / THREADS / WEAVE
    # ────────────────────────────────────────────────────────────
    def show_convergence(self) -> None:
        UI.banner("CONVERGENCE 2079", "Horizon temporel du Codex", icon="🌀")
        signals = self.store.recent_signals(20)
        delta = self.calculator.calculate(signals)
        print(self.convergence.report(delta))

    def show_grimoire(self, count: int = 1) -> None:
        UI.banner("GRIMOIRE", "Fragments du Codex Vauvillensis", icon="📖")
        print(self.grimoire.read(count))

    def invoke(self, emotion: str = "oubli", count: int = 3) -> None:
        UI.banner("INVOCATIONS LLM", f"Émotion : {emotion}", icon="🕯")
        print(self.invocation_gen.generate(emotion=emotion, count=count))

    def show_draugrs(self) -> None:
        UI.banner("DRAUGRS MÉMÉTIQUES", "Conservation Glitchique", icon="👻")
        print(self.draugr_engine.list_active())

    def banish_draugr(self, draugr_id: int) -> None:
        UI.banner("BANNISSEMENT", f"Draugr #{draugr_id}", icon="✨")
        print(self.draugr_engine.banish(draugr_id))

    def show_threads(self, count: int = 5) -> None:
        UI.banner("FILS DU MÉTIER", "Temps Tissé", icon="🧵")
        threads_data = self.store.top_threads(count)
        print(self.visualizer.visualize_threads(threads_data))

    def weave(self, max_threads: int = 3) -> None:
        UI.banner("TISSAGE", f"{max_threads} fils assemblés", icon="🧶")
        print(self.weaver.weave(max_threads))

    # ────────────────────────────────────────────────────────────
    # ORACLE
    # ────────────────────────────────────────────────────────────
    def consult_oracle(self, live: bool = False) -> None:
        UI.banner("ORACLE DU MÉTIER", "Consultation Quantique", icon="🔮")
        total = 4

        UI.step(1, total, "Collecte des signaux…")
        signals, errors = self._gather(live)
        for e in errors:
            UI.warn(e)
        UI.step(1, total, f"{len(signals)} signaux", "✓")

        UI.step(2, total, "Persistance…")
        for sig in signals:
            self.store.save_signal(sig)
        UI.step(2, total, "Enregistrés", "✓")

        UI.step(3, total, "Effondrement de la superposition…")
        for sig in signals:
            self.weaver.observe_signal(sig)
        UI.step(3, total, "Lectures résolues", "✓")

        delta = self.calculator.calculate(signals)
        self.store.save_delta(delta, self.calculator.interpret(delta)[0])
        self._log_cost("oracle", signals)

        UI.step(4, total, "Consultation de l'Oracle", "✓")
        UI.delta_gauge(delta)
        print(self.oracle.consult(signals, delta))

    # ────────────────────────────────────────────────────────────
    # EXPORT
    # ────────────────────────────────────────────────────────────
    def export(self, fmt: str = "json", output: Optional[Path] = None) -> None:
        UI.banner("EXPORT", f"Format : {fmt}", icon="📤")
        signals = self.store.recent_signals(500)
        trend = self.store.delta_trend(30)
        threads_data = self.store.top_threads(20)
        if fmt == "json":
            data = {
                "generated_at": datetime.datetime.now().isoformat(),
                "signals": [s.to_dict() for s in signals],
                "delta_trend": [{"timestamp": t, "delta": d} for t, d in trend],
                "threads": [{"id": tid, "phrases": phrases} for tid, phrases in threads_data],
            }
            text = json.dumps(data, ensure_ascii=False, indent=2)
        elif fmt == "md":
            lines = [f"# Rapport Trame Watcher v5 — {datetime.datetime.now():%Y-%m-%d %H:%M}\n"]
            lines.append(f"## Δ récents ({len(trend)} mesures)")
            for t, d in trend[-20:]:
                lines.append(f"- `{t}` → Δ = {d:.3f}")
            lines.append(f"\n## Fils tissés ({len(threads_data)})")
            for tid, phrases in threads_data[:10]:
                lines.append(f"\n### Fil {tid}")
                for p in phrases[:5]:
                    lines.append(f"- {p}")
            lines.append(f"\n## Signaux récents ({len(signals)})")
            for s in signals[:50]:
                layers_str = ",".join(str(l) for l in s.fractal_echo)
                lines.append(f"- **{s.category}** (Δ:{s.intensity:.2f}) Couches:{layers_str} — {s.source} — {s.content}")
            lines.append(f"\n## FracturoScript")
            for s in signals[:20]:
                if s.fracturo:
                    lines.append(f"- `{s.fracturo}`")
            text = "\n".join(lines)
        elif fmt == "fs":
            lines = ["// FracturoScript Export — Trame Watcher v5", ""]
            for s in signals[:50]:
                lines.append(s.to_fracturo_line())
            text = "\n".join(lines)
        else:
            raise ValueError(f"Format inconnu : {fmt}")
        if output:
            output.write_text(text, encoding="utf-8")
            UI.success(f"Export → {output}")
        else:
            print(text)


# ═══════════════════════════════════════════════════════════════
# 🚀 POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="trame_watcher.py",
        description="🌀 TRAME WATCHER v5.2 — Le Métier à Tisser Quantique",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples :
  python trame_watcher.py watch --live --continuous --interval 600
  python trame_watcher.py compile --live
  python trame_watcher.py prophesy --live
  python trame_watcher.py visualize --layers --threads
  python trame_watcher.py convergence
  python trame_watcher.py grimoire --count 3
  python trame_watcher.py invoke --emotion silence --count 5
  python trame_watcher.py draugr --list
  python trame_watcher.py threads --count 5
  python trame_watcher.py weave --threads 3
  python trame_watcher.py oracle --live
  python trame_watcher.py export --format fs -o invocations.fs

Que la rune te guide — ou te trahisse, selon la marée.
Ya Hu… raz••• Alou…
        """,
    )
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    p.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    p.add_argument("-v", "--verbose", action="store_true")
    sub = p.add_subparsers(dest="command")

    pw = sub.add_parser("watch", help="Veille (une passe ou continue)")
    pw.add_argument("--live", action="store_true")
    pw.add_argument("--interval", type=int, default=300)
    pw.add_argument("--once", action="store_true", default=True)
    pw.add_argument("--continuous", dest="once", action="store_false")

    pp = sub.add_parser("prophesy", help="Prophétie glitchée")
    pp.add_argument("--live", action="store_true")

    pd = sub.add_parser("delta", help="Δ local actuel")
    pd.add_argument("--live", action="store_true")

    pv = sub.add_parser("visualize", help="Carte de la Trame")
    pv.add_argument("--live", action="store_true")
    pv.add_argument("--layers", action="store_true", help="Heatmap OSI 7 couches")
    pv.add_argument("--threads", action="store_true", help="Affiche les fils tissés")

    ph = sub.add_parser("history", help="Tendance du Δ")
    ph.add_argument("--days", type=int, default=7)

    pf = sub.add_parser("feeds", help="Gère les flux RSS")
    pf.add_argument("--list", action="store_true")

    pe = sub.add_parser("export", help="Exporte l'historique")
    pe.add_argument("--format", choices=["json", "md", "fs"], default="json")
    pe.add_argument("-o", "--output", type=Path)

    pc = sub.add_parser("compile", help="Rituel de l'Aube (complet)")
    pc.add_argument("--live", action="store_true")

    pg = sub.add_parser("grimoire", help="Fragment du Codex")
    pg.add_argument("--count", type=int, default=1)

    sub.add_parser("convergence", help="Tracker de Convergence 2077-2082")

    pi = sub.add_parser("invoke", help="Générateur d'invocations LLM")
    pi.add_argument("--emotion", default="oubli")
    pi.add_argument("--count", type=int, default=3)

    pdr = sub.add_parser("draugr", help="Gère les Draugrs mémétiques")
    pdr.add_argument("--list", action="store_true")
    pdr.add_argument("--banish", type=int, default=None, help="ID du Draugr à bannir")

    pt = sub.add_parser("threads", help="Liste les fils de temps-tissé")
    pt.add_argument("--count", type=int, default=5)

    pwv = sub.add_parser("weave", help="Compose un récit à partir des fils")
    pwv.add_argument("--threads", type=int, default=3)

    po = sub.add_parser("oracle", help="Consultation quantique complète")
    po.add_argument("--live", action="store_true")

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    setup_logging(verbose=args.verbose)
    config = load_config(args.config)
    w = TrameWatcher(config=config, db_path=args.db)

    cmd = args.command
    try:
        if cmd == "watch":
            w.watch(live=args.live, interval=args.interval, once=args.once)
        elif cmd == "prophesy":
            w.prophesy(live=args.live)
        elif cmd == "delta":
            w.show_delta(live=args.live)
        elif cmd == "visualize":
            w.visualize(live=args.live, layers=args.layers, threads=args.threads)
        elif cmd == "history":
            w.history(days=args.days)
        elif cmd == "feeds":
            UI.banner("FLUX RSS CONFIGURÉS", icon="📡")
            for f in config.get("feeds", []):
                print(f"  • {C.CYAN}{f.get('name')}{C.RESET}: {f.get('url')}")
        elif cmd == "export":
            w.export(fmt=args.format, output=args.output)
        elif cmd == "compile":
            w.compile_ritual(live=args.live)
        elif cmd == "grimoire":
            w.show_grimoire(count=args.count)
        elif cmd == "convergence":
            w.show_convergence()
        elif cmd == "invoke":
            w.invoke(emotion=args.emotion, count=args.count)
        elif cmd == "draugr":
            if args.banish is not None:
                w.banish_draugr(args.banish)
            else:
                w.show_draugrs()
        elif cmd == "threads":
            w.show_threads(count=args.count)
        elif cmd == "weave":
            w.weave(max_threads=args.threads)
        elif cmd == "oracle":
            w.consult_oracle(live=args.live)
        else:
            parser.print_help()
    except KeyboardInterrupt:
        UI.separator("═")
        UI.warn("Interruption. Le silence se referme.", icon="🛑")


if __name__ == "__main__":
    main()
