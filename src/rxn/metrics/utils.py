from typing import Iterator, Sequence, TypeVar

from rxn.utilities.files import PathLike, iterate_lines_from_file
from rxn.utilities.misc import get_multiplier

T = TypeVar("T")


def combine_precursors_and_products(
    precursors: Iterator[str], products: Iterator[str]
) -> Iterator[str]:
    """
    Combine two matching iterables of precursors/products into an iterator of reaction SMILES.

    Args:
        precursors: iterable of sets of precursors.
        products: iterable of sets of products.

    Returns:
        iterator over reaction SMILES.
    """

    yield from (
        f"{precursor_set}>>{product_set}"
        for precursor_set, product_set in zip(precursors, products)
    )


def combine_precursors_and_products_from_files(
    precursors_file: PathLike, products_file: PathLike
) -> Iterator[str]:
    """
    Combine the precursors file and the products file into an iterator of reaction SMILES.

    Args:
        precursors_file: file containing the sets of precursors.
        products_file: file containing the sets of products.

    Returns:
        iterator over reaction SMILES.
    """

    yield from combine_precursors_and_products(
        precursors=iterate_lines_from_file(precursors_file),
        products=iterate_lines_from_file(products_file),
    )


def get_sequence_multiplier(ground_truth: Sequence[T], predictions: Sequence[T]) -> int:
    """
    Get the multiplier for the number of predictions by ground truth sample.

    Raises:
        ValueError: if the lists have inadequate sizes (possibly forwarded
            from get_multiplier).
    """
    n_gt = len(ground_truth)
    n_pred = len(predictions)

    return get_multiplier(n_gt, n_pred)
