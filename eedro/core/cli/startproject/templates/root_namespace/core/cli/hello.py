import click


@click.option(
    "-u",
    "--user",
    type=str,
    default="Anonymous",
    show_default=True,
    help="A username to say hello to.",
)
@click.command("hello")
@click.pass_context
def hello_cmd(ctx: click.Context, *, user: str):
    click.echo(f"Debug mode is {'on' if ctx.obj['DEBUG'] else 'off'}!")
    click.echo(f"Hello {user}!")
