import pathlib

from click.testing import CliRunner

from eedro.__main__ import main_cmd


def _get_expected_generated_files(project_name: str, root_namespace: str) -> set[str]:
    return {
        ".dockerignore",
        ".editorconfig",
        ".flake8",
        ".gitignore",
        "Makefile",
        "MANIFEST.in",
        "bin/manage.sh",
        "ci/base/Dockerfile",
        "ci/nginx/Dockerfile",
        "ci/nginx/templates/ping.conf.template",
        "ci/ping/run.sh",
        "ci/pong/run.sh",
        "ci/tests/Dockerfile",
        "ci/tests/run.sh",
        "docker-compose.override.yml",
        "docker-compose.yml",
        f"etc/config/{project_name}.yml",
        "pyproject.toml",
        f"{root_namespace}/__init__.py",
        f"{root_namespace}/__main__.py",
        f"{root_namespace}/__version__.py",
        f"{root_namespace}/contrib/README.md",
        f"{root_namespace}/contrib/__init__.py",
        f"{root_namespace}/core/README.md",
        f"{root_namespace}/core/__init__.py",
        f"{root_namespace}/core/cli/__init__.py",
        f"{root_namespace}/core/cli/hello.py",
        f"{root_namespace}/core/cli/manage.py",
        f"{root_namespace}/core/server/__init__.py",
        f"{root_namespace}/core/server/base.py",
        f"{root_namespace}/core/server/ping.py",
        f"{root_namespace}/core/server/pong.py",
        "tests/__init__.py",
        "tests/test_hello.py",
        "tests/test_ping.py",
        "tests/test_pong.py",
        "tests/test_version.py",
    }


def test_startproject_smoke_generates_expected_project_artifacts(
    tmp_path: pathlib.Path,
) -> None:
    runner = CliRunner()
    project_path = tmp_path / "generated-project"
    project_name = "sample-app"
    root_namespace = "sample_root"

    result = runner.invoke(
        main_cmd,
        [
            "startproject",
            "--name",
            project_name,
            "--path",
            str(project_path),
            "--python",
            "3.12",
            "--root",
            root_namespace,
        ],
    )

    assert result.exit_code == 0, result.output

    generated_files = {
        path.relative_to(project_path).as_posix()
        for path in project_path.rglob("*")
        if path.is_file()
    }
    assert generated_files == _get_expected_generated_files(
        project_name,
        root_namespace,
    )

    for file_path in tmp_path.rglob("*"):
        if file_path.is_file():
            assert (
                "$%" not in file_path.read_text()
            ), f"{file_path.name} is rendered incorrectly"

    pyproject_content = (project_path / "pyproject.toml").read_text()

    assert 'target-version = ["py312"]' in pyproject_content
    assert f'name = "{project_name}"' in pyproject_content
    assert (
        f'{project_name} = "{root_namespace}.__main__:manage_cmd"'  # noqa: E231
        in pyproject_content
    )
