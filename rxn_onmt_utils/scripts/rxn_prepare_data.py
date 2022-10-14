#!/usr/bin/env python
# LICENSED INTERNAL CODE. PROPERTY OF IBM.
# IBM Research Zurich Licensed Internal Code
# (C) Copyright IBM Corp. 2020
# ALL RIGHTS RESERVED
import logging
from pathlib import Path

import click
from rxn.reaction_preprocessing.config import (
    CommonConfig,
    Config,
    DataConfig,
    FragmentBond,
    InitialDataFormat,
    RxnImportConfig,
    SplitConfig,
    StandardizeConfig,
)
from rxn.reaction_preprocessing.main import preprocess_data
from rxn.utilities.logging import setup_console_logger

from rxn_onmt_utils import __version__
from rxn_onmt_utils.rxn_models import defaults
from rxn_onmt_utils.rxn_models.utils import RxnPreprocessingFiles

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


@click.command(context_settings=dict(show_default=True))
@click.option("--input_data", type=str, required=True, help="Input data TXT")
@click.option(
    "--output_dir",
    type=str,
    required=True,
    help="Directory where to save the generated files",
)
@click.option(
    "--split_seed", default=defaults.SEED, help="Random seed for splitting step"
)
@click.option(
    "--fragment_bond",
    type=click.Choice(["DOT", "TILDE"], case_sensitive=False),
    default="DOT",
)
def main(input_data: str, output_dir: str, split_seed: int, fragment_bond: str) -> None:
    """Preprocess the data to generate a dataset for training transformer models.

    The script will automatically generate the following files in output_dir:
        data.imported.csv
        data.standardized.csv
        data.processed.csv
        data.processed.train.csv
        data.processed.validation.csv
        data.processed.test.csv
        data.processed.train.precursors_tokens
        data.processed.train.products_tokens
        data.processed.validation.precursors_tokens
        data.processed.validation.products_tokens
        data.processed.test.precursors_tokens
        data.processed.test.products_tokens
    """
    setup_console_logger()
    logger.info(
        f"Prepare reaction data for training with rxn-onmt-utils, version {__version__}."
    )

    # Running the command below fails if the paths are relative -> make them absolute
    input_data_path = Path(input_data).resolve()
    output_dir_path = Path(output_dir).resolve()

    # make sure that the required output directory exists
    output_dir_path.mkdir(parents=True, exist_ok=True)

    # NB: if the format is CSV, use the following below:
    #   rxn_import.data_format=CSV
    #   rxn_import.input_csv_column_name=rxn_smiles_xxx

    cfg = Config(
        data=DataConfig(
            path=str(input_data_path),
            proc_dir=str(output_dir_path),
            name=RxnPreprocessingFiles.FILENAME_ROOT,
        ),
        common=CommonConfig(fragment_bond=FragmentBond[fragment_bond]),
        rxn_import=RxnImportConfig(data_format=InitialDataFormat.TXT),
        standardize=StandardizeConfig(
            annotation_file_paths=[], discard_unannotated_metals=False
        ),
        split=SplitConfig(hash_seed=split_seed),
    )

    try:
        logger.info("Running the data preprocessing")
        preprocess_data(cfg)
    except Exception as e:
        logger.exception("Error during data preprocessing:")
        raise SystemExit("Error during data preprocessing") from e


if __name__ == "__main__":
    main()
