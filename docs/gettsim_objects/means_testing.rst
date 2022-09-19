.. _means_testing:

Assets considered for means testing
===================================

| The table below gives an overview of all tangible and intangible assets which are considered when performing means for several transfers. A cross indicates that the asset class is not considered and, hence, deducted from the overall assets of a household.

| This documentation shall help to understand the composition of the :ref:`basic input variable <input_variables>` 'vermögen_bedürft_hh'. Despite small differences over the transfers, we decided, for now, to require only one wealth variable as input and use it for all transfers.

.. note::
   | ALGII = Grundsicherung für Arbeitslose
   | GSA/E = Grundsicherung im Alter/ bei Erwerbsminderung
   | WoGe = Wohngeld
   | KiZu = Kinderzuschlag

   HC = hardship case
   (Asset class is not considered if it would constitute a particular hardship for that person, see § 90 Abs.3 SGBXII `<https://www.gesetze-im-internet.de/sgb_12/__90.html>`_)

+-----------------------------------------------+---------+---------+---------+---------+
| Not counted as assets                         |  ALGII  |  GSA/E  |  WoGe   |  KiZu   |
+===============================================+=========+=========+=========+=========+
| Appropriate household goods                   |    x    |    x    |    x    |    x    |
+-----------------------------------------------+---------+---------+---------+---------+
|| Adequate motor vehicle for each              ||   x    || x (HC) ||   x    ||   x    |
|| person capable of working                    ||        ||        ||        ||        |
+-----------------------------------------------+---------+---------+---------+---------+
|| Assets for retirement provision and          ||   x    ||   x    ||   x    ||   x    |
|| retirement assets                            ||        ||        ||        ||        |
+-----------------------------------------------+---------+---------+---------+---------+
|| Owner-occupied house/apartment of            ||   x    ||   x    ||   x    ||   x    |
|| appropriate size                             ||        ||        ||        ||        |
+-----------------------------------------------+---------+---------+---------+---------+
|| Assets for obtaining/maintaining a house     ||   x    ||   x    ||   x    ||   x    |
|| property for people in need of care          ||        ||        ||        ||        |
+-----------------------------------------------+---------+---------+---------+---------+
|| Assets to build up/secure a livelihood       ||   x    ||   x    ||   x    ||   x    |
|| or establishment of a household              ||        ||        ||        ||        |
+-----------------------------------------------+---------+---------+---------+---------+
| Family and heirloom pieces                    | x (HC)  |    x    |         | x (HC)  |
+-----------------------------------------------+---------+---------+---------+---------+
|| Property and rights, if realization would    ||   x    ||   x    ||        ||   x    |
|| be uneconomical or a particular hardship     ||        ||        ||        ||        |
+-----------------------------------------------+---------+---------+---------+---------+
|| Items to start/continue vocational           ||   x    ||   x    ||   x    ||   x    |
|| training/employment                          ||        ||        ||        ||        |
+-----------------------------------------------+---------+---------+---------+---------+
| Items for the satisfaction of spiritual needs ||        ||   x    ||   x    ||        |
+-----------------------------------------------+---------+---------+---------+---------+

.. seealso::
    See the following links for legal bases for the definition of assets for each transfer.
     * ALGII: §12 SGBII `<https://www.gesetze-im-internet.de/sgb_2/__12.html>`_
     * GSA/E: §90 SGBXII `<https://www.gesetze-im-internet.de/sgb_12/__90.html>`_
     * WoGe: §21 WoGG `<https://www.gesetze-im-internet.de/bkgg_1996/__6a.html>`_
     * KiZu: §6a BKGG, Abs.3 `<https://www.gesetze-im-internet.de/bkgg_1996/__6a.html>`_
