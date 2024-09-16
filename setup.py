from setuptools import setup

setup(
    name="SPAN",
    version="0.1.1",
    description="Simple code to drive the NI MyDAQ and perform simple spectral analysis",
    url="https://github.com/Stan-Verhoeve/MyDAQ",
    author="Stan Verhoeve",
    author_email="verhoeve@strw.leidenuniv.nl",
    packages=["span"],
    install_requires=[
        "numpy",
        "scipy",
        "nidaqmx",
        "matplotlib",
    ],
)
