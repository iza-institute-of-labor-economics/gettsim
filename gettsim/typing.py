from typing import NewType

import pandas as pd

Series = NewType("Series", pd.Series)

FloatSeries = Series(float)
IntSeries = Series(int)
BoolSeries = Series(bool)
CatSeries = Series(int)
