import pytest
from rxn.chemutils.reaction_smiles import ReactionFormat

from rxn_onmt_utils.rxn_models.reaction_combiner import ReactionCombiner


def test_reaction_combiner():
    combiner = ReactionCombiner()

    precursors = ["CC.O", "CCC.O"]
    products = ["CCO", "CCCO"]
    expected = ["CC.O>>CCO", "CCC.O>>CCCO"]

    assert list(combiner.combine(precursors, products)) == expected


def test_reaction_combiner_with_tokenized_input():
    combiner = ReactionCombiner()

    precursors = ["C C . O", "C C C . O"]
    products = ["C C O", "C C C O"]
    expected = ["CC.O>>CCO", "CCC.O>>CCCO"]

    assert list(combiner.combine(precursors, products)) == expected


def test_multiple_precursors_per_product():
    combiner = ReactionCombiner()

    # Three sets of precursors for one product
    precursors = ["CC.O", "CC.O.N", "CC.O.P", "CCC.O", "CCC.O.N", "CCC.O.P"]
    products = ["CCO", "CCCO"]
    expected = [
        "CC.O>>CCO",
        "CC.O.N>>CCO",
        "CC.O.P>>CCO",
        "CCC.O>>CCCO",
        "CCC.O.N>>CCCO",
        "CCC.O.P>>CCCO",
    ]

    assert list(combiner.combine(precursors, products)) == expected


def test_multiple_products_per_precursors():
    combiner = ReactionCombiner()

    # Two products for each set of precursors
    precursors = ["CC.O", "CCC.O"]
    products = ["CCO", "OCCO", "CCCO", "OCCCO"]
    expected = [
        "CC.O>>CCO",
        "CC.O>>OCCO",
        "CCC.O>>CCCO",
        "CCC.O>>OCCCO",
    ]

    assert list(combiner.combine(precursors, products)) == expected


def test_incompatible_number_of_precursors_and_products():
    combiner = ReactionCombiner()

    # Three precursors and two products -> unclear how to combine
    precursors = ["CC.O", "CCC.O", "CCCC.O"]
    products = ["CCO", "CCCO"]

    with pytest.raises(ValueError):
        _ = list(combiner.combine(precursors, products))


def test_different_output_formats():
    precursors = ["CC~O", "CCC~O"]
    products = ["CCO", "CCCO"]

    assert list(
        ReactionCombiner(reaction_format=ReactionFormat.STANDARD).combine(
            precursors, products
        )
    ) == ["CC.O>>CCO", "CCC.O>>CCCO"]
    assert list(
        ReactionCombiner(reaction_format=ReactionFormat.STANDARD_WITH_TILDE).combine(
            precursors, products
        )
    ) == ["CC~O>>CCO", "CCC~O>>CCCO"]
    assert list(
        ReactionCombiner(reaction_format=ReactionFormat.EXTENDED).combine(
            precursors, products
        )
    ) == ["CC.O>>CCO |f:0.1|", "CCC.O>>CCCO |f:0.1|"]


def test_standardization():
    precursors = ["C(C).O", "O.C(CC)"]
    products = ["CCO", "CCCO"]

    assert list(ReactionCombiner(standardize=True).combine(precursors, products)) == [
        "CC.O>>CCO",
        "CCC.O>>CCCO",
    ]
    assert list(ReactionCombiner(standardize=False).combine(precursors, products)) == [
        "C(C).O>>CCO",
        "O.C(CC)>>CCCO",
    ]


def test_invalid_reactions():
    invalid_string = "C>>C"
    combiner = ReactionCombiner(standardize=True, invalid_reaction=invalid_string)

    precursors = ["CC.O", "CCC.O", "CC>CC>O"]
    products = ["CCo", "CCCO", "CCCCO"]
    expected = [invalid_string, "CCC.O>>CCCO", invalid_string]

    assert list(combiner.combine(precursors, products)) == expected
