import pathlib

from click.testing import CliRunner

from eedro.__main__ import main_cmd


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

    assert (project_path / "pyproject.toml").exists()
    assert (project_path / "docker-compose.yml").exists()
    assert (project_path / "docker-compose.override.yml").exists()
    assert (project_path / "Makefile").exists()
    assert (project_path / "tests" / "test_version.py").exists()
    assert (project_path / "ci" / "tests" / "run.sh").exists()
    assert (project_path / "etc" / "config" / f"{project_name}.yml").exists()
    assert (project_path / root_namespace / "__main__.py").exists()
    assert (project_path / root_namespace / "__version__.py").exists()

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
