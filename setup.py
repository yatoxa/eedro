from setuptools import find_packages, setup

setup(
    name="eedro",
    version="0.0.1",
    author="Anton Yantsen",
    packages=find_packages(
        exclude=(
            "tests",
            "tests.*",
        )
    ),
    install_requires=[
        "click~=8.1",
    ],
    entry_points={
        "console_scripts": ("eedro=eedro.__main__:main_cmd",),
    },
    zip_safe=False,
)
