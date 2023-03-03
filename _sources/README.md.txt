# RXN package for the calculation of metrics for OpenNMT-based models

[![Actions tests](https://github.com/rxn4chemistry/rxn-metrics/actions/workflows/tests.yaml/badge.svg)](https://github.com/rxn4chemistry/rxn-metrics/actions)

This repository contains a Python package and associated scripts for training reaction models based on the OpenNMT library.
This repository is closely related to [`rxn-onmt-models`](https://github.com/rxn4chemistry/rxn-onmt-models), which handles the training pipelines for these models.
The repository also relies on other RXN packages; see [`rxn-utilities`](https://github.com/rxn4chemistry/rxn-utilities), [`rxn-chemutils`](https://github.com/rxn4chemistry/rxn-chemutils), and [`rxn-onmt-utils`](https://github.com/rxn4chemistry/rxn-onmt-utils).

The documentation can be found [here](https://rxn4chemistry.github.io/rxn-metrics/).

This repository was produced through a collaborative project involving IBM Research Europe and Syngenta.

## System Requirements

This package is supported on all operating systems.
It has been tested on the following systems:
+ macOS: Big Sur (11.1)
+ Linux: Ubuntu 18.04.4

A Python version of 3.6, 3.7, or 3.8 is recommended.
Python versions 3.9 and above are not expected to work due to compatibility with the selected version of OpenNMT.

## Installation guide

The package can be installed from Pypi:
```bash
pip install rxn-metrics[rdkit]
```
You can leave out `[rdkit]` if RDKit is already available in your environment.

For local development, the package can be installed with:
```bash
pip install -e ".[dev,rdkit]"
```

## Calculation of metrics

The metrics are best calculated by launching one of the following scripts:
* `rxn-prepare-context-metrics`
* `rxn-prepare-forward-metrics`
* `rxn-prepare-retro-metrics`
Note that these scripts will run the models directly to limit the likelihood of making errors.

If the prediction files are available already, the script `rxn-evaluate-metrics` will compute the metrics only.

To aggregate all the metrics for different models (typically: after tuning the hyperparameters), you can run the script `rxn-parse-metrics-into-csv`.
