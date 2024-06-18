import subprocess
import sys

zsh_commands = {
    "ssh_work": "ssh-add ~/.ssh/id_ed25519",
    "ssh_private": "ssh-add ~/.ssh/github_private",
    "zshrc": "nvim ~/.zshrc",
    "ds_util": "code /Users/danielsinkin/GitHub_private/ds_util/",
    "obsidian": "code /Users/danielsinkin/GitHub_private/Obsidian/",
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
        print(f"{idx:03d} - {name.ljust(max_name_len)} - {command}")
        idx += 1
    for name, command in python_scripts.items():
        print(f"{idx:03d} - {name.ljust(max_name_len)} - {command}")
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
        print(f"Invalid command: {command_key}")
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        list_commands()
    else:
        command_key = sys.argv[1]
        command_args = sys.argv[2:]
        execute_command(command_key, command_args)
