from rxn.metrics.utils import get_sequence_multiplier


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
