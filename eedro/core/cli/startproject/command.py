import click

from ....contrib.cli.base import BaseCommand, CommandError


class StartProjectCommand(BaseCommand):
    def handle(self, **options) -> None:
        try:
            1 / 0
        except Exception as e:
            raise CommandError(e) from e


@click.command("startproject")
@click.pass_context
def startproject_cmd(ctx: click.Context, **options) -> None:
    StartProjectCommand(ctx, **ctx.parent.params).run(**options)
