import os
import pathlib
import re
import shutil
import string
from typing import Any, Dict, Optional

import click

from ....contrib.cli.base import BaseCommand

DEFAULT_TEMPLATES_DIR = pathlib.Path(__file__).parent.resolve() / "templates"

PLACEHOLDERS_TO_REPLACE_IN_DEST_FILENAMES = {
    "project_name": "project_name",
    "root_namespace": "root_namespace",
}

SOURCE_PATHS_TO_IGNORE = [
    re.compile(r"^.+\.py[cod]$"),
]

PYTHON_CONTEXTS = {
    "3.10": {
        "python_docker_image": "python:3.10",
        "black_target_version": '["py310"]',
    },
    "3.11": {
        "python_docker_image": "python:3.11",
        "black_target_version": '["py311"]',
    },
    "3.12": {
        "python_docker_image": "python:3.12",
        "black_target_version": '["py312"]',
    },
}


class Template(string.Template):
    delimiter = "$%"


class StartProjectCommand(BaseCommand):
    reraise_exceptions = (click.UsageError,)

    _templates_dir: pathlib.Path

    def get_dest_filename(self, src_filename: str, context: Dict[str, Any]) -> str:
        for placeholder, var_name in PLACEHOLDERS_TO_REPLACE_IN_DEST_FILENAMES.items():
            src_filename = src_filename.replace(placeholder, context[var_name])

        return src_filename

    def get_dest_dir(
        self,
        src_dir: str,
        project_path: str,
        context: Dict[str, Any],
    ) -> pathlib.Path:
        dest_dir = src_dir.replace(str(self._templates_dir), project_path)
        dest_dir = pathlib.Path(self.get_dest_filename(dest_dir, context))
        dest_dir.mkdir(mode=0o755, parents=True, exist_ok=True)
        return dest_dir

    def ignore_template_file(self, template_file_path: str) -> bool:
        for pattern in SOURCE_PATHS_TO_IGNORE:
            if re.match(pattern, template_file_path):
                return True

    def get_context(
        self,
        project_name: str,
        python_version: str,
        root_namespace: Optional[str] = None,
    ) -> Dict[str, Any]:
        project_name = project_name.replace("_", "-")
        project_name_underscore = project_name.replace("-", "_")
        return {
            "project_name": project_name,
            "project_name_underscore": project_name_underscore,
            "project_title": project_name.replace("-", " ").capitalize(),
            "root_namespace": root_namespace or project_name_underscore,
            **PYTHON_CONTEXTS[python_version],
        }

    def handle(
        self,
        *,
        project_name: str,
        project_path: pathlib.Path,
        root_namespace: str,
        python_version: str,
        ignore: bool = False,
        **options,
    ) -> None:
        context = self.get_context(
            project_name,
            python_version,
            root_namespace=root_namespace,
        )

        for templates_dir, _, template_files in os.walk(self._templates_dir):
            src_dir = pathlib.Path(templates_dir).resolve()
            dest_dir = self.get_dest_dir(templates_dir, str(project_path), context)

            for template_file in template_files:
                if self.ignore_template_file(template_file):
                    continue

                src_file = src_dir / template_file
                dest_file = dest_dir / self.get_dest_filename(template_file, context)

                if dest_file.exists() and ignore:
                    continue

                template = Template(src_file.read_text())
                dest_file.write_text(template.substitute(**context))
                shutil.copymode(src_file, dest_file)

    def validate_options(
        self,
        *,
        project_path: pathlib.Path,
        templates_dir: pathlib.Path,
        force: bool,
        ignore: bool,
        **options,
    ) -> None:
        self._templates_dir = templates_dir

        if (
            project_path.exists()
            and next(project_path.iterdir(), False)
            and not force
            and not ignore
        ):
            raise click.UsageError(
                f"{project_path} directory is not empty, change the project path"
                f" or use the -f|--force flag to overwrite existing files"
                f" or use the -i|--ignore flag to use existing files."
            )

        if force and ignore:
            raise click.UsageError(
                "The --force and --ignore flags cannot be used at the same time.",
            )


@click.command("startproject")
@click.option(
    "-n",
    "--name",
    "project_name",
    type=str,
    required=True,
    help="Name of the new project.",
)
@click.option(
    "-p",
    "--path",
    "project_path",
    type=click.Path(
        file_okay=False,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the new project.",
)
@click.option(
    "-t",
    "--templates",
    "templates_dir",
    type=click.Path(
        exists=True,
        file_okay=False,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    default=DEFAULT_TEMPLATES_DIR,
    show_default=True,
    help="Path to the templates directory.",
)
@click.option(
    "-r",
    "--root",
    "root_namespace",
    type=str,
    help="The name of the new project's root namespace.",
)
@click.option(
    "--python",
    "python_version",
    type=click.Choice(PYTHON_CONTEXTS),
    required=True,
    help="Python version of the new project.",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Overwrite files existing in the new project path.",
)
@click.option(
    "-i",
    "--ignore",
    is_flag=True,
    help="Use files that exist in the new project path.",
)
@click.pass_context
def startproject_cmd(ctx: click.Context, **options) -> None:
    StartProjectCommand(ctx.command.name, **ctx.parent.params).run(**options)
