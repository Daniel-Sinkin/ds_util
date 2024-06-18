import sys
import webbrowser

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
    "d2l": "https://learn.d2l.ai",
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
    print("Links:")
    for idx, key in enumerate(link_keys, 1):
        print(f"{idx:03d}. {key} - {links[key]}")
    print("\nGroups:")
    for group in groups:
        print(f"{group}: {', '.join(groups[group])}")


def open_link(index_or_key):
    try:
        # If index_or_key is a digit, treat it as an index
        if index_or_key.isdigit():
            index = int(index_or_key) - 1
            link = link_list[index]
        else:
            # Otherwise, treat it as a key
            link = links[index_or_key]

        webbrowser.open(link)
    except (IndexError, KeyError):
        print(f"Invalid link key or number: {index_or_key}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        list_links()
    else:
        for key_or_index in sys.argv[1:]:
            if key_or_index in groups:
                # If the argument is a group, open all links in the group
                for group_key in groups[key_or_index]:
                    open_link(group_key)
            else:
                open_link(key_or_index)
