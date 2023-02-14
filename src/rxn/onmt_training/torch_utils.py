# LICENSED INTERNAL CODE. PROPERTY OF IBM.
# IBM Research Zurich Licensed Internal Code
# (C) Copyright IBM Corp. 2021
# ALL RIGHTS RESERVED


def set_num_threads(n: int) -> None:
    """
    Set the number of threads to be used by torch.

    torch is imported within the function, and the function lives in its own
    file, because of errors occurring on the cluster in some cases if this
    was not the case.
    """
    import torch

    torch.set_num_threads(n)
