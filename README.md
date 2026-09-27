# 🌀 Trame Watcher v5.2 — Le Métier à Tisser Quantique

> *Feng-Shui Edition*

Un outil en ligne de commande, écrit en Python, qui transforme des flux d'actualité (RSS) en une mythologie générative : détection de « signaux faibles », calcul d'un indice de dissonance (Δ), tissage narratif, prophéties, oracle, et tout un lore original (factions, lieux sacrés, paléo-mèmes, lexique runique).

C'est à la fois :
- un **scanner de signaux** qui analyse du texte (flux RSS ou simulation) à la recherche de motifs (glitch, répétition, anomalie, prophétie) ;
- un **moteur narratif** qui interprète ces signaux à travers un univers fictionnel (factions, lieux sacrés de Normandie, entités, paléo-mèmes) et les tisse en fils narratifs persistants ;
- une **interface CLI stylisée** (« Feng-Shui ») avec bannières, jauges et couleurs.

---

## ✨ Fonctionnalités

- **Détection de signaux faibles** dans du texte, par catégorie (`glitch`, `répétition`, `anomalie`, `prophétie`), à partir de listes de mots-clés configurables.
- **Ingestion RSS/Atom** en direct (`--live`) ou **simulation** de signaux hors-ligne.
- **Classification en 7 couches OSI mythologiques** (Matière → Intention), inspirées du modèle réseau mais détournées en strates ontologiques.
- **Superposition quantique** : chaque signal génère plusieurs lectures possibles (faction / lieu / paléo-mème / couche) avant qu'une seule ne soit « observée ».
- **FracturoScript** : un traducteur texte → glyphes runiques avec calcul d'intensité et de niveau de risque (`SÛR` → `Ω - CRITIQUE`).
- **Paléo-mèmes** : bibliothèque de biais cognitifs/archétypes déclenchés par des mots associés.
- **Indice Δ (delta)** de dissonance ontologique, calculé à partir de l'historique des signaux, avec interprétation (`SILENCE STRUCTURÉ` → `Ω - CRITIQUE`) et alertes contextuelles.
- **Fils tissés (threads)** : les lectures de signaux successifs sont regroupées en fils narratifs persistants en base.
- **Draugrs mémétiques** : entités générées automatiquement en cas de forte dissonance, gérables (liste / bannissement).
- **Générateurs de contenu** : prophéties, invocations LLM, fragments de grimoire, rapports de convergence (compte à rebours vers le 21/06/2079).
- **Visualisations texte** : carte de la Trame, heatmap des 7 couches, sparklines, fils tissés.
- **Persistance SQLite** : tous les signaux, fils et l'historique Δ sont stockés localement.
- **Export** des données au format `json`, `md` (rapport Markdown) ou `fs` (FracturoScript).
- **Rendu enrichi optionnel** via [`rich`](https://github.com/Textualize/rich) (fallback ANSI si absent).

---

## 📦 Installation

Python 3.9+ requis (usage de `from __future__ import annotations` et de types génériques).

```bash
git clone https://github.com/Syrinx-2112/Trame-Watcher
cd Trame-Watcher
```

Aucune dépendance externe n'est strictement nécessaire (tout repose sur la bibliothèque standard). L'affichage enrichi est optionnel :

```bash
pip install rich
```

---

## 🚀 Utilisation

```bash
python trame_watcher.py <commande> [options]
```

Options globales :

| Option | Description |
|---|---|
| `--config PATH` | Fichier de config JSON (défaut : `~/.trame_watcher/config.json`) |
| `--db PATH` | Fichier SQLite (défaut : `~/.trame_watcher/trame_v5.db`) |
| `-v`, `--verbose` | Logs détaillés dans la console (en plus du fichier log) |

### Commandes disponibles

| Commande | Description | Options clés |
|---|---|---|
| `watch` | Veille : une passe ou boucle continue | `--live`, `--continuous`, `--interval N` |
| `prophesy` | Génère une prophétie glitchée | `--live` |
| `delta` | Affiche le Δ (indice de dissonance) actuel | `--live` |
| `visualize` | Carte de la Trame (texte) | `--live`, `--layers`, `--threads` |
| `history` | Tendance du Δ sur N jours | `--days N` |
| `feeds` | Liste les flux RSS configurés | `--list` |
| `export` | Exporte l'historique | `--format json\|md\|fs`, `-o FICHIER` |
| `compile` | « Rituel de l'Aube » : passe complète (scan + calculs + rapport) | `--live` |
| `grimoire` | Affiche un ou plusieurs fragments du Codex | `--count N` |
| `convergence` | Rapport du Tracker de Convergence 2077–2082 | — |
| `invoke` | Génère des invocations orientées LLM | `--emotion X`, `--count N` |
| `draugr` | Gère les Draugrs mémétiques actifs | `--list`, `--banish ID` |
| `threads` | Liste les fils de temps-tissé | `--count N` |
| `weave` | Compose un récit à partir des fils existants | `--threads N` |
| `oracle` | Consultation quantique complète | `--live` |

### Exemples

```bash
# Veille continue, scan des flux RSS toutes les 10 minutes
python trame_watcher.py watch --live --continuous --interval 600

# Rituel complet en direct
python trame_watcher.py compile --live

# Visualiser la heatmap des 7 couches + les fils tissés
python trame_watcher.py visualize --layers --threads

# Suivre la convergence vers l'événement Ω
python trame_watcher.py convergence

# Piocher 3 fragments du grimoire
python trame_watcher.py grimoire --count 3

# Exporter les 50 derniers signaux en FracturoScript
python trame_watcher.py export --format fs -o invocations.fs
```

---

## ⚙️ Configuration

Au premier lancement, une configuration par défaut est utilisée (mots-clés de signaux faibles, runes par catégorie, mots-clés OSI, flux RSS par défaut, fragments prophétiques). Elle peut être surchargée via un fichier JSON (`--config`), fusionné clé par clé avec les valeurs par défaut. Paramètres notables :

```json
{
  "base_delta": 0.35,
  "signal_weight": 0.15,
  "feeds": [
    { "name": "mon_flux", "url": "https://exemple.org/rss.xml" }
  ]
}
```

- `base_delta` : valeur de dissonance de base en l'absence de signaux.
- `signal_weight` : poids de chaque signal détecté dans le calcul du Δ.
- `weak_signals` : dictionnaire `catégorie → mots-clés` déclenchant la détection.
- `feeds` : liste des flux RSS/Atom interrogés en mode `--live`.

---

## 🗃️ Données & persistance

Toutes les données sont stockées localement dans une base SQLite (`~/.trame_watcher/trame_v5.db` par défaut), avec trois tables :

- `signals` — chaque signal détecté (contenu, intensité, catégorie, runes, lectures en superposition, lecture observée, glyphe FracturoScript…).
- `threads` — les fils narratifs tissés à partir des lectures de signaux successifs.
- `delta_history` — l'historique de l'indice Δ et du statut associé, pour la commande `history`.

Les logs sont écrits dans `~/.trame_watcher/trame_watcher.log`.

---

## 🧩 Architecture du code

Le script est organisé en modules numérotés au sein d'un seul fichier :

0. **Interface Feng-Shui** (`UI`, `C`) — bannières, étapes, jauges Δ, couleurs ANSI.
1. **Lexique FracturoScript** (`FracturoTranslator`) — traduction texte → glyphes runiques + score de risque.
2. **Paléo-mèmes** (`PaleoMemeAnalyzer`) — détection d'archétypes/biais cognitifs dans un texte.
3. **Superposition quantique** (`SignalDetector`) — détection des signaux, classification en couches OSI, génération des lectures possibles, ingestion RSS/Atom.
4. **Persistance** (`TrameStore`) — accès SQLite (signaux, fils, historique Δ, draugrs, journal de coût).
5. **Delta** (`DeltaCalculator`) — calcul et interprétation de l'indice de dissonance.
6. **Temps tissé** (`ThreadWeaver`) — regroupement des lectures en fils narratifs.
7. **Draugrs** (`DraugrEngine`), **Prophéties** (`ProphecyGenerator`), **Invocations** (`InvocationGenerator`), **Grimoire** (`GrimoireReader`), **Oracle** (`OracleGenerator`), **Convergence** (`ConvergenceTracker`), **Visualisation** (`TrameVisualizer`) — générateurs de contenu et rapports.
8. **`TrameWatcher`** — classe façade qui orchestre tous les modules pour chaque sous-commande CLI.

Un helper `safe_name()` (et ses variantes `safe_paleo_name` / `safe_place_name`) uniformise l'accès aux structures, qu'il s'agisse de dictionnaires (`FACTIONS`, `SACRED_PLACES`) ou de dataclasses (`PALEO_MEMES`).

---

## 📜 Univers

Le lore s'articule autour de lieux réels de Normandie (La Hague, Caen, Raz Blanchard…) réinterprétés comme des points sacrés, de factions fictives (Hackervölvas, Enfants de la Panne, Prophètes du Vide…), et d'une date de convergence fixée au **21 juin 2079, 03:33:33**. Tout contenu généré (prophéties, invocations, fragments de grimoire) est fictionnel et généré procéduralement à partir des tables de configuration du script.

---

## 📄 Licence

*(à compléter selon vos préférences — MIT, CC-BY-NC, tous droits réservés, etc.)*
