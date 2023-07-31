from rxn.metrics.true_reactant_accuracy import (
    get_standardized_true_reactants,
    true_reactant_accuracy,
)


def test_get_standardized_true_reactants() -> None:
    input_expected_pairs = [
        ("[CH3:9]O.O.N>>CON", ["CO"]),
        ("O[CH3:9].O.N>>CON", ["CO"]),  # same, non-canonical
        ("[CH3:9]O.[OH2:7].N>>CON", ["CO", "O"]),  # two true reactants
        ("[OH2:7].[CH3:9]O.N>>CON", ["CO", "O"]),  # same, ordered differently
        ("[CH3:9]FC.O>>CO", ["CFC"]),  # invalid valence is admitted
    ]

    for rxn_smiles, expected in input_expected_pairs:
        assert get_standardized_true_reactants(rxn_smiles) == expected

    # Cases considered as errors, and returning None
    # 1) No reactant with atom mapping
    assert get_standardized_true_reactants("CC.O>>CCO") is None
    # 2) Not a reaction SMILES
    assert get_standardized_true_reactants("[CH4:9].O") is None
    # 3) Invalid component SMILES
    assert get_standardized_true_reactants("[CH3:9]C[Ik].O>>CO") is None


def test_true_reactant_accuracy() -> None:
    # To simplify the tests below: a few lists of reaction pairs.
    # a, b, c are "reactant-compatible reactions", while x, y, z aren't
    a = [  # different maps
        "[CH3:7][CH2:5]O.N.[CH4:9]>>CON",
        "[CH3:3][CH2:2]O.N.[CH4:1]>>CON",
    ]
    b = [  # different other reactants, different order, non-canonical
        "[CH3:7][CH2:5]O.N.[CH4:9]>>CON",
        "S.O.[CH4:1].O[CH2:3][CH3:2].>>CON",
    ]
    c = [  # other mapped atoms mapped on the same reactants
        "[CH3:7][CH2:5]O.N.[CH4:9]>>CON",
        "S.OO.CC[OH:8].[CH4:6]>>CON",
    ]
    x = [  # additional mapped compound in gt
        "[CH3:7][CH2:5]O.N.[CH4:9].[OH2:1]>>CON",
        "[CH3:3][CH2:2]O.N.[CH4:1]>>CON",
    ]
    y = [  # additional mapped compound in pred
        "[CH3:7][CH2:5]O.N.[CH4:9]>>CON",
        "[CH3:3][CH2:2]O.N.[CH4:1].[OH2:1]>>CON",
    ]
    z = [  # prediction has no maps
        "[CH3:7][CH2:5]O.N.[CH4:9]>>CON",
        "[CH3][CH2]O.N.[CH4]>>CON",
    ]

    # a few examples for top-1
    assert true_reactant_accuracy(
        [a[0], b[0], c[0]],
        [a[1], b[1], c[1]],
    ) == {1: 1.0}
    assert true_reactant_accuracy(
        [x[0], y[0], z[0]],
        [x[1], y[1], z[1]],
    ) == {1: 0.0}
    assert true_reactant_accuracy(
        [a[0], y[0], c[0]],
        [a[1], y[1], c[1]],
    ) == {1: 2 / 3}
