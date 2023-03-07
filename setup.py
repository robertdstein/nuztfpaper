import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nuztfpaper",
    version="0.1.0",
    author="Robert Stein",
    author_email="rdstein@caltech.edu",
    description="Code for analysis used in ZTF Neutrino Program paper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords="astronomy astroparticle science",
    url="https://github.com/robertdstein/nuztfpaper",
    packages=setuptools.find_packages(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.10",
    install_requires=[
        "matplotlib",
        "astropy",
        "jupyter",
        "seaborn",
        "nuztf>=2.4.1",
        "flarestack>=2.2.6",
        "openpyxl",
        "numpy",
        "pandas",
    ],
)
