# ds_util
Utility scripts that I'm using

## Example outputs of AST
```bash
(.venv) danielsinkin@Air-von-Daniel ds_util % ds.ast . --header_only
'/Users/danielsinkin/GitHub_private/ds_util/time_tracker.py' (lines=230, functions=12, classes=3)
'/Users/danielsinkin/GitHub_private/ds_util/ast_explorer.py' (lines=338, functions=9, classes=3)
'/Users/danielsinkin/GitHub_private/ds_util/zsh.py' (lines=115, functions=2, classes=0)
'/Users/danielsinkin/GitHub_private/ds_util/linker.py' (lines=76, functions=2, classes=0)

Total: Files=4, Lines=759, Functions=25, Classes=6
```

## Custom .zshrc contents
```bash
alias code.='code .'

alias obsidian='open -a /Applications/Obsidian.app'

bindkey "^[[A" history-search-backward
bindkey "^[[B" history-search-forward


dspy.ls() {
echo "
dspy.ast=python3 /Users/danielsinkin/GitHub_private/ds_util/ast_explorer.py
dspy.zsh=python3 /Users/danielsinkin/GitHub_private/ds_util/zsh.py
dspy.link=python3 /Users/danielsinkin/GitHub_private/ds_util/linker.py
"
}

alias dspy.ast="python3 /Users/danielsinkin/GitHub_private/ds_util/ast_explorer.py"
alias dspy.zsh="python3 /Users/danielsinkin/GitHub_private/ds_util/zsh.py"
alias dspy.link="python3 /Users/danielsinkin/GitHub_private/ds_util/linker.py"
```
