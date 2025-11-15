#!/bin/bash
# Bash completion script for AccuDoc CLI
# Install: Copy to /etc/bash_completion.d/accudoc or source in ~/.bashrc

_accudoc_completions() {
    local cur prev opts commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Main commands
    commands="scan generate export site info cache check-links plugins batch \
              branch-compare version-check spellcheck multi-repo coverage \
              readability db-schema monorepo breaking-changes code-quality \
              grammar doc-coverage dataflow"
    
    # Global options
    global_opts="-h --help -v --verbose -q --quiet"
    
    # Get the command (first word after accudoc_cli.py or accudoc)
    local command=""
    for ((i=1; i < ${#COMP_WORDS[@]}; i++)); do
        if [[ "${COMP_WORDS[i]}" != -* ]]; then
            command="${COMP_WORDS[i]}"
            break
        fi
    done
    
    # If no command yet, complete commands
    if [[ -z "$command" ]] || [[ "$command" == "$cur" ]]; then
        COMPREPLY=( $(compgen -W "${commands} ${global_opts}" -- ${cur}) )
        return 0
    fi
    
    # Command-specific completions
    case "${command}" in
        scan)
            local opts="-o --output -f --format -e --exclude --include-hidden --no-cache"
            if [[ ${cur} == -* ]]; then
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            else
                # Complete with directories
                COMPREPLY=( $(compgen -d -- ${cur}) )
            fi
            ;;
        generate)
            local opts="-o --output -t --template --format --theme"
            if [[ ${cur} == -* ]]; then
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            elif [[ ${prev} == "--format" ]] || [[ ${prev} == "-f" ]]; then
                COMPREPLY=( $(compgen -W "markdown html text" -- ${cur}) )
            elif [[ ${prev} == "--template" ]] || [[ ${prev} == "-t" ]]; then
                COMPREPLY=( $(compgen -W "default minimal detailed api" -- ${cur}) )
            elif [[ ${prev} == "--theme" ]]; then
                COMPREPLY=( $(compgen -W "default dark minimal corporate" -- ${cur}) )
            else
                # Complete with files
                COMPREPLY=( $(compgen -f -- ${cur}) )
            fi
            ;;
        export)
            local opts="-o --output -t --template --format --theme --no-cache"
            if [[ ${cur} == -* ]]; then
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            elif [[ ${prev} == "--format" ]]; then
                COMPREPLY=( $(compgen -W "markdown html text" -- ${cur}) )
            elif [[ ${prev} == "--template" ]] || [[ ${prev} == "-t" ]]; then
                COMPREPLY=( $(compgen -W "default minimal detailed api" -- ${cur}) )
            else
                COMPREPLY=( $(compgen -d -- ${cur}) )
            fi
            ;;
        site)
            local opts="-o --output --theme --title --no-search"
            if [[ ${cur} == -* ]]; then
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            elif [[ ${prev} == "--theme" ]]; then
                COMPREPLY=( $(compgen -W "default dark minimal" -- ${cur}) )
            else
                COMPREPLY=( $(compgen -f -- ${cur}) )
            fi
            ;;
        info)
            local opts="--version"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            ;;
        cache)
            local opts="-c --clear -s --stats --path"
            if [[ ${cur} == -* ]]; then
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            else
                COMPREPLY=( $(compgen -d -- ${cur}) )
            fi
            ;;
        check-links)
            local opts="-o --output --external --timeout"
            if [[ ${cur} == -* ]]; then
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            else
                COMPREPLY=( $(compgen -d -- ${cur}) )
            fi
            ;;
        plugins)
            local opts="-l --list -i --info -d --directory"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            ;;
        batch)
            if [[ ${cur} == -* ]]; then
                COMPREPLY=()
            else
                # Complete with .json files
                COMPREPLY=( $(compgen -f -X '!*.json' -- ${cur}) )
            fi
            ;;
        branch-compare)
            local opts="-b --base -c --compare -o --output -f --format -l --list"
            if [[ ${cur} == -* ]]; then
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            elif [[ ${prev} == "--format" ]] || [[ ${prev} == "-f" ]]; then
                COMPREPLY=( $(compgen -W "markdown json" -- ${cur}) )
            else
                COMPREPLY=( $(compgen -d -- ${cur}) )
            fi
            ;;
        version-check)
            local opts="-o --output -f --format"
            if [[ ${cur} == -* ]]; then
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            elif [[ ${prev} == "--format" ]] || [[ ${prev} == "-f" ]]; then
                COMPREPLY=( $(compgen -W "markdown json" -- ${cur}) )
            else
                COMPREPLY=( $(compgen -d -- ${cur}) )
            fi
            ;;
        spellcheck)
            local opts="-o --output -f --format -e --extensions"
            if [[ ${cur} == -* ]]; then
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            elif [[ ${prev} == "--format" ]] || [[ ${prev} == "-f" ]]; then
                COMPREPLY=( $(compgen -W "markdown json" -- ${cur}) )
            else
                COMPREPLY=( $(compgen -f -- ${cur}) )
            fi
            ;;
        multi-repo)
            local opts="-o --output -c --config"
            if [[ ${cur} == -* ]]; then
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            else
                COMPREPLY=( $(compgen -f -- ${cur}) )
            fi
            ;;
        coverage|readability|db-schema|monorepo|breaking-changes|code-quality|grammar|doc-coverage)
            local opts="-o --output -f --format"
            if [[ ${cur} == -* ]]; then
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            elif [[ ${prev} == "--format" ]] || [[ ${prev} == "-f" ]]; then
                COMPREPLY=( $(compgen -W "markdown json" -- ${cur}) )
            else
                COMPREPLY=( $(compgen -d -- ${cur}) )
            fi
            ;;
        dataflow)
            local opts="-o --output -f --format --no-diagrams"
            if [[ ${cur} == -* ]]; then
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            elif [[ ${prev} == "--format" ]] || [[ ${prev} == "-f" ]]; then
                COMPREPLY=( $(compgen -W "markdown json" -- ${cur}) )
            else
                # Complete with directories and .py files
                COMPREPLY=( $(compgen -f -X '!*.py' -- ${cur}) $(compgen -d -- ${cur}) )
            fi
            ;;
        *)
            # Default file/directory completion
            COMPREPLY=( $(compgen -f -- ${cur}) )
            ;;
    esac
    
    return 0
}

# Register completion function
complete -F _accudoc_completions accudoc_cli.py
complete -F _accudoc_completions accudoc
complete -F _accudoc_completions python accudoc_cli.py
complete -F _accudoc_completions python3 accudoc_cli.py
