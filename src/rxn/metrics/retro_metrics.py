import os
from typing import Any, Dict, Iterable, Optional

from rxn.utilities.files import PathLike, iterate_lines_from_file

from .metrics import class_diversity, coverage, round_trip_accuracy, top_n_accuracy
from .metrics_calculator import MetricsCalculator
from .metrics_files import MetricsFiles, RetroFiles


class RetroMetrics(MetricsCalculator):
    """
    Class to compute common metrics for retro models, starting from files
    containing the ground truth and predictions.

    Note: all files are expected to be standardized (canonicalized, sorted, etc.).
    """

    def __init__(
        self,
        gt_precursors: Iterable[str],
        gt_products: Iterable[str],
        predicted_precursors: Iterable[str],
        predicted_products: Iterable[str],
        predicted_classes: Optional[Iterable[str]] = None,
    ):
        self.gt_products = list(gt_products)
        self.gt_precursors = list(gt_precursors)
        self.predicted_products = list(predicted_products)
        self.predicted_precursors = list(predicted_precursors)
        self.predicted_classes = (
            list(predicted_classes) if predicted_classes is not None else None
        )

    def get_metrics(self) -> Dict[str, Any]:
        topn = top_n_accuracy(
            ground_truth=self.gt_precursors, predictions=self.predicted_precursors
        )
        roundtrip, roundtrip_std = round_trip_accuracy(
            ground_truth=self.gt_products, predictions=self.predicted_products
        )
        cov = coverage(
            ground_truth=self.gt_products, predictions=self.predicted_products
        )
        if self.predicted_classes:
            classdiversity, classdiversity_std = class_diversity(
                ground_truth=self.gt_products,
                predictions=self.predicted_products,
                predicted_classes=self.predicted_classes,
            )
        else:
            classdiversity, classdiversity_std = {}, {}

        return {
            "accuracy": topn,
            "round-trip": roundtrip,
            "round-trip-std": roundtrip_std,
            "coverage": cov,
            "class-diversity": classdiversity,
            "class-diversity-std": classdiversity_std,
        }

    @classmethod
    def from_metrics_files(cls, metrics_files: MetricsFiles) -> "RetroMetrics":
        if not isinstance(metrics_files, RetroFiles):
            raise ValueError("Invalid type provided")

        # Whether to use the reordered files - for class token
        # To determine whether True or False, we check if the reordered files exist
        reordered = RetroFiles.reordered(metrics_files.predicted_canonical).exists()

        return cls.from_raw_files(
            gt_precursors_file=metrics_files.gt_tgt,
            gt_products_file=metrics_files.gt_src,
            predicted_precursors_file=(
                metrics_files.predicted_canonical
                if not reordered
                else RetroFiles.reordered(metrics_files.predicted_canonical)
            ),
            predicted_products_file=(
                metrics_files.predicted_products_canonical
                if not reordered
                else RetroFiles.reordered(metrics_files.predicted_products_canonical)
            ),
            predicted_classes_file=(
                None
                if not os.path.exists(metrics_files.predicted_classes)
                else metrics_files.predicted_classes
                if not reordered
                else RetroFiles.reordered(metrics_files.predicted_classes)
            ),
        )

    @classmethod
    def from_raw_files(
        cls,
        gt_precursors_file: PathLike,
        gt_products_file: PathLike,
        predicted_precursors_file: PathLike,
        predicted_products_file: PathLike,
        predicted_classes_file: Optional[PathLike] = None,
    ) -> "RetroMetrics":
        return cls(
            gt_precursors=iterate_lines_from_file(gt_precursors_file),
            gt_products=iterate_lines_from_file(gt_products_file),
            predicted_precursors=iterate_lines_from_file(predicted_precursors_file),
            predicted_products=iterate_lines_from_file(predicted_products_file),
            predicted_classes=None
            if predicted_classes_file is None
            else iterate_lines_from_file(predicted_classes_file),
        )
