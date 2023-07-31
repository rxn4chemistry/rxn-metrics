import importlib.util
import logging

from rxn.utilities.files import dump_list_to_file

from .metrics_files import RetroFiles
from .utils import combine_precursors_and_products_from_files

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
