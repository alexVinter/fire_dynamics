"""
Нечёткий поиск по справочнику техники (Модуль 5).
Сравнение запроса с name и search_keywords через rapidfuzz.
"""

from rapidfuzz import fuzz
from rapidfuzz import process as rf_process

from core.models import Modification


def find_best_match(input_query: str):
    """
    Найти лучшее совпадение по запросу среди модификаций (TechDirectory-уровень).

    Сравнивает input_query с отображаемым именем и с search_keywords.
    Берётся лучший score по каждому полю.

    Returns:
        - int (id модификации), если лучший score > 85;
        - list из до 3 элементов {"id": int, "name": str, "score": int},
          если лучший score от 50 до 85 (включительно);
        - None, если лучший score < 50.
    """
    if not (input_query and input_query.strip()):
        return None

    query = input_query.strip()
    mods = list(
        Modification.objects.all().select_related("model", "model__brand")
    )
    if not mods:
        return None

    # Пары (строка для сравнения, modification)
    name_choices = [(str(m), m) for m in mods]
    kw_choices = [(m.search_keywords or "", m) for m in mods]

    # Лучший по name (встроенный fuzz.ratio совместим с rapidfuzz.process)
    names_only = [c[0] for c in name_choices]
    best_name = rf_process.extractOne(query, names_only, scorer=fuzz.ratio)
    if best_name:
        score_name, idx_name = best_name[1], best_name[2]
        mod_by_name = name_choices[idx_name][1]
    else:
        score_name, mod_by_name = 0, None

    # Лучший по search_keywords
    kws_only = [c[0] for c in kw_choices]
    best_kw = rf_process.extractOne(query, kws_only, scorer=fuzz.ratio) if any(kws_only) else None
    if best_kw:
        score_kw, idx_kw = best_kw[1], best_kw[2]
        mod_by_kw = kw_choices[idx_kw][1]
    else:
        score_kw, mod_by_kw = 0, None

    # Итоговый лучший score и модификация
    if score_name >= score_kw and mod_by_name:
        best_mod, best_score = mod_by_name, score_name
    elif mod_by_kw:
        best_mod, best_score = mod_by_kw, score_kw
    else:
        return None

    if best_score > 85:
        return best_mod.id

    if 50 <= best_score <= 85:
        # Собрать топ-3 по тому же полю (name или keywords), затем по другому
        combined = []
        seen_ids = set()
        for choice_list, get_mod in [
            (name_choices, lambda c: c[1]),
            (kw_choices, lambda c: c[1]),
        ]:
            extracted = rf_process.extract(query, [c[0] for c in choice_list], scorer=fuzz.ratio, limit=3)
            for choice_str, score, idx in extracted:
                mod = get_mod(choice_list[idx])
                if mod.id not in seen_ids and score >= 50:
                    seen_ids.add(mod.id)
                    combined.append((score, mod))
        combined.sort(key=lambda x: -x[0])
        top3 = combined[:3]
        return [{"id": m.id, "name": str(m), "score": s} for s, m in top3]

    return None
