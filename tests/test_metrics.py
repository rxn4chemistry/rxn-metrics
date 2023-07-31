import numpy as np
import pytest

from rxn.metrics.metrics import (
    class_diversity,
    coverage,
    round_trip_accuracy,
    top_n_accuracy,
)


def test_top_n_accuracy() -> None:
    # a few examples for top-1
    assert top_n_accuracy(
        ["A", "B", "C"],
        ["A", "B", "C"],
    ) == {1: 1.0}
    assert top_n_accuracy(
        ["A", "B", "C"],
        ["A", "0", "C"],
    ) == {1: 2 / 3}

    # a few examples for top-2
    assert top_n_accuracy(
        ["A", "B", "C"],
        ["A", "0", "B", "0", "C", "0"],
    ) == {1: 1.0, 2: 1.0}
    assert top_n_accuracy(
        ["A", "B", "C"],
        ["0", "A", "B", "0", "C", "0"],
    ) == {1: 2 / 3, 2: 1.0}
    assert top_n_accuracy(
        ["A", "B", "C"],
        ["0", "1", "0", "B", "C", "0"],
    ) == {1: 1 / 3, 2: 2 / 3}

    # raises if not an exact multiple
    with pytest.raises(ValueError):
        _ = top_n_accuracy([1, 2], [1, 2, 3])


def test_round_trip_accuracy() -> None:
    # a few examples for top-1
    assert round_trip_accuracy(
        ["A", "B", "C"],
        ["A", "B", "C"],
    ) == (
        {1: 1.0},
        {1: 0.0},  # std
    )
    assert round_trip_accuracy(
        ["A", "B", "C"],
        ["A", "0", "C"],
    ) == (
        {1: 2 / 3},
        {1: float(np.std([1.0, 0.0, 1.0]))},  # std
    )

    # a few examples for top-2
    assert round_trip_accuracy(
        ["A", "B", "C"],
        ["A", "A", "B", "B", "C", "0"],
    ) == (
        {
            1: 1.0,
            2: 5 / 6,
        },
        {1: float(np.std([1.0, 1.0, 1.0])), 2: float(np.std([1.0, 1.0, 0.5]))},
    )
    assert round_trip_accuracy(
        ["A", "B", "C"],
        ["A", "0", "B", "0", "C", "0"],
    ) == (
        {
            1: 1.0,
            2: 0.5,
        },
        {1: float(np.std([1.0, 1.0, 1.0])), 2: float(np.std([0.5, 0.5, 0.5]))},
    )
    assert round_trip_accuracy(
        ["A", "B", "C"],
        ["0", "A", "0", "B", "0", "C"],
    ) == (
        {
            1: 0.0,
            2: 0.5,
        },
        {1: float(np.std([0.0, 0.0, 0.0])), 2: float(np.std([0.5, 0.5, 0.5]))},
    )
    assert round_trip_accuracy(
        ["A", "B", "C"],
        ["0", "1", "0", "B", "C", "0"],
    ) == (
        {
            1: 1 / 3,
            2: 1 / 3,
        },
        {1: float(np.std([0.0, 0.0, 1.0])), 2: float(np.std([0.0, 0.5, 0.5]))},
    )

    # raises if not an exact multiple
    with pytest.raises(ValueError):
        _ = round_trip_accuracy([1, 2], [1, 2, 3])


def test_class_diversity() -> None:
    # a few examples for top-1
    assert class_diversity(
        ["A", "B", "C"], ["A", "B", "C"], ["1.1.1", "2.2.2", "3.3.3"]
    ) == (
        {1: 1.0},
        {1: 0.0},  # std
    )
    assert class_diversity(
        ["A", "B", "C"], ["A", "0", "C"], ["1.1.1", "2.2.2", "3.3.3"]
    ) == (
        {1: 2 / 3},
        {1: float(np.std([1.0, 0.0, 1.0]))},  # std
    )

    # a few examples for top-2
    assert class_diversity(
        ["A", "B", "C"],
        ["A", "A", "B", "B", "C", "0"],
        ["1.1.1", "1.1.1", "2.2.2", "1.1.1", "3.3.3", "2.2.2"],
    ) == (
        {
            1: 1.0,
            2: 4 / 3,
        },
        {1: float(np.std([1.0, 1.0, 1.0])), 2: float(np.std([1.0, 2.0, 1.0]))},
    )
    assert class_diversity(
        ["A", "B", "C"],
        ["A", "0", "B", "0", "C", "0"],
        ["1.1.1", "1.1.1", "2.2.2", "1.1.1", "3.3.3", "2.2.2"],
    ) == (
        {
            1: 1.0,
            2: 1.0,
        },
        {1: float(np.std([1.0, 1.0, 1.0])), 2: float(np.std([1.0, 1.0, 1.0]))},
    )
    assert class_diversity(
        ["A", "B", "C"],
        ["0", "A", "0", "B", "0", "C"],
        ["1.1.1", "1.1.1", "2.2.2", "1.1.1", "3.3.3", "2.2.2"],
    ) == (
        {
            1: 0.0,
            2: 1.0,
        },
        {1: float(np.std([0.0, 0.0, 0.0])), 2: float(np.std([1.0, 1.0, 1.0]))},
    )
    assert class_diversity(
        ["A", "B", "C"],
        ["0", "1", "0", "B", "C", "0"],
        ["1.1.1", "1.1.1", "2.2.2", "1.1.1", "3.3.3", "2.2.2"],
    ) == (
        {
            1: 1 / 3,
            2: 2 / 3,
        },
        {1: float(np.std([0.0, 0.0, 1.0])), 2: float(np.std([0.0, 1.0, 1.0]))},
    )

    # An example with invalid classes
    assert class_diversity(
        ["A", "B", "C"],
        ["0", "1", "0", "B", "C", "0"],
        ["1.1.1", "1.1.1", "2.2.2", "1.1.1", "", "2.2.2"],
    ) == (
        {
            1: 0 / 3,
            2: 1 / 3,
        },
        {1: float(np.std([0.0, 0.0, 0.0])), 2: float(np.std([0.0, 1.0, 0.0]))},
    )

    # raises if not an exact multiple
    with pytest.raises(ValueError):
        _ = class_diversity(["A", "B"], ["A", "B", "C"], ["1.1.1", "1.1.1", "2.2.2"])


def test_coverage() -> None:
    # a few examples for top-1
    assert coverage(
        ["A", "B", "C"],
        ["A", "B", "C"],
    ) == {1: 1.0}
    assert coverage(
        ["A", "B", "C"],
        ["A", "0", "C"],
    ) == {1: 2 / 3}

    # a few examples for top-2
    assert coverage(
        ["A", "B", "C"],
        ["A", "0", "B", "0", "C", "0"],
    ) == {1: 1.0, 2: 1.0}
    assert coverage(
        ["A", "B", "C"],
        ["0", "A", "B", "0", "C", "0"],
    ) == {1: 2 / 3, 2: 1.0}
    assert coverage(
        ["A", "B", "C"],
        ["0", "1", "0", "B", "C", "0"],
    ) == {1: 1 / 3, 2: 2 / 3}

    # raises if not an exact multiple
    with pytest.raises(ValueError):
        _ = coverage([1, 2], [1, 2, 3])
