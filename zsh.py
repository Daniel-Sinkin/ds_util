import subprocess
import sys

import pyperclip
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

snippets = {"hello_world": "Hello, World!"}

commands = (
    list(zsh_commands.values())
    + list(python_scripts.values())
    + list(snippets.values())
)
command_keys = (
    list(zsh_commands.keys()) + list(python_scripts.keys()) + list(snippets.keys())
)


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
    for name, snippet in snippets.items():
        print(
            f"{Fore.GREEN}{idx:03d}{Style.RESET_ALL} - {Fore.CYAN}{name.ljust(max_name_len)}{Style.RESET_ALL} - {Fore.YELLOW}{snippet}{Style.RESET_ALL}"
        )
        idx += 1


def execute_command(command_key, args, clipboard):
    try:
        if command_key.isdigit():
            index = int(command_key) - 1
            command = commands[index]
        else:
            if command_key in zsh_commands:
                command = zsh_commands[command_key]
            elif command_key in python_scripts:
                command = python_scripts[command_key]
            elif command_key in snippets:
                command = snippets[command_key]
                pyperclip.copy(command)
                print(
                    f"{Fore.GREEN}Snippet copied to clipboard: {Style.RESET_ALL}{command}"
                )
                return
            else:
                raise KeyError

        if command.startswith("python3"):
            command += " " + " ".join(args)

        if clipboard:
            pyperclip.copy(command)
            print(
                f"{Fore.GREEN}Command copied to clipboard: {Style.RESET_ALL}{command}"
            )
        else:
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
        clipboard_flag = "--clipboard" in sys.argv or "-c" in sys.argv
        command_args = [arg for arg in sys.argv[2:] if arg not in ("--clipboard", "-c")]
        execute_command(command_key, command_args, clipboard_flag)
