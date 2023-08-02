from typing import Iterator, Sequence, TypeVar

from rxn.chemutils.reaction_combiner import ReactionCombiner
from rxn.chemutils.reaction_smiles import ReactionFormat
from rxn.utilities.files import PathLike, count_lines, iterate_lines_from_file
from rxn.utilities.misc import get_multiplier, get_multipliers

T = TypeVar("T")


def combine_precursors_and_products(
    precursors: Iterator[str],
    products: Iterator[str],
    total_precursors: int,
    total_products: int,
) -> Iterator[str]:
    """
    Combine two matching iterables of precursors/products into an iterator of reaction SMILES.

    Args:
        precursors: iterable of sets of precursors.
        products: iterable of sets of products.
        total_precursors: total number of precursors.
        total_products: total number of products.

    Returns:
        iterator over reaction SMILES.
    """
    combiner = ReactionCombiner(reaction_format=ReactionFormat.STANDARD_WITH_TILDE)

    precursor_multiplier, product_multiplier = get_multipliers(
        total_precursors, total_products
    )

    yield from combiner.combine_iterators(
        precursors, products, precursor_multiplier, product_multiplier
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
    n_precursors = count_lines(precursors_file)
    n_products = count_lines(products_file)

    yield from combine_precursors_and_products(
        precursors=iterate_lines_from_file(precursors_file),
        products=iterate_lines_from_file(products_file),
        total_precursors=n_precursors,
        total_products=n_products,
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
