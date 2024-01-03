from .core.cli.main import main_cmd
from .core.cli.startproject.command import startproject_cmd

main_cmd.add_command(startproject_cmd)


if __name__ == "__main__":
    main_cmd()
