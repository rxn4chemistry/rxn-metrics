import logging
from pathlib import Path
from typing import Optional, Union

from rxn.chemutils.tokenization import file_is_tokenized, tokenize_file
from rxn.onmt_utils import translate
from rxn.utilities.files import dump_list_to_file, is_path_exists_or_creatable

from .metrics_files import RetroFiles
from .tokenize_file import (
    classification_file_is_tokenized,
    detokenize_classification_file,
    tokenize_classification_file,
)
from .utils import combine_precursors_and_products_from_files

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def maybe_classify_predictions(
    classification_model: Optional[Path],
    retro_files: RetroFiles,
    batch_size: int,
    gpu: bool,
) -> None:
    """Classify the reactions for determining the diversity metric.

    Only executed if a classification model is available."""

    if classification_model is None:
        return

    create_rxn_from_files(
        retro_files.predicted_canonical,
        retro_files.predicted_products_canonical,
        retro_files.predicted_rxn_canonical,
    )

    classification_translation(
        src_file=retro_files.predicted_rxn_canonical,
        tgt_file=None,
        pred_file=retro_files.predicted_classes,
        model=classification_model,
        n_best=1,
        beam_size=5,
        batch_size=batch_size,
        gpu=gpu,
    )


def create_rxn_from_files(
    input_file_precursors: Union[str, Path],
    input_file_products: Union[str, Path],
    output_file: Union[str, Path],
) -> None:
    logger.info(
        f'Combining files "{input_file_precursors}" and "{input_file_products}" -> "{output_file}".'
    )
    dump_list_to_file(
        combine_precursors_and_products_from_files(
            precursors_file=input_file_precursors,
            products_file=input_file_products,
        ),
        output_file,
    )


def classification_translation(
    src_file: Union[str, Path],
    tgt_file: Optional[Union[str, Path]],
    pred_file: Union[str, Path],
    model: Union[str, Path],
    n_best: int,
    beam_size: int,
    batch_size: int,
    gpu: bool,
    max_length: int = 3,
    as_external_command: bool = False,
) -> None:
    """
    Do a classification translation.

    This function takes care of tokenizing/detokenizing the input.

    Note: no check is made that the source is canonical.

    Args:
        src_file: source file (tokenized or detokenized).
        tgt_file: ground truth class file (tokenized), not mandatory.
        pred_file: file where to save the predictions.
        model: model to do the translation
        n_best: number of predictions to make for each input.
        beam_size: beam size.
        batch_size: batch size.
        gpu: whether to use the GPU.
        max_length: maximum sequence length.
    """
    if not is_path_exists_or_creatable(pred_file):
        raise RuntimeError(f'The file "{pred_file}" cannot be created.')

    # src
    if file_is_tokenized(src_file):
        tokenized_src = src_file
    else:
        tokenized_src = str(src_file) + ".tokenized"
        tokenize_file(src_file, tokenized_src, fallback_value="")

    # tgt
    if tgt_file is None:
        tokenized_tgt = None
    elif classification_file_is_tokenized(tgt_file):
        tokenized_tgt = tgt_file
    else:
        tokenized_tgt = str(tgt_file) + ".tokenized"
        tokenize_classification_file(tgt_file, tokenized_tgt)

    tokenized_pred = str(pred_file) + ".tokenized"

    translate(
        model=model,
        src=tokenized_src,
        tgt=tokenized_tgt,
        output=tokenized_pred,
        n_best=n_best,
        beam_size=beam_size,
        max_length=max_length,
        batch_size=batch_size,
        gpu=gpu,
        as_external_command=as_external_command,
    )

    detokenize_classification_file(tokenized_pred, pred_file)
