from pathlib import Path

from setuptools import find_packages
from setuptools import setup


DESCRIPTION = (
    "GETTSIM aims at providing a depiction of the German Taxes and Transfers System "
    "that is usable across a wide range of research applications, ranging from highly "
    "complex dynamic programming models to extremely detailed micro-simulation studies."
)
README = Path("README.rst").read_text()
PROJECT_URLS = {
    "Bug Tracker": "https://github.com/iza-institute-of-labor-economics/gettsim/issues",
    "Documentation": "https://gettsim.readthedocs.io",
    "Source Code": "https://github.com/iza-institute-of-labor-economics/gettsim",
}


setup(
    name="gettsim",
    version="0.4",
    description=DESCRIPTION,
    long_description=DESCRIPTION + "\n\n" + README,
    long_description_content_type="text/x-rst",
    author="Hans-Martin von Gaudecker",
    author_email="gaudecker@iza.org",
    python_requires=">=3.6",
    url="https://gettsim.readthedocs.io",
    project_urls=PROJECT_URLS,
    packages=find_packages(),
    license="AGPLv3",
    keywords=["Economics", "Taxes and Transfers", "Germany"],
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    platforms="any",
    package_data={
        "gettsim": [
            "parameters/*.yaml",
            "pre_processing/exogene_renten_daten/*.yaml",
            "tests/test_data/*.csv",
            "tests/test_data/*.ods",
            "synthetic_data/*.yaml",
        ]
    },
    include_package_data=True,
    zip_safe=False,
)
