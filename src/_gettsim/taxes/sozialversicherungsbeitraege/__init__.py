"""Social insurance contributions."""


def sozialv_beitr_arbeitnehmer_m(
    ges_pflegev_beitr_arbeitnehmer_m: float,
    ges_krankenv_beitr_arbeitnehmer_m: float,
    ges_rentenv_beitr_arbeitnehmer_m: float,
    arbeitsl_v_beitr_arbeitnehmer_m: float,
) -> float:
    """Sum of employee's social insurance contributions.

    Parameters
    ----------
    ges_pflegev_beitr_arbeitnehmer_m
        See :func:`ges_pflegev_beitr_arbeitnehmer_m`.
    ges_krankenv_beitr_arbeitnehmer_m
        See :func:`ges_krankenv_beitr_arbeitnehmer_m`.
    ges_rentenv_beitr_arbeitnehmer_m
        See :func:`ges_rentenv_beitr_arbeitnehmer_m`.
    arbeitsl_v_beitr_arbeitnehmer_m
        See :func:`arbeitsl_v_beitr_arbeitnehmer_m`.

    Returns
    -------

    """
    return (
        ges_pflegev_beitr_arbeitnehmer_m
        + ges_krankenv_beitr_arbeitnehmer_m
        + ges_rentenv_beitr_arbeitnehmer_m
        + arbeitsl_v_beitr_arbeitnehmer_m
    )


def sozialv_beitr_arbeitgeber_m(
    ges_pflegev_beitr_arbeitgeber_m: float,
    ges_krankenv_beitr_arbeitgeber_m: float,
    ges_rentenv_beitr_arbeitgeber_m: float,
    arbeitsl_v_beitr_arbeitgeber_m: float,
) -> float:
    """Sum of employer's social insurance contributions.

    Parameters
    ----------
    ges_pflegev_beitr_arbeitgeber_m
        See :func:`ges_pflegev_beitr_arbeitgeber_m`.
    ges_krankenv_beitr_arbeitgeber_m
        See :func:`ges_krankenv_beitr_arbeitgeber_m`.
    ges_rentenv_beitr_arbeitgeber_m
        See :func:`ges_rentenv_beitr_arbeitgeber_m`.
    arbeitsl_v_beitr_arbeitgeber_m
        See :func:`arbeitsl_v_beitr_arbeitgeber_m`.

    Returns
    -------

    """
    return (
        ges_pflegev_beitr_arbeitgeber_m
        + ges_krankenv_beitr_arbeitgeber_m
        + ges_rentenv_beitr_arbeitgeber_m
        + arbeitsl_v_beitr_arbeitgeber_m
    )


def _sozialv_beitr_summe_m(
    sozialv_beitr_arbeitnehmer_m: float,
    sozialv_beitr_arbeitgeber_m: float,
) -> float:
    """Sum of employer's and employee's social insurance contributions.

    Parameters
    ----------
    sozialv_beitr_arbeitnehmer_m
        See :func:`sozialv_beitr_arbeitnehmer_m`.
    sozialv_beitr_arbeitgeber_m
        See :func:`sozialv_beitr_arbeitgeber_m`.
    Returns
    -------

    """
    return sozialv_beitr_arbeitnehmer_m + sozialv_beitr_arbeitgeber_m
