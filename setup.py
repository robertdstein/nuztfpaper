import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ztf_nu_paper_code",
    version="0.0.1",
    author="Robert Stein",
    author_email="robert.stein@desy.de",
    description="Code for plots used in ZTF Neutrino Program paper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords="astroparticle physics science",
    url="https://github.com/robertdstein/ztf_nu_paper_code",
    packages=setuptools.find_packages(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires='>=3.7',
    install_requires=[
        "matplotlib",
        "astropy",
        "jupyter",
        "seaborn",
        "nuztf"
    ],
)
