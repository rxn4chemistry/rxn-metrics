import importlib.util
import logging
from typing import Dict, List, Optional, Sequence

from rxn.chemutils.conversion import canonicalize_smiles
from rxn.chemutils.miscellaneous import smiles_has_atom_mapping
from rxn.chemutils.reaction_smiles import parse_any_reaction_smiles
from rxn.chemutils.utils import remove_atom_mapping
from rxn.utilities.containers import chunker
from rxn.utilities.files import dump_list_to_file

from .metrics_files import RetroFiles
from .utils import combine_precursors_and_products_from_files, get_sequence_multiplier

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def true_reactant_environment_check(do_reactant_check: bool) -> None:
    """Make sure that the Python packages required for the determination of true
    reactants are available (if applicable).

    Raises:
        RuntimeError: if the environment lacks a dependency.
    """
    if not do_reactant_check:
        # no reactant check to do, i.e. no packages are needed.
        return

    spec = importlib.util.find_spec("rxnmapper")
    if spec is None:
        raise RuntimeError(
            'The package "rxnmapper" is not available. Install it, or deactivate '
            "the calculation of the true reactant accuracy."
        )


def maybe_determine_true_reactants(
    do_reactant_check: bool, retro_files: RetroFiles, batch_size: int
) -> None:
    if not do_reactant_check:
        return

    # Importing only here, so that the scripts work without the rxnmapper
    # package if the true reactant accuracy is not needed.
    from rxnmapper import BatchedMapper

    logger.info(
        "The user opted in for the true reactant accuracy; "
        "the ground truth and predicted reactions will be atom-mapped."
    )

    mapper = BatchedMapper(batch_size=batch_size)

    logger.info("Atom-mapping the ground truth reactions...")
    gt_reactions = combine_precursors_and_products_from_files(
        precursors_file=retro_files.gt_tgt, products_file=retro_files.gt_src
    )
    dump_list_to_file(mapper.map_reactions(gt_reactions), retro_files.gt_mapped)
    logger.info("Atom-mapping the ground truth reactions... Done.")

    logger.info("Atom-mapping the predicted reactions...")
    predicted_reactions = combine_precursors_and_products_from_files(
        precursors_file=retro_files.predicted_canonical,
        products_file=retro_files.gt_src,
    )
    dump_list_to_file(
        mapper.map_reactions(predicted_reactions), retro_files.predicted_mapped
    )
    logger.info("Atom-mapping the predicted reactions... Done.")


def get_standardized_true_reactants(mapped_rxn_smiles: str) -> Optional[List[str]]:
    """
    Get the reactants that contribute atoms to the product, and standardize them.

    Returns:
        The sorted list of "true reactants", None if something is not right.
    """
    try:
        reactants = parse_any_reaction_smiles(mapped_rxn_smiles).reactants
        true_reactants = [r for r in reactants if smiles_has_atom_mapping(r)]
        true_reactants = [remove_atom_mapping(r) for r in true_reactants]
        canonical_true_reactants = [
            canonicalize_smiles(r, check_valence=False) for r in true_reactants
        ]
        if len(canonical_true_reactants) == 0:
            return None
        return sorted(canonical_true_reactants)
    except Exception as e:
        logger.debug(
            f'Error when determining the true reactants in "{mapped_rxn_smiles}": {e}'
        )
        return None


def true_reactant_accuracy(
    ground_truth_mapped: Sequence[str], predictions_mapped: Sequence[str]
) -> Dict[int, float]:
    """
    Compute the top-n "true reactant" accuracy values (i.e. discarding reagents).

    Args:
        ground_truth_mapped: list of atom-mapped reactions from the ground truth.
        predictions_mapped: list of atom-mapped reactions from the predictions.

    Raises:
        ValueError: if the list sizes are incompatible, forwarded from get_sequence_multiplier().

    Returns:
        Dictionary of top-n accuracy values.
    """
    multiplier = get_sequence_multiplier(
        ground_truth=ground_truth_mapped, predictions=predictions_mapped
    )

    # we will count, for each "n", how many predictions are correct
    correct_for_topn: List[int] = [0 for _ in range(multiplier)]

    # We will process sample by sample - for that, we need to chunk the predictions
    prediction_chunks = chunker(predictions_mapped, chunk_size=multiplier)

    for gt, predictions in zip(ground_truth_mapped, prediction_chunks):
        gt_true_reactants = get_standardized_true_reactants(gt)

        # if the ground truth has no mapping info: count as a negative
        if gt_true_reactants is None:
            continue

        pred_true_reactants = [get_standardized_true_reactants(p) for p in predictions]
        for i in range(multiplier):
            correct = gt_true_reactants in pred_true_reactants[: i + 1]
            correct_for_topn[i] += int(correct)

    return {
        i + 1: correct_for_topn[i] / len(ground_truth_mapped) for i in range(multiplier)
    }
