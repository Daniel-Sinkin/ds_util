import subprocess
import sys

zsh_commands = [
    "ssh-add ~/.ssh/id_ed25519",
    "ssh-add ~/.ssh/github_private",
    "nvim ~/.zshrc",
]

python_scripts = [
    "python3 /Users/danielsinkin/GitHub_private/ds_util/ast_explorer.py",
]

commands = zsh_commands + python_scripts


def list_commands():
    for idx, command in enumerate(commands, 1):
        print(f"{idx:03d}. {command}")


def execute_command(index, args):
    try:
        command = commands[index - 1]
        if command.startswith("python3"):
            command += " " + " ".join(args)
        subprocess.run(command, shell=True, check=True)
    except IndexError:
        print(f"Invalid command number: {index}")
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        list_commands()
    elif len(sys.argv) >= 2 and sys.argv[1].isdigit():
        command_index = int(sys.argv[1])
        command_args = sys.argv[2:]
        execute_command(command_index, command_args)
    else:
        print("Usage: script.py [command_number] [args...]")
