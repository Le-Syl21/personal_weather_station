"""Turn a positional list of translations into a named phrase book.

Authoring 63 languages is a lot of repetition; this accepts the translations in
the order build_translations.py prints them and writes the readable, keyed file
contributors are meant to edit.
"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from build_translations import PHRASEBOOKS, STRINGS, flatten, phrase_list

UI_KEYS = [
    "::".join(path)
    for path, _ in flatten(json.loads(STRINGS.read_text(encoding="utf-8")))
    if path[0] != "entity"
]


def seed(language, entities, ui, quality="seeded"):
    """Write scripts/phrasebooks/<language>.json from ordered translations."""

    phrases = phrase_list()

    assert len(entities) == len(phrases), (
        f"{language}: {len(entities)} phrases pour {len(phrases)} attendues"
    )
    assert len(ui) == len(UI_KEYS), (
        f"{language}: {len(ui)} chaînes UI pour {len(UI_KEYS)} attendues"
    )

    book = {
        "quality": quality,
        "entities": dict(zip(phrases, entities)),
        "ui": dict(zip(UI_KEYS, ui)),
    }

    for key, value in {**book["entities"], **book["ui"]}.items():
        assert str(value).strip(), f"{language}: traduction vide pour {key!r}"

    PHRASEBOOKS.mkdir(parents=True, exist_ok=True)
    (PHRASEBOOKS / f"{language}.json").write_text(
        json.dumps(book, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    return language


def seed_from(base, language, entity_overrides=None, ui_overrides=None, quality="seeded"):
    """
    Derive a phrase book from another one.

    Regional variants differ by a handful of words, so restating a hundred
    identical phrases would only invite them to drift apart.
    """

    source = json.loads((PHRASEBOOKS / f"{base}.json").read_text(encoding="utf-8"))

    entities = dict(source["entities"])
    entities.update(entity_overrides or {})

    ui = dict(source["ui"])
    ui.update(ui_overrides or {})

    for key in (entity_overrides or {}):
        assert key in source["entities"], f"{language}: phrase inconnue {key!r}"
    for key in (ui_overrides or {}):
        assert key in source["ui"], f"{language}: clé UI inconnue {key!r}"

    return seed(
        language,
        [entities[phrase] for phrase in phrase_list()],
        [ui[key] for key in UI_KEYS],
        quality,
    )
