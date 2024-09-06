# Description
SPectral ANalyzer (SPAN) is a very basic code to drive the NI MyDAQ for automated measurements. Functionality is very bare-bones, but is enough to successfully complete the PE1 course at Leiden University

# Installation
It is recommended to create a virtual python3 environment and activate it. See e.g. https://docs.python.org/3/library/venv.html
* `git clone` the repository using either `HTTPS` or `SSH`
* Move into the main directory
* Install using `pip install .`

Alternatively, the [source code](span) can be used on its own to drive the NI MyDAQ. Keep in mind that (relative) imports referencing `SPAN` may not work if your Python interpreter does not have access to the PATH of the source code.

# Usage
Basic usage for driving the MyDAQ and analysing spectra can be found in the [examples](examples) directory.


