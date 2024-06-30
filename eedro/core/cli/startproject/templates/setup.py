from setuptools import find_packages, setup

from $%{root_namespace} import get_version

setup(
    name="$%{project_name}",
    version=get_version() or "0.0.1",
    description="<description of the $%{project_title} project>",
    license="<license of the $%{project_title} project>",
    author="<name of the author of the $%{project_title} project>",
    author_email="<email of the author of the $%{project_title} project>",
    packages=find_packages(
        exclude=(
            "tests",
            "tests.*",
        )
    ),
    install_requires=[
        "click~=8.1",
        "aiohttp~=3.9",
        "PyYAML~=6.0",
    ],
    entry_points={
        "console_scripts": ("$%{project_name}=$%{root_namespace}.__main__:manage_cmd",),
    },
    zip_safe=False,
)
