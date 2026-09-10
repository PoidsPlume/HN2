# Mémoire M2 Humanités Numériques — Notebooks d'analyse

Ce dépôt regroupe l'ensemble des notebooks utilisés pour les analyses réalisées dans le cadre du mémoire de deuxième année du Master Humanités Numériques.

Le pipeline couvre l'ensemble du traitement du corpus : extraction des articles depuis les PDF sources, constitution d'une base de données unifiée, classification thématique, extraction et normalisation des entités nommées (notamment géographiques), traitements linguistiques (NLP) et analyse statistique du corpus.

> **Note sur les données** : les textes intégraux des articles ne sont pas diffusés sur ce dépôt. Ils peuvent être fournis sur demande aux chercheurs qui souhaitent les consulter — n'hésitez pas à me contacter directement.

## Sommaire

- [Notebooks](#notebooks)
- [Compléments](#compléments)
- [Pipeline de traitement](#pipeline-de-traitement)

## Notebooks

Les notebooks sont numérotés selon l'ordre d'exécution du pipeline.

| # | Notebook | Description |
|---|----------|--------------|
| 1 | `extract_text.ipynb` | Conversion des fichiers PDF en fichiers JSON contenant les articles uniques, et préparation des différents jeux de données destinés à l'annotation. |
| 2 | `set_database.ipynb` | Attribution d'un identifiant unique à chaque article par hachage de son contenu, puis constitution d'un fichier Parquet unique regroupant l'ensemble des informations. Les articles vides ne permettant pas de générer de hash ont été écartés (2 269 articles). |
| 3 | `classify_subject.ipynb` | Entraînement et exécution du modèle de catégorisation distinguant les articles relevant de la fiction de ceux relevant du réel. |
| 4 | `NER.ipynb` | Entraînement et évaluation des différentes stratégies de reconnaissance d'entités nommées (NER) pour l'extraction des termes relatifs à la prostitution, ainsi qu'extraction des lieux via SpaCy. |
| 5 | `NER_LOC.ipynb` | Normalisation des lieux extraits à l'étape précédente. |
| 6 | `NLP.ipynb` | Lemmatisation, tokenisation, extraction des n-grammes les plus fréquents et traitements complémentaires sur les n-grammes extraits. |
| 7 | `stats.ipynb` | Statistiques descriptives sur le corpus. |

## Compléments

Fichiers de données annexes produits ou utilisés en support des notebooks ci-dessus.

- `geocodes_final.parquet` — Liste de l'ensemble des lieux extraits des articles, accompagnés de leurs coordonnées géographiques.
- `liste_sources_31_mars_2026.pdf` — Liste des sources présentes sur Europresse (extraite depuis Europresse).
- `liste_pays_sources.json` — Dictionnaire associant chaque source à son pays d'origine, incluant des enrichissements manuels.
- `corpus_metadonnées.parquet` — Fichier de métadonnées du corpus (hors textes intégraux), au format Polars. Schéma détaillé ci-dessous.

### Schéma de `corpus_metadonnées.parquet`

```python
Schema([
    ('id', String),
    ('journaux', List(String)),
    ('dates', List(String)),
    ('pays', List(String)),
    ('type', String),
    ('pays_entites', List(Struct({'pays': String, 'code_pays': String}))),
    ('entities', List(Struct({
        'ngram': String,
        'text': String,
        'start': Int64,
        'end': Int64,
        'labels': List(String),
        'feats': List(String),
        'upos': List(String),
        'start_phrase': Int64,
        'end_phrase': Int64
    })))
])
```

| Colonne | Type | Description |
|---------|------|--------------|
| `id` | `String` | Identifiant unique de l'article (hash du contenu, voir `set_database.ipynb`). |
| `journaux` | `List(String)` | Journal(aux) source(s) de l'article. |
| `dates` | `List(String)` | Date(s) de publication associée(s). |
| `pays` | `List(String)` | Pays associé(s) à la source. |
| `type` | `String` | Type d'article (résultat de la classification fiction/réalité). |
| `pays_entites` | `List(Struct)` | Entités géographiques identifiées, avec nom du pays (`pays`) et code pays (`code_pays`). |
| `entities` | `List(Struct)` | Entités nommées extraites, avec forme n-gramme normalisée (`ngram`), texte brut (`text`), positions de début/fin (`start`, `end`), étiquettes (`labels`), traits morphologiques (`feats`), catégories grammaticales universelles (`upos`) et positions de la phrase contenant l'entité (`start_phrase`, `end_phrase`). |

> Ce fichier constitue le point d'accès principal aux résultats du pipeline (classification, NER, géolocalisation) sans nécessiter l'accès aux textes bruts.

## Pipeline de traitement

```
extract_text.ipynb
        │
        ▼
set_database.ipynb
        │
        ▼
classify_subject.ipynb
        │
        ▼
     NER.ipynb
        │
        ▼
  NER_LOC.ipynb
        │
        ▼
     NLP.ipynb
        │
        ▼
    stats.ipynb
```

Les fichiers `geocodes_final.parquet`, `liste_sources_31_mars_2026.pdf` et `liste_pays_sources.json` interviennent en support des étapes de géolocalisation (`NER_LOC.ipynb`) et de contextualisation des sources. Le fichier `corpus_metadonnées.parquet` regroupe les métadonnées et résultats consolidés de l'ensemble du pipeline.

## Accès aux données

Pour des raisons de droits liés aux sources de presse, les textes intégraux des articles ne sont pas hébergés sur ce dépôt. Seules les métadonnées et les résultats dérivés (entités, catégorisation, géocodage) sont partagés publiquement. Les chercheurs souhaitant accéder aux textes complets du corpus peuvent en faire la demande directement auprès de moi.
