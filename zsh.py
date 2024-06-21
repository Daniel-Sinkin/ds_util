import subprocess
import sys

from colorama import Fore, Style, init

init(autoreset=True)

zsh_commands = {
    "ssh_work": "ssh-add ~/.ssh/id_ed25519",
    "ssh_private": "ssh-add ~/.ssh/github_private",
    "zshrc": "nvim ~/.zshrc",
    "ds_util": "code /Users/danielsinkin/GitHub_private/ds_util/",
    "obsidian": "code /Users/danielsinkin/GitHub_private/Obsidian/",
    "opengl": "code /Users/danielsinkin/GitHub_private/opengl/",
    "jpk": "code /Users/danielsinkin/GitHub/jpk-core/",
    "trb": "code /Users/danielsinkin/GitHub/tr-jpk-brokerfacade/",
}

python_scripts = {
    "ast": "python3 /Users/danielsinkin/GitHub_private/ds_util/ast_explorer.py",
    "link": "python3 /Users/danielsinkin/GitHub_private/ds_util/linker.py",
}

commands = list(zsh_commands.values()) + list(python_scripts.values())
command_keys = list(zsh_commands.keys()) + list(python_scripts.keys())


def list_commands():
    idx = 1
    max_name_len = max(
        max(len(name) for name in command_keys),
        max(len(name) for name in python_scripts.keys()),
    )
    for name, command in zsh_commands.items():
        print(
            f"{Fore.GREEN}{idx:03d}{Style.RESET_ALL} - {Fore.CYAN}{name.ljust(max_name_len)}{Style.RESET_ALL} - {Fore.YELLOW}{command}{Style.RESET_ALL}"
        )
        idx += 1
    for name, command in python_scripts.items():
        print(
            f"{Fore.GREEN}{idx:03d}{Style.RESET_ALL} - {Fore.CYAN}{name.ljust(max_name_len)}{Style.RESET_ALL} - {Fore.YELLOW}{command}{Style.RESET_ALL}"
        )
        idx += 1


def execute_command(command_key, args):
    try:
        if command_key.isdigit():
            index = int(command_key) - 1
            command = commands[index]
        else:
            if command_key in zsh_commands:
                command = zsh_commands[command_key]
            elif command_key in python_scripts:
                command = python_scripts[command_key]
            else:
                raise KeyError

        if command.startswith("python3"):
            command += " " + " ".join(args)

        subprocess.run(command, shell=True, check=True)
    except (IndexError, KeyError):
        print(f"{Fore.RED}Invalid command: {command_key}{Style.RESET_ALL}")
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Command failed: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        list_commands()
    else:
        command_key = sys.argv[1]
        command_args = sys.argv[2:]
        execute_command(command_key, command_args)
