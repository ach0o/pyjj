from os import path

from setuptools import setup


def get_long_description() -> str:
    readme = path.join(path.dirname(path.abspath(__file__)), "README.md")
    with open(readme, encoding="utf8") as f:
        return f.read()


setup(
    name="pyjj",
    version="0.0.1",
    author="Changhyun An",
    author_email="88soldieron@gmail.com",
    py_modules=["pyjj"],
    install_requires=["click", "pyyaml"],
    maintainer="Changhyun An",
    maintainer_email="88soldieron@gmail.com",
    url="https://www.github.com/achooan/pyjj",
    license="MIT",
    description="A bookmark management CLI",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    entry_points={"console_scripts": ["pyjj=pyjj:pyjj"]},
    python_requires=">=3.7",
    packages=["pyjj"],
)
