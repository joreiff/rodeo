# Copyright 2022 Johannes Reiff
# SPDX-License-Identifier: Apache-2.0

import numpy as np
import numpy.typing as npt


__all__ = [
    'dofs',
    'time',
    'position',
    'momentum',
    'states',
    'grid',
]


def dofs(qpt: np.ndarray, /) -> int:
    """Return the number of degrees of freedom for states *qpt*."""

    return len(qpt) // 2


class _Time(type):
    def __getitem__(self, qpt: np.ndarray) -> np.ndarray | float | None:
        return qpt[-1] if len(qpt) % 2 == 1 else None

    def __setitem__(self, qpt: np.ndarray, value: npt.ArrayLike):
        if len(qpt) % 2 == 0:
            raise ValueError('The passed state array does not have a time column.')
        qpt[-1] = value

time = _Time('time', (), {})
time.__doc__ = """
Access the time :math:`t` for each state in *qpt*.

This function object uses the subscript operator to support assignment::

    t = rodeo.time[qpt] # read
    rodeo.time[qpt] = t # write
"""


class _Position(type):
    def __getitem__(self, qpt: np.ndarray) -> np.ndarray:
        return qpt[: dofs(qpt)]

    def __setitem__(self, qpt: np.ndarray, value: npt.ArrayLike):
        qpt[: dofs(qpt)] = value

position = _Position('position', (), {})
position.__doc__ = """
Access the position :math:`\\vec{q}` for each state in *qpt*.

This function object uses the subscript operator to support assignment::

    q = rodeo.position[qpt] # read
    rodeo.position[qpt] = q # write
"""


class _Momentum(type):
    def __getitem__(self, qpt: np.ndarray) -> np.ndarray:
        n = dofs(qpt)
        return qpt[n : 2 * n]

    def __setitem__(self, qpt: np.ndarray, value: npt.ArrayLike):
        n = dofs(qpt)
        qpt[n : 2 * n] = value

momentum = _Momentum('momentum', (), {})
momentum.__doc__ = """
Access the momentum :math:`\\vec{p}` for each state in *qpt*.

This function object uses the subscript operator to support assignment::

    p = rodeo.momentum[qpt] # read
    rodeo.momentum[qpt] = p # write
"""


def states(
    q: npt.ArrayLike,
    p: npt.ArrayLike = 0.0,
    t: npt.ArrayLike | None = None,
) -> np.ndarray:

    """Build a state from positions *q*, momenta *p*, and optional time *t*."""

    qp = np.broadcast_arrays(q, p)

    if t is not None:
        t = np.broadcast_to(t, qp[0].shape[1:])
        if qp[0].shape:
            t = t.reshape((1,) + t.shape)
        qp.append(t)

    return np.concatenate(qp)


def grid(*ranges: npt.ArrayLike) -> np.ndarray:
    """Return a list of coordinates on a grid defined by multiple 1D vectors."""

    return np.stack(list(map(np.ravel, np.meshgrid(*ranges, indexing='ij'))))
