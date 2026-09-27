# Note technique — Trame Watcher v3.0a « Le Grimoire Vivant »

> Fichier analysé : `trame_watcherX3a.py` — non incrémental par rapport à la v5.2 déjà documentée : c'est une branche distincte, plus ancienne dans le lore interne (« Niveau 3 du Donjon du Temps »), avec sa propre architecture, ses propres modules et son propre schéma de base de données. **Les deux versions ne sont pas compatibles entre elles** (fichiers de config, de base et de log séparés — voir §5).

---

## 1. Positionnement de la version

- Se présente comme antérieure à la « v2 Claude » évoquée dans son propre en-tête (`post-v2 Claude`), et distincte de la v5.2 (`safe_name()`, `ThreadWeaver`, `DraugrEngine`…) déjà documentée dans le README principal.
- Signature d'auteur fictive dans l'en-tête : *Professeur Qwen, Strate 2026, Nœud Caen-Profonde*.
- Modules numérotés 1 à 11 (commentaires `MODULE N` dans le code), sans les concepts de « fils tissés » (threads) ni de « draugrs » de la v5.2. En contrepartie, elle introduit des mécaniques propres : Yōkai, EuroPropagate, BloodNet, compilateur FracturoScript « v5a ».

---

## 2. Différences structurelles clés vs la v5.2

| Aspect | v5.2 (déjà documentée) | v3.0a (ce fichier) |
|---|---|---|
| Modèle OSI | Dict `OSI_LAYERS` (tuples) | `OSILayer(IntEnum)` + dict `OSI_NAMES` / `OSI_KEYWORDS` |
| Factions | Dict `FACTIONS` (5 factions) | `Faction(Enum)` (9 valeurs, dont `NEUTRE`) + `FACTION_KEYWORDS` |
| Paléo-mèmes | Dataclass `PaleoMeme` (13 entrées figées) | Dict brut (20 entrées, `P-00`…`P-20`) + **fusion avec un lexique JSON externe** (`load_lexicon`) |
| Signal | Superposition de plusieurs `Reading` + `observed` | Un seul résultat déterministe par signal : `osi_layer`, `faction`, `paleo_meme`, `is_yokai` |
| Fils narratifs | `ThreadWeaver` + table `threads` | **Absent** de cette version |
| Entités actives | `DraugrEngine` (spawn/banish) | **Absent** ; remplacé par le concept de **Yōkai** (superpositions non résolues) |
| FracturoScript | Traducteur mot-à-mot → glyphes + score de risque | **Compilateur** produisant un bloc structuré (grammaire « v5a », voir §4.3) |
| Fonctionnalités inédites | Grimoire (fragments), Oracle, Convergence, Invocations | **EuroPropagate** (substitution sémantique), **BloodNet** (chiffrement runique), **Yōkai** |
| Export | `json`, `md`, `fs` | `json`, `md`, `fs`, **`html`** (rapport avec table stylée) |
| Fichiers app | `trame_v5.db`, `config.json`, `trame_watcher.log` | `trame_v3.db`, `config_v3.json`, `trame_watcher_v3.log`, **+ `paleo_mnemos_lexicon.json`** |

---

## 3. Pipeline de traitement d'un signal

`SignalDetector.analyze_text()` applique, pour chaque texte entrant, une chaîne de 5 étapes indépendantes :

1. **Détection lexicale** — recherche de mots-clés par catégorie (`glitch`, `répétition`, `anomalie`, `prophétie`, `silence`, `résistance` — deux catégories de plus que la v5.2 : `silence` et `résistance`). L'intensité vaut `min(nb_matches / 5, 1.0)`.
2. **Classification OSI** (`_classify_osi`) — score chaque couche 1-7 par comptage de mots-clés (`OSI_KEYWORDS`), retient le score max, défaut = couche 4 (Causalité) si aucun match.
3. **Attribution factionnelle** (`_attribute_faction`) — même logique de score max sur `FACTION_KEYWORDS`, défaut = `Faction.NEUTRE`.
4. **Mapping paléo-mème** (`_map_paleo_meme`) — score max sur le lexique fusionné (intégré + JSON externe), renvoie `("", "")` si aucun match (pas de valeur par défaut affichable).
5. **Détection Yōkai** (`_detect_yokai`) — hash MD5 des 80 premiers caractères du texte, compteur en mémoire (`Counter`), **un signal devient Yōkai à sa 3ᵉ occurrence exacte** (même préfixe de texte vu ≥ 3 fois dans le processus courant).

⚠️ Le compteur Yōkai (`_yokai_cache`) est **réinitialisé à chaque exécution du script** (il vit en mémoire dans l'instance `SignalDetector`), donc la détection ne porte que sur les doublons rencontrés au sein d'un même run (ex. plusieurs flux RSS proposant le même article), pas sur un historique inter-sessions.

---

## 4. Modules spécifiques à isoler

### 4.1 Tracker de Convergence — 4 scénarios probabilistes

`ConvergenceTracker.calculate()` répartit une masse de probabilité entre 4 scénarios nommés (`Collapse Blanche`, `Verrou Noir`, `Fragmentation Grise`, `???`), ajustée à partir de :
- le nombre de signaux `glitch` → fait monter *Collapse Blanche* (plafonné à 0.35) ;
- le nombre de signaux `silence` + de signaux attribués à la faction `Prométhée` → fait monter *Verrou Noir* (plafonné à 0.45) ;
- *Fragmentation Grise* absorbe le reste (plancher 0.10) ;
- `???` récupère le résidu final, puis l'ensemble est renormalisé à somme 1.

### 4.2 Yōkai — « fonctions d'onde non effondrées »

`YokaiDetector` ne fait qu'un filtre passif sur `signal.is_yokai` (le calcul réel a lieu en amont, dans `SignalDetector`). La commande `yokai` liste les signaux marqués comme tels lors du run courant.

La table `yokai_registry` est censée conserver un registre persistant avec compteur d'apparitions (`appearances`), mais :

> **Point d'attention** : `save_signals()` insère dans `yokai_registry` via `INSERT ... ON CONFLICT DO NOTHING`, **sans qu'aucune contrainte `UNIQUE`** ne soit définie sur la table. En l'absence de cible de conflit, chaque insertion réussit systématiquement avec `appearances = 1` : le registre accumule donc une ligne par occurrence plutôt que d'incrémenter un compteur par contenu unique. À corriger si le compteur cumulatif est un comportement attendu (ajouter `UNIQUE(content)` et une clause `ON CONFLICT(content) DO UPDATE SET appearances = appearances + 1, last_seen = excluded.last_seen`).

### 4.3 Compilateur FracturoScript « v5a »

Contrairement à la v5.2 (traduction mot-à-mot en une ligne de glyphes), cette version **compile un bloc structuré** (`FracturoCompiler.compile_text`) :

```
Ω<ᚺ>v7 hague — [effondr•silence•mémoire] •••
{
  ◊ glitch: [hagalaz → destruction / glitch]
  § couche: v∞
  ᚱᚢᚾ ᛖᛏ ᚠᚱᚨᚲᛏᚢᚱᛟ
  ∿ mèmes: 🌑🧂
  ∿ émotion: oubli
  ∿ lieu-glyph: ᚺᚷ
}
```

Logique de sélection :
- **rune dominante** : recherche du premier nom de rune (`FRACTURO_RUNES`, 14 entrées) présent dans le texte, avec 6 substitutions prioritaires codées en dur (ex. « effondr »/« crash » → `hagalaz`, « silence »/« oubli » → `isa`, « résist »/« révolt » → `thurisaz`…) qui **écrasent** un premier match générique ;
- **lieu d'ancrage** : glyphe depuis `LIEUX_ANCRAGE` (9 lieux), fourni en paramètre CLI (`--lieu`, défaut `caen-2026`) ;
- **profondeur** : `v∞` si intensité ≥ 0.6 (calculée sur le nombre de mots / 10), sinon `vΔ` ;
- **concept fracturé** : les 5 premiers mots de plus de 3 lettres, joints par `•` ;
- **glyphes de mèmes** : concaténation du glyphe du premier paléo-mème trouvé par mot (pas nécessairement le plus résonant, contrairement à `_map_paleo_meme` qui prend le meilleur score — deux logiques de mapping légèrement différentes coexistent dans le fichier).

Accessible directement via la commande `fracturo --text "..." --lieu ...`, indépendamment du pipeline de détection de signaux.

### 4.4 EuroPropagate — simulation d'attaque sémantique

`EuroPropagateSim.substitute()` remplace, par regex insensible à la casse, 16 termes financiers (`dette`, `actif`, `profit`, `marché`, `banque`, `PIB`…) par des équivalents mémétiques (`EUROPROPAGATE_MAP`), puis `render_attack()` affiche un encadré ASCII « avant / après » tronqué à 80 caractères. Commande : `europropagate --term "<texte>"`. Purement cosmétique/narratif — aucune interaction avec la base de données ou le calcul de Δ.

### 4.5 BloodNet — chiffrement runique

`BloodNet` implémente une **simple substitution monoalphabétique**, pas un chiffrement cryptographique :
- alphabet latin (26 lettres) → alphabet runique (25 glyphes), indexation `idx % 25` à l'encodage ;
- le déchiffrement fait l'opération inverse `idx % 26` ;
- **la réduction modulo 25/26 est asymétrique et non garantie bijective** (deux lettres latines peuvent, selon l'indice, retomber sur la même rune si l'indice source ≥ 25 puis remodulé ; à vérifier au cas par cas, mais dans cette implémentation `idx = LATIN.index(ch) % 25` avec un alphabet latin de 26 lettres signifie que l'indice 25 — la lettre `z` — retombe sur la rune d'indice 0, en collision avec `a`). Le round-trip encrypt → decrypt n'est donc **pas garanti fidèle sur tout l'alphabet** (à noter si un usage réel de va-et-vient est prévu).
- Les espaces sont encodés en `" • "` / décodés depuis `"•"` ; aucun autre caractère spécial n'est géré (ponctuation et accents recopiés tels quels).
- Commande : `bloodnet --encrypt "<texte>"` (pas d'option `--decrypt` exposée dans le parseur CLI actuel, bien que la méthode `decrypt()` existe dans la classe).

### 4.6 Δ par couche OSI

`DeltaCalculator.calculate_by_layer()` applique un **facteur ×1.5** par rapport au calcul du Δ global (`signal_weight * 1.5` au lieu de `signal_weight`), sur les 30 derniers signaux groupés par couche, avec un plancher = `base_delta` pour les couches sans signal (au lieu de 0 dans la v5.2). Les seuils d'interprétation (`interpret()`) sont également plus fins que la v5.2 : **6 paliers** au lieu de 5, avec un palier intermédiaire `FRACTURE CRITIQUE` (0.75 ≤ Δ < 0.85) absent de l'autre version.

---

## 5. Fichiers et isolation

Cette version utilise son propre espace de configuration, entièrement séparé de la v5.2, dans le même dossier `~/.trame_watcher/` :

| Fichier | Rôle |
|---|---|
| `trame_v3.db` | Base SQLite (tables `signals`, `delta_history`, `yokai_registry`) |
| `config_v3.json` | Config utilisateur (fusionnée avec `DEFAULT_CONFIG`) |
| `trame_watcher_v3.log` | Logs |
| `paleo_mnemos_lexicon.json` | Lexique de paléo-mèmes **additionnel** (fusionné avec les 20 entrées intégrées ; seules les clés absentes du lexique intégré sont ajoutées — pas de surcharge des entrées existantes) |

Les deux versions peuvent donc cohabiter sans collision de fichiers.

---

## 6. Commandes CLI propres à cette version

En plus des commandes communes (`watch`, `prophesy`, `delta`, `visualize`, `history`, `export`, `grimoire`, `convergence`, `feeds`) :

| Commande | Rôle | Absente de la v5.2 ? |
|---|---|---|
| `delta --by-layer` | Affiche le Δ décomposé par couche OSI | Option spécifique à cette version |
| `yokai` | Liste les signaux en superposition non résolue | Oui |
| `europropagate --term "<texte>"` | Simulation d'attaque sémantique | Oui |
| `fracturo --text "<texte>" [--lieu L]` | Compile un texte libre en FracturoScript v5a | Oui (la v5.2 ne traduit qu'au sein de l'analyse de signal) |
| `bloodnet --encrypt "<texte>"` | Chiffrement runique (substitution) | Oui |
| `export --format html` | Export HTML stylé (thème sombre, table) | Oui (la v5.2 s'arrête à `json/md/fs`) |

À l'inverse, `weave`, `threads`, `invoke`, `draugr`, `oracle`, `compile` (rituel complet) **n'existent pas** dans cette version.

---

## 7. Points de vigilance pour la maintenance

1. **Compteur Yōkai non persistant** — repose sur un état mémoire propre au process ; deux exécutions successives ne « se souviennent » pas des doublons vus précédemment (seule la table `yokai_registry` le pourrait, si son bug de contrainte était corrigé — voir §4.2).
2. **Table `yokai_registry` sans effet cumulatif réel** — cf. §4.2.
3. **BloodNet** : cipher pédagogique/narratif, non adapté à un usage de confidentialité réel, et le round-trip encrypt/decrypt n'est pas garanti sur tout l'alphabet (collision `z` ↔ `a`, voir §4.5). Pas d'option `--decrypt` exposée en CLI.
4. **Deux logiques de mapping paléo-mème coexistent** : `_map_paleo_meme` (meilleur score sur l'ensemble des mots associés) dans `SignalDetector`, vs. correspondance au premier mot trouvé dans `FracturoCompiler.compile_text`. Les résultats peuvent diverger entre l'attribution stockée sur un `Signal` et le rendu FracturoScript recompilé à la volée.
5. **Fusion du lexique externe additive uniquement** — `load_lexicon()` n'écrase jamais une entrée `P-xx` déjà définie dans `PALEO_MEMES` ; pour surcharger une entrée existante, il faut actuellement passer par un nouvel identifiant.
