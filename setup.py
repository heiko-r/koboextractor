import setuptools
import os

readmepath = os.path.join(os.path.dirname(__file__), 'README.rst')
with open(readmepath, "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="koboextractor",
    version="0.2.0",
    author="Heiko Rothkranz",
    description="Extract datasets from KoBoToolbox",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/heiko-r/koboextractor",
    project_urls={
        'Documentation': 'https://koboextractor.readthedocs.io',
        'Source': 'https://github.com/heiko-r/koboextractor/',
        'Tracker': 'https://github.com/heiko-r/koboextractor/issues',
    },
    keywords='KoBoToolbox',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'requests'
    ],
    python_requires='>=3.6',
)