from .core.cli.hello import hello_cmd
from .core.cli.manage import manage_cmd

manage_cmd.add_command(hello_cmd)


if __name__ == "__main__":
    manage_cmd(obj={})
