# ds_util
Utility scripts that I'm using

My custom .zshrc contents:
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