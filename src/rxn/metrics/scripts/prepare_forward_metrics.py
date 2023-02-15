from pathlib import Path

import click

from rxn.metrics.run_metrics import evaluate_metrics, run_model_for_metrics


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
    "--forward_model",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to the forward model",
)
@click.option("--batch_size", default=64, type=int, help="Batch size")
@click.option(
    "--n_best", default=5, type=int, help="Number of retro predictions to make (top-N)"
)
@click.option("--gpu", is_flag=True, help="If given, run the predictions on a GPU.")
@click.option(
    "--no_metrics", is_flag=True, help="If given, the metrics will not be computed."
)
def main(
    precursors_file: Path,
    products_file: Path,
    output_dir: Path,
    forward_model: Path,
    batch_size: int,
    n_best: int,
    gpu: bool,
    no_metrics: bool,
) -> None:
    """Starting from the ground truth files and forward model, generate the
    translation files needed for the metrics, and calculate the default metrics."""

    run_model_for_metrics(
        task="forward",
        model_path=forward_model,
        src_file=precursors_file,
        tgt_file=products_file,
        output_dir=output_dir,
        n_best=n_best,
        beam_size=10,
        batch_size=batch_size,
        gpu=gpu,
        initialize_logger=True,
    )

    if not no_metrics:
        evaluate_metrics("forward", output_dir)


if __name__ == "__main__":
    main()
