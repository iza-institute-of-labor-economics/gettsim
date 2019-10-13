SOC_SEC = ["svbeit", "rvbeit", "avbeit", "gkvbeit", "pvbeit"]
UI = ["m_alg1"]
PENS = ["pen_sim"]
ZVE = [
    "zve_nokfb",
    "zve_abg_nokfb",
    "zve_kfb",
    "zve_abg_kfb",
    "kifreib",
    "gross_e1",
    "gross_e4",
    "gross_e5",
    "gross_e6",
    "gross_e7",
    "gross_e1_tu",
    "gross_e4_tu",
    "gross_e5_tu",
    "gross_e6_tu",
    "gross_e7_tu",
    "ertragsanteil",
]
ZVE_LIST = ["nokfb", "kfb"]
TAX_SCHED = (
    [f"tax_{inc}" for inc in ZVE_LIST]
    + [f"tax_{inc}_tu" for inc in ZVE_LIST]
    + ["abgst_tu", "abgst", "soli", "soli_tu"]
)
KG = ["kindergeld_basis", "kindergeld_tu_basis"]
FC = ["incometax_tu", "incometax", "kindergeld", "kindergeld_hh", "kindergeld_tu"]
UHV = ["uhv"]
WG = ["wohngeld_basis", "wohngeld_basis_hh"]
ALG2 = [
    "ar_base_alg2_ek",
    "ar_alg2_ek_hh",
    "alg2_grossek_hh",
    "mehrbed",
    "regelbedarf",
    "regelsatz",
    "alg2_kdu",
    "uhv_hh",
]
KIZ = ["kiz_temp", "kiz_incrange"]
DPI = ["dpi_ind", "dpi"]
GROSS = ["gross"]

OUT_PUT = (
    SOC_SEC
    + UI
    + PENS
    + ZVE
    + TAX_SCHED
    + KG
    + FC
    + UHV
    + WG
    + ALG2
    + KIZ
    + DPI
    + GROSS
)
