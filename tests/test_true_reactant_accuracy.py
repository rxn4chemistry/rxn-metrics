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
        "[CH3:7][CH2:5]O.N.C[CH3:9]>>CON",
        "[CH3:3][CH2:2]O.N.C[CH3:1]>>CON",
    ]
    b = [  # different other reactants, different order, non-canonical
        "[CH3:7][CH2:5]O.N.N[CH3:9]>>CON",
        "S.O.[CH3:1]N.O[CH2:3][CH3:2].>>CON",
    ]
    c = [  # other mapped atoms mapped on the same reactants
        "[CH3:7][CH2:5]O.N.O[CH3:9]>>CON",
        "S.OO.CC[OH:8].O[CH3:6]>>CON",
    ]
    x = [  # additional mapped compound in gt
        "[CH3:7][CH2:5]O.N.S[CH3:9].[OH2:1]>>CON",
        "[CH3:3][CH2:2]O.N.S[CH3:1]>>CON",
    ]
    y = [  # additional mapped compound in pred
        "[CH3:7][CH2:5]O.N.P[CH3:9]>>CON",
        "[CH3:3][CH2:2]O.N.P[CH3:1].[OH2:1]>>CON",
    ]
    z = [  # prediction has no maps
        "[CH3:7][CH2:5]O.N.F[CH3:9]>>CON",
        "[CH3][CH2]O.N.F[CH3]>>CON",
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

    # a few examples for top-2
    # 1) correct predictions given first
    assert true_reactant_accuracy(
        [a[0], b[0], c[0]],
        [a[1], x[1], b[1], y[1], c[1], z[1]],
    ) == {1: 1.0, 2: 1.0}
    # 2) correct prediction given first two times, and second one time
    assert true_reactant_accuracy(
        [a[0], b[0], c[0]],
        [a[1], x[1], y[1], b[1], c[1], z[1]],
    ) == {1: 2 / 3, 2: 1.0}
    # 1) correct prediction given first one time, and second one time
    assert true_reactant_accuracy(
        [a[0], b[0], c[0]],
        [x[1], a[1], x[1], z[1], c[1], z[1]],
    ) == {1: 1 / 3, 2: 2 / 3}

    # If problem in the ground truth: count as incorrect! Here: no mapping
    assert true_reactant_accuracy(
        ["CC.O>>CCO"],
        ["CC.O>>CCO"],
    ) == {1: 0.0}
