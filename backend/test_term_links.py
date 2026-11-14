import term_links as TL
from foodrugs_full import norm


def test_synonym_groups_are_normalized_and_disjoint():
    for kind, groups in TL.SYNONYMS.items():
        seen = set()
        for g in groups:
            assert all(t == norm(t) for t in g), g
            assert not seen & set(g), f'termo em dois grupos: {seen & set(g)}'
            seen |= set(g)


def test_links_are_normalized_and_inference_is_capped():
    for table in (TL.CLASSES, TL.COMPONENTS):
        for key, values in table.items():
            assert key == norm(key) and all(v == norm(v) for v in values)
    assert TL.LEVEL_CAP == 1
