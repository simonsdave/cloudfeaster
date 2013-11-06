from setuptools import setup

setup(
    name='clf',
    py_modules=[
        'clf.spider',
        'clf.webdriver_spider',
    ],
    install_requires=[
        'selenium==2.35.0',
    ],
    version=1.0,
    description="CloudFeaster",
    author="Dave Simons",
    author_email="simonsdave@gmail.com",
    url="https://github.com/simonsdave/clf"
)
