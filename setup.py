from setuptools import find_packages, setup

from eedro import get_version

setup(
    name="eedro",
    version=get_version(),
    author="Anton Yantsen",
    packages=find_packages(
        exclude=(
            "tests",
            "tests.*",
        )
    ),
    install_requires=[
        "click~=8.1",
        "PyYAML~=6.0",
        "pydantic~=2.8",
    ],
    entry_points={
        "console_scripts": ("eedro=eedro.__main__:main_cmd",),
    },
    zip_safe=False,
)
