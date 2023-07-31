from typing import Optional

from rxn.utilities.files import dump_list_to_file, iterate_lines_from_file

from .metrics_files import RetroFiles


def maybe_prepare_class_token_files(
    class_tokens: Optional[int], retro_files: RetroFiles
) -> None:
    """If the model is a class-token one, create the expected src and target files.

    Args:
        class_tokens: the number of tokens used in the trainings.
        retro_files: information on the location of files for the metrics.
    """
    if class_tokens is None:
        return

    class_token_products = (
        f"{convert_class_token_idx_for_translation_models(class_token_idx)}{line}"
        for line in iterate_lines_from_file(retro_files.gt_src)
        for class_token_idx in range(class_tokens)
    )
    class_token_precursors = (
        line
        for line in iterate_lines_from_file(retro_files.gt_tgt)
        for _ in range(class_tokens)
    )
    dump_list_to_file(class_token_products, retro_files.class_token_products)
    dump_list_to_file(class_token_precursors, retro_files.class_token_precursors)


def convert_class_token_idx_for_translation_models(class_token_idx: int) -> str:
    return f"[{class_token_idx}]"
