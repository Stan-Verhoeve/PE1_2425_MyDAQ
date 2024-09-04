from setuptools import setup

setup(
    name="SPAN",
    version="0.1.0",
    description="Simple code to drive the NiDAQ",
    url="https://github.com/Stan-Verhoeve/MyDAQ",
    author="Stan Verhoeve",
    author_email="verhoeve@strw.leidenuniv.nl",
    packages=["span"],
    install_requires=["numpy",
                      "scipy",
                      "nidaqmx",
                      ],
)
