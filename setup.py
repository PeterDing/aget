
import sys


try:
    from setuptools import setup
except ImportError:
    # Use distutils.core as a fallback.
    # We won't be able to build the Wheel file on Windows.
    from distutils.core import setup

if sys.version_info < (3, 5, 0):
    raise RuntimeError("aget requires Python 3.5.0+")

version = "0.1.9"

requires = ["mugen"]

setup(
    name="aget",
    version=version,
    author="PeterDing",
    author_email="dfhasyt@gmail.com",
    license="Apache 2.0",

    description="",
    url="http://github.com/PeterDing/aget",

    install_requires=requires,

    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
    ],

    packages=["aget"],

    scripts=['bin/aget'],

    include_package_data=True
)
