from setuptools import setup


setup(
    name="pyjj",
    version="1.0",
    author="Changhyun An",
    author_email="88soldieron" "@" "gmail.com",
    py_modules=["pyjj"],
    install_requires=["click"],
    maintainer="Changhyun An",
    maintainer_email="88soldieron" "@" "gmail.com",
    url="https://www.github.com/achooan/pyjj",
    description="A command line interface for bookmark management",
    entry_points={"console_scripts": ["pyjj=pyjj:pyjj"]},
)
