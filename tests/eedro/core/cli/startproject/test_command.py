import click
import pytest

from eedro.contrib.cli.base import CommandError
from eedro.core.cli.startproject.command import Context, StartProjectCommand


def test_context_get_context_normalizes_project_name():
    context = Context.get_context(
        project_name="my_app",
        python_version="3.12",
        root_namespace="",
    )

    assert context.project_name == "my-app"
    assert context.project_name_underscore == "my_app"
    assert context.root_namespace == "my_app"
    assert context.python_local_version == "python3.12"


def test_get_dest_filename_replaces_placeholders(tmp_path):
    command = StartProjectCommand("startproject", work_dir=tmp_path)
    context = Context.get_context(
        project_name="demo-app",
        python_version="3.12",
        root_namespace="demo_root",
    )

    result = command.get_dest_filename("root_namespace/project_name.txt", context)

    assert result == "demo_root/demo-app.txt"


def test_validate_options_requires_force_or_ignore_for_non_empty_dir(tmp_path):
    project_path = tmp_path / "project"
    templates_dir = tmp_path / "templates"
    project_path.mkdir()
    templates_dir.mkdir()
    (project_path / "existing.txt").write_text("data")

    command = StartProjectCommand("startproject", work_dir=tmp_path)

    with pytest.raises(click.UsageError):
        command.validate_options(
            project_path=project_path,
            templates_dir=templates_dir,
            context_class_path=None,
            force=False,
            ignore=False,
        )


def test_validate_options_rejects_force_and_ignore_together(tmp_path):
    project_path = tmp_path / "project"
    templates_dir = tmp_path / "templates"
    project_path.mkdir()
    templates_dir.mkdir()

    command = StartProjectCommand("startproject", work_dir=tmp_path)

    with pytest.raises(click.UsageError):
        command.validate_options(
            project_path=project_path,
            templates_dir=templates_dir,
            context_class_path=None,
            force=True,
            ignore=True,
        )


def test_context_class_raises_command_error_for_unimportable_class(tmp_path):
    command = StartProjectCommand("startproject", work_dir=tmp_path)
    command._context_class_path = "not.existing.Context"

    with pytest.raises(CommandError):
        _ = command.context_class


def test_context_class_rejects_class_not_inheriting_context(tmp_path):
    command = StartProjectCommand("startproject", work_dir=tmp_path)
    command._context_class_path = "pathlib.Path"

    with pytest.raises(click.UsageError):
        _ = command.context_class


def test_handle_generates_project_files_from_templates(tmp_path):
    templates_dir = tmp_path / "templates"
    source_root = templates_dir / "root_namespace"
    source_root.mkdir(parents=True)
    (templates_dir / "project_name.txt").write_text("name=$%{project_name}\n")
    (source_root / "__init__.py").write_text("# $%{root_namespace}\n")
    (source_root / "config_project_name.txt").write_text("$%{python_local_version}")

    project_path = tmp_path / "generated"
    project_path.mkdir()

    command = StartProjectCommand("startproject", work_dir=tmp_path)
    command.run(
        project_name="sample-app",
        project_path=project_path,
        templates_dir=templates_dir,
        context_class_path=None,
        root_namespace="sample_root",
        python_version="3.12",
        force=True,
        ignore=False,
    )

    assert (project_path / "sample-app.txt").read_text() == "name=sample-app\n"
    assert (
        project_path / "sample_root" / "__init__.py"
    ).read_text() == "# sample_root\n"
    assert (
        project_path / "sample_root" / "config_sample-app.txt"
    ).read_text() == "python3.12"


def test_handle_respects_ignore_for_existing_destination_files(tmp_path):
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    (templates_dir / "project_name.txt").write_text("generated=$%{project_name}\n")

    project_path = tmp_path / "generated"
    project_path.mkdir()
    existing_file = project_path / "keep-me.txt"
    existing_file.write_text("manual\n")
    # Template file resolves to keep-me.txt by using project_name = keep-me.
    (templates_dir / "project_name.txt").rename(templates_dir / "keep-me.txt")
    (templates_dir / "keep-me.txt").write_text("generated=$%{project_name}\n")

    command = StartProjectCommand("startproject", work_dir=tmp_path)
    command.run(
        project_name="keep-me",
        project_path=project_path,
        templates_dir=templates_dir,
        context_class_path=None,
        root_namespace="keep_me",
        python_version="3.12",
        force=False,
        ignore=True,
    )

    assert existing_file.read_text() == "manual\n"
