Data types in the Tax and Transfer System
=========================================

GETTSIM uses pandas Series throughout and has his own type hints, which describe the
data type of each Series. They are used for their internal functions and entforced
on all input data. You can find the type hints in the documentation of
:ref:`functions` and of all basic input data in :ref:`variables`. The description of
the current types can be found in the table below.

If you want to contribute functions to GETTSIM, you are entforced to use
these types as typehints. If you use the GETTSIM interface to provide some own policies
or alter existing ones, only the data output of your functions is checked.


+----------------+-------------------------------------------+------------------+
| Internal type  | Description                               | dtype of Series  |
+================+===========================================+==================+
| FloatSeries    | Floats or ints. Missings allowed          | float, int       |
+----------------+-------------------------------------------+------------------+
| IntSeries      | Only integers. No missings allowed.       | int              |
+----------------+-------------------------------------------+------------------+
| BoolSeries     | True or False vales. No missings allowed. | bool             |
+----------------+-------------------------------------------+------------------+
| DateTimeSeries | Datetime values. No missings allowed      | numpy.datetime64 |
+----------------+-------------------------------------------+------------------+
