import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="covid-npi",
    use_scm_version=True,
    author="UCA Datalab",
    author_email="david.gomezullate@uca.es",
    description="COVID NPI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/UCA-Datalab/covid-npi.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7, <3.8",
    setup_requires=["setuptools_scm"],
    install_requires=[
        "matplotlib==3.2.1",
        "numpy==1.18.1",
        "pandas==1.0.3",
        "pip==19.3",
        "pymongo==3.11.0",
        "pytest==6.2.4",
        "scipy==1.7.1",
        "toml==0.10.2",
        "typer==0.3.2",
        "xlrd==1.1.0",
    ],
)
