from distutils.core import setup
import re

s = open('asynccapsolver/version.py').read()
v = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", s, re.M).group(1)

setup(name='asynccapsolver',
    version=v,
    description='Async API wrapper for capsolver',
    install_requires=["aiohttp","certifi"],
    author='optinsoft',
    author_email='optinsoft@gmail.com',
    keywords=['capsolver','async'],
    url='https://github.com/optinsoft/asynccapsolver',
    packages=['asynccapsolver']
)