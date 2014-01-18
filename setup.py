from setuptools import setup

setup(
    name="clf",
    packages=[
        "clf",
        "clf.clicmd",
        "clf.util",
        "clf.spider_host",
        "clf.spider_repo",
    ],
    scripts=[
        "bin/clf",
        "bin/spider_host",
    ],
    install_requires=[
        "selenium==2.35.0",
        "boto==2.15.0",
        "jsonschema==2.3.0",
        "python-keyczar==0.71c",
    ],
    version=1.0,
    description="CloudFeaster",
    author="Dave Simons",
    author_email="simonsdave@gmail.com",
    url="https://github.com/simonsdave/clf"
)
