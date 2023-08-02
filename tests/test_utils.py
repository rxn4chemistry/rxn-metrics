import pytest
from rxn.utilities.files import dump_list_to_file, named_temporary_directory

from rxn.metrics.utils import (
    combine_precursors_and_products_from_files,
    get_sequence_multiplier,
)


def test_combine_precursors_and_products_from_files() -> None:
    # Make sure that things are combined properly with the precursors file
    # containing twice as many lines as the products file.
    with named_temporary_directory() as tmp_dir:
        precursors_file = tmp_dir / "a"
        products_file = tmp_dir / "b"

        dump_list_to_file(
            ["CC.O", "CC.O.[Na+]~[Cl-]", "CCC.O", "NS.CCC.O"],
            precursors_file,
        )
        dump_list_to_file(["CCO", "CCCO"], products_file)

        results = combine_precursors_and_products_from_files(
            precursors_file, products_file
        )
        assert list(results) == [
            "CC.O>>CCO",
            "CC.O.[Na+]~[Cl-]>>CCO",
            "CCC.O>>CCCO",
            "NS.CCC.O>>CCCO",
        ]


def test_get_sequence_multiplier() -> None:
    assert get_sequence_multiplier([1, 2, 3], [1, 2, 3]) == 1
    assert get_sequence_multiplier([1, 2, 3], [1, 1, 2, 2, 3, 3]) == 2
    assert (
        get_sequence_multiplier(
            ["a", "b", "c"], ["a", "aa", "aaa", "b", "bb", "bbb", "c", "cc", "ccc"]
        )
        == 3
    )

    # raises if not an exact multiple
    with pytest.raises(ValueError):
        _ = get_sequence_multiplier([1, 2], [1, 2, 3])
    with pytest.raises(ValueError):
        _ = get_sequence_multiplier([1, 2, 3], [1, 2])

    # raises if one of the lists is empty
    with pytest.raises(ValueError):
        _ = get_sequence_multiplier([], [1, 2, 3])
    with pytest.raises(ValueError):
        _ = get_sequence_multiplier([1, 2, 3], [])
