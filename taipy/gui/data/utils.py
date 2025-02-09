# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from __future__ import annotations

import typing as t
from abc import ABC, abstractmethod

import numpy as np

from .._warnings import _warn

if t.TYPE_CHECKING:
    import pandas as pd


class Decimator(ABC):
    """Base class for decimating chart data.

    *Decimating* is the term used to name the process of reducing the number of
    data points displayed in charts while retaining the overall shape of the traces.
    `Decimator` is a base class that does decimation on data sets.

    Taipy GUI comes out-of-the-box with several implementation of this class for
    different use cases.
    """

    _CHART_MODES: t.List[str] = []

    def __init__(self, threshold: t.Optional[int], zoom: t.Optional[bool]) -> None:
        """Initialize a new `Decimator`.

        Arguments:
            threshold (Optional[int]): The minimum amount of data points before the
                decimator class is applied.
            zoom (Optional[bool]): set to True to reapply the decimation
                when zoom or re-layout events are triggered.
        """
        super().__init__()
        self.threshold = threshold
        self._zoom = zoom if zoom is not None else True

    def _is_applicable(self, data: t.Any, nb_rows_max: int, chart_mode: str):
        if chart_mode not in self._CHART_MODES:
            _warn(f"{type(self).__name__} is only applicable for {' '.join(self._CHART_MODES)}.")
            return False
        return (
            self.threshold is None
            and nb_rows_max < len(data)
            or self.threshold is not None
            and self.threshold < len(data)
        )

    @abstractmethod
    def decimate(self, data: np.ndarray, payload: t.Dict[str, t.Any]) -> np.ndarray:
        """Decimate function.

        This method is executed when the appropriate conditions specified in the
        constructor are met. This function implements the algorithm that determines
        which data points are kept or dropped.

        Arguments:
            data (numpy.array): An array containing all the data points represented as
                tuples.
            payload (Dict[str, any]): additional information on charts that is provided
                at runtime.

        Returns:
            An array of Boolean mask values. The array should set True or False for each
                of its indexes where True indicates that the corresponding data point
                from *data* should be preserved, or False requires that this
                data point be dropped.
        """
        return NotImplementedError  # type: ignore


def _df_data_filter(
    dataframe: pd.DataFrame,
    x_column_name: t.Optional[str],
    y_column_name: str,
    z_column_name: str,
    decimator: Decimator,
    payload: t.Dict[str, t.Any],
    is_copied: bool,
):
    df = dataframe.copy() if not is_copied else dataframe
    if not x_column_name:
        index = 0
        while f"tAiPy_index_{index}" in df.columns:
            index += 1
        x_column_name = f"tAiPy_index_{index}"
        df[x_column_name] = df.index
    column_list = [x_column_name, y_column_name, z_column_name] if z_column_name else [x_column_name, y_column_name]
    points = df[column_list].to_numpy()
    mask = decimator.decimate(points, payload)
    return df[mask], is_copied


def _df_relayout(
    dataframe: pd.DataFrame,
    x_column: t.Optional[str],
    y_column: str,
    chart_mode: str,
    x0: t.Optional[float],
    x1: t.Optional[float],
    y0: t.Optional[float],
    y1: t.Optional[float],
    is_copied: bool,
):
    if chart_mode not in ["lines+markers", "markers"]:
        return dataframe, is_copied
    # if chart data is invalid
    if x0 is None or x1 is None or y0 is None or y1 is None:
        return dataframe, is_copied
    df = dataframe.copy() if not is_copied else dataframe
    is_copied = True
    has_x_col = True

    if not x_column:
        index = 0
        while f"tAiPy_index_{index}" in df.columns:
            index += 1
        x_column = f"tAiPy_index_{index}"
        df[x_column] = df.index
        has_x_col = False

    # if chart_mode is empty
    if chart_mode == "lines+markers":
        # only filter by x column
        df = df.loc[(df[x_column] > x0) & (df[x_column] < x1)]
    else:
        # filter by both x and y columns
        df = df.loc[(df[x_column] > x0) & (df[x_column] < x1) & (df[y_column] > y0) & (df[y_column] < y1)]  # noqa
    if not has_x_col:
        df.drop(x_column, axis=1, inplace=True)
    return df, is_copied
