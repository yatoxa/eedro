import click

from ... import get_version


@click.group()
@click.version_option(version=get_version(), package_name="$%{project_name}")
@click.option("--debug", is_flag=True, help="Enable debug mode.")
@click.pass_context
def manage_cmd(ctx: click.Context, *, debug: bool):
    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug
