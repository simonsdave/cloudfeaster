#
# to build the distrubution @ dist/cloudfeaster-*.*.*.tar.gz
#
#   >git clone https://github.com/simonsdave/cloudfeaster.git
#   >cd cloudfeaster
#   >source cfg4dev
#   >python setup.py sdist --formats=gztar
#

import re

from setuptools import setup

#
# this approach used below to determine ```version``` was inspired by
# https://github.com/kennethreitz/requests/blob/master/setup.py#L31
#
# why this complexity? wanted version number to be available in the
# a runtime.
#
# the code below assumes the distribution is being built with the
# current directory being the directory in which setup.py is stored
# which should be totally fine 99.9% of the time. not going to add
# the coode complexity to deal with other scenarios
#
reg_ex_pattern = r"__version__\s*=\s*['\"](?P<version>[^'\"]*)['\"]"
reg_ex = re.compile(reg_ex_pattern)
version = ""
with open("cloudfeaster/__init__.py", "r") as fd:
    for line in fd:
        match = reg_ex.match(line)
        if match:
            version = match.group("version")
            break
if not version:
    raise Exception("Can't locate cloudfeaster's version number")

setup(
    name="cloudfeaster",
    packages=[
        "cloudfeaster",
        "cloudfeaster.util",
    ],
    scripts=[
        "bin/spiderhost.py",
        "bin/spiderhost.sh",
        "bin/spiders.py",
    ],
    install_requires=[
        "colorama>=0.3.5",
        "jsonschema==2.5.1",
        # on 13 jan '16 tried to upgrade to selenium 2.49.0
        # but got errors during unit tests
        "selenium==2.48.0",
    ],
    include_package_data=True,
    version=version,
    description="Cloudfeaster",
    author="Dave Simons",
    author_email="simonsdave@gmail.com",
    url="https://github.com/simonsdave/cloudfeaster"
)
