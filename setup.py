import io
import os

from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))


def load_readme():
    with io.open(os.path.join(HERE, "README.rst"), "rt", encoding="utf8") as f:
        return f.read()


def load_about():
    about = {}
    with io.open(
            os.path.join(HERE, "lektmfe", "__about__.py"), "rt", encoding="utf-8"
    ) as f:
        exec(f.read(), about)  # pylint: disable=exec-used
    return about


ABOUT = load_about()

setup(
    name="lekt-mfe",
    version=ABOUT["__version__"],
    url="https://github.com/lektorium-tutor/lekt-mfe",
    project_urls={
        "Code": "https://github.com/lektorium-tutor/lekt-mfe"
    },
    license="AGPLv3",
    author="Overhang.IO",
    maintainer="tCRIL",
    maintainer_email="adolfo@tcril.org",
    description="mfe plugin for Lekt",
    long_description=load_readme(),
    long_description_content_type="text/x-rst",
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    python_requires=">=3.5",
    install_requires=["lekt>=14.0.25,<15.0.0"],
    entry_points={"lekt.plugin.v1": ["mfe = lektmfe.plugin"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
