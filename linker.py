import sys
import webbrowser

import colorama
import pyperclip
from colorama import Fore, Style

colorama.init(autoreset=True)

links: dict[str, str] = {
    "jira": "https://drkv.atlassian.net/",
    "github": "https://github.com",
    "github_private": "https://github.com/Daniel-Sinkin",
    "github_work": "https://github.com/DanielSinkinJPK",
    "github_jpk": "https://github.com/drkv-com/jpk-core",
    "github_trb": "https://github.com/drkv-com/tr-jpk-brokerfacade",
    "github_jpk_pulls": "https://github.com/drkv-com/jpk-core/pulls",
    "github_trb_pulls": "https://github.com/drkv-com/tr-jpk-brokerfacade/pulls",
    "grafana": "https://drkv.grafana.net/a/cloud-home-app",
    "opengl": "https://learnopengl.com",
    "d2l": "https://d2l.ai",
    "gpt": "https://chatgpt.com/?model=gpt-4o",
}

# Define groups
groups: dict[str, list[str]] = {
    "work": ["gpt", "github_jpk_pulls", "github_trb_pulls", "jira"],
}

# Convert the dictionary to a list for indexing
link_list = list(links.values())
link_keys = list(links.keys())


def list_links():
    max_name_len = max(len(key) for key in link_keys)
    print(f"{Fore.BLUE}Links:{Style.RESET_ALL}")
    for idx, key in enumerate(link_keys, 1):
        print(
            f"{Fore.GREEN}{idx:03d}{Style.RESET_ALL} - {Fore.CYAN}{key.ljust(max_name_len)}{Style.RESET_ALL} - {Fore.YELLOW}{links[key]}{Style.RESET_ALL}"
        )
    print(f"\n{Fore.BLUE}Groups:{Style.RESET_ALL}")
    for group in groups:
        print(f"{Fore.MAGENTA}{group}{Style.RESET_ALL}: {', '.join(groups[group])}")


def open_link(index_or_key, clipboard=False):
    try:
        if index_or_key.isdigit():
            index = int(index_or_key) - 1
            link = link_list[index]
        else:
            link = links[index_or_key]

        if clipboard:
            pyperclip.copy(link)
            print(f"{Fore.GREEN}Link copied to clipboard: {Style.RESET_ALL}{link}")
        else:
            webbrowser.open(link)
    except (IndexError, KeyError):
        print(f"{Fore.RED}Invalid link key or number: {index_or_key}{Style.RESET_ALL}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        list_links()
    else:
        clipboard_flag = "--clipboard" in sys.argv or "-c" in sys.argv
        command_args = [arg for arg in sys.argv[1:] if arg not in ("--clipboard", "-c")]

        for key_or_index in command_args:
            if key_or_index in groups:
                for group_key in groups[key_or_index]:
                    open_link(group_key, clipboard_flag)
            else:
                open_link(key_or_index, clipboard_flag)
