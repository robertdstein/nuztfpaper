import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nuztfpaper",
    version="0.0.1",
    author="Robert Stein",
    author_email="robert.stein@desy.de",
    description="Code for plots used in ZTF Neutrino Program paper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords="astroparticle physics science",
    url="https://github.com/robertdstein/nuztfpaper",
    packages=setuptools.find_packages(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires='>=3.8',
    install_requires=[
        "matplotlib",
        "astropy",
        "jupyter",
        "seaborn",
        "nuztf",
        "flarestack==2.2.6",
        "openpyxl",
        "nuztf"
    ],
)
