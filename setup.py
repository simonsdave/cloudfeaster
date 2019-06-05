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


_author = "Dave Simons"
_author_email = "simonsdave@gmail.com"


def _long_description():
    try:
        with open('README.rst', 'r') as f:
            return f.read()
    except IOError:
        # simple fix for avoid failure on "source cfg4dev"
        return "a long description"


setup(
    name="cloudfeaster",
    packages=[
        "cloudfeaster",
        "cloudfeaster.samples",
        "cloudfeaster_extension",
    ],
    scripts=[
        'bin/check-circleci-config.sh',
        'bin/generate-circleci-config.py',
        'bin/check-consistent-clf-version.sh',
        'bin/run-all-spiders.sh',
        'bin/run-spider.sh',
    ],
    install_requires=[
        "colorama>=0.3.5",
        "jsonschema>=2.3.0",
        "python-dateutil==2.8.0",
        "selenium==3.141.0",
    ],
    include_package_data=True,
    version=version,
    description="Cloudfeaster",
    long_description=_long_description(),
    author=_author,
    author_email=_author_email,
    maintainer=_author,
    maintainer_email=_author_email,
    license="MIT",
    url="https://github.com/simonsdave/cloudfeaster",
    download_url="https://github.com/simonsdave/cloudfeaster/tarball/v%s" % version,
    keywords=[
        'selenium',
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
