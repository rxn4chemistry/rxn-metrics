import logging
from pathlib import Path
from typing import Optional

import click
from rxn.chemutils.miscellaneous import canonicalize_file
from rxn.chemutils.tokenization import copy_as_detokenized
from rxn.onmt_models import rxn_translation
from rxn.utilities.files import ensure_directory_exists_and_is_empty
from rxn.utilities.logging import setup_console_and_file_logger

from rxn.metrics.class_tokens import maybe_prepare_class_token_files
from rxn.metrics.classification_translation import maybe_classify_predictions
from rxn.metrics.metrics_files import RetroFiles
from rxn.metrics.run_metrics import evaluate_metrics
from rxn.metrics.true_reactant_accuracy import (
    maybe_determine_true_reactants,
    true_reactant_environment_check,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


@click.command(context_settings={"show_default": True})
@click.option(
    "--precursors_file",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="File containing the precursors of a test set",
)
@click.option(
    "--products_file",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="File containing the products of a test set",
)
@click.option(
    "--output_dir",
    required=True,
    type=click.Path(path_type=Path),
    help="Where to save all the files",
)
@click.option(
    "--retro_model",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to the single-step retrosynthesis model",
)
@click.option(
    "--forward_model",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to the forward model",
)
@click.option(
    "--classification_model",
    type=click.Path(exists=True, path_type=Path),
    required=False,
    default=None,
    help="Path to the classification model",
)
@click.option("--batch_size", default=64, type=int, help="Batch size")
@click.option(
    "--n_best", default=10, type=int, help="Number of retro predictions to make (top-N)"
)
@click.option(
    "--gpu/--no-gpu", default=False, help="Whether to run the predictions on a GPU."
)
@click.option(
    "--no_metrics", is_flag=True, help="If given, the metrics will not be computed."
)
@click.option(
    "--beam_size", default=15, type=int, help="Beam size for retro (> n_best)."
)
@click.option(
    "--class_tokens",
    default=None,
    type=int,
    help="The number of tokens used in the trainings",
)
@click.option(
    "--with_true_reactant_accuracy/--no_true_reactant_accuracy",
    default=False,
    help="Whether to calculate the true reactant accuracy, based on rxnmapper.",
)
@click.option(
    "--rxnmapper_batch_size",
    default=8,
    type=int,
    help=(
        "Batch size for RXNMapper. Considered "
        "only if the true reactant accuracy is activated."
    ),
)
def main(
    precursors_file: Path,
    products_file: Path,
    output_dir: Path,
    retro_model: Path,
    forward_model: Path,
    classification_model: Optional[Path],
    batch_size: int,
    n_best: int,
    gpu: bool,
    no_metrics: bool,
    beam_size: int,
    class_tokens: Optional[int],
    with_true_reactant_accuracy: bool,
    rxnmapper_batch_size: int,
) -> None:
    """Starting from the ground truth files and two models (retro, forward),
    generate the translation files needed for the metrics, and calculate the default metrics.
    """
    true_reactant_environment_check(with_true_reactant_accuracy)

    ensure_directory_exists_and_is_empty(output_dir)
    retro_files = RetroFiles(output_dir)

    setup_console_and_file_logger(retro_files.log_file)

    copy_as_detokenized(products_file, retro_files.gt_src)
    copy_as_detokenized(precursors_file, retro_files.gt_tgt)

    maybe_prepare_class_token_files(class_tokens, retro_files)

    # retro
    rxn_translation(
        src_file=(
            retro_files.gt_src
            if class_tokens is None
            else retro_files.class_token_products
        ),
        tgt_file=(
            retro_files.gt_tgt
            if class_tokens is None
            else retro_files.class_token_precursors
        ),
        pred_file=retro_files.predicted,
        model=retro_model,
        n_best=n_best,
        beam_size=beam_size,
        batch_size=batch_size,
        gpu=gpu,
    )

    canonicalize_file(
        retro_files.predicted,
        retro_files.predicted_canonical,
        fallback_value="",
        sort_molecules=True,
    )

    # Forward
    rxn_translation(
        src_file=retro_files.predicted_canonical,
        tgt_file=None,
        pred_file=retro_files.predicted_products,
        model=forward_model,
        n_best=1,
        beam_size=10,
        batch_size=batch_size,
        gpu=gpu,
    )

    canonicalize_file(
        retro_files.predicted_products,
        retro_files.predicted_products_canonical,
        fallback_value="",
    )

    maybe_classify_predictions(classification_model, retro_files, batch_size, gpu)
    maybe_determine_true_reactants(
        with_true_reactant_accuracy, retro_files, rxnmapper_batch_size
    )

    if not no_metrics:
        evaluate_metrics("retro", output_dir)


if __name__ == "__main__":
    main()
