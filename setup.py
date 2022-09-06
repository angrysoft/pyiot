from setuptools import setup, find_packages
from pyiot import __version__


setup(
    name="pyiot",
    version=__version__,
    packages=find_packages(),
    url="https://bitbucket.org/angrysoft/angryhome",
    license="Apache 2.0",
    author="AngrySoft",
    author_email="sebastian.zwierzchowski@gmail.com",
    description="",
    requires=["zeroconf", "pycryptodomex"],
)
