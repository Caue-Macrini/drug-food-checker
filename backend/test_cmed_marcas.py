import cmed_marcas as M


def test_core_removes_salts_and_hydrates():
    assert M.core('CLORIDRATO DE METFORMINA') == 'metformina'
    assert M.core('LOSARTANA POTÁSSICA') == 'losartana'
    assert M.core('CLORIDRATO  DE ONDANSETRONA DI-HIDRATADO') == 'ondansetrona'
    assert M.core('HEMITARTARATO DE ZOLPIDEM') == 'zolpidem'


def test_candidates_include_english_name():
    assert M.candidates('VARFARINA SÓDICA')[0] == 'warfarin'
    assert 'atorvastatin' in M.candidates('ATORVASTATINA CÁLCICA')
    assert 'amoxicillin' in M.candidates('AMOXICILINA TRI-HIDRATADA')
    assert 'denosumab' in M.candidates('DENOSUMABE')
    assert M.candidates('ÁCIDO VALPRÓICO')[0] == 'valproic acid'


def test_pick_accepts_only_existing_terms():
    entity = {'warfarin': (1, 10), 'sertraline': (2, 5)}
    norm = lambda s: s.lower()
    assert M.pick('VARFARINA SÓDICA', entity, set(), norm) == ('warfarin', (1, 10))
    assert M.pick('CLORIDRATO DE SERTRALINA', entity, set(), norm) == ('sertraline', (2, 5))
    assert M.pick('EXTRATO DE PASSIFLORA', entity, set(), norm) is None
    assert M.pick('VARFARINA SÓDICA', entity, {'warfarin'}, norm) is None
