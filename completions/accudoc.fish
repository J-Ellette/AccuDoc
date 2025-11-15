# Fish shell completion script for AccuDoc CLI
# Install: Copy to ~/.config/fish/completions/accudoc.fish

# Remove previous completions
complete -c accudoc -e
complete -c accudoc_cli.py -e

# Global options
complete -c accudoc -s h -l help -d 'Show help message'
complete -c accudoc -s v -l verbose -d 'Enable verbose output'
complete -c accudoc -s q -l quiet -d 'Suppress output'

complete -c accudoc_cli.py -s h -l help -d 'Show help message'
complete -c accudoc_cli.py -s v -l verbose -d 'Enable verbose output'
complete -c accudoc_cli.py -s q -l quiet -d 'Suppress output'

# Commands
set -l commands scan generate export site info cache check-links plugins batch branch-compare version-check spellcheck multi-repo coverage readability db-schema monorepo breaking-changes code-quality grammar doc-coverage dataflow

# Condition helpers
function __fish_accudoc_needs_command
    set -l cmd (commandline -opc)
    if test (count $cmd) -eq 1
        return 0
    end
    return 1
end

function __fish_accudoc_using_command
    set -l cmd (commandline -opc)
    if test (count $cmd) -gt 1
        if contains -- $cmd[2] $argv
            return 0
        end
    end
    return 1
end

# Command completions
complete -c accudoc -n '__fish_accudoc_needs_command' -a 'scan' -d 'Scan repository and generate analysis'
complete -c accudoc -n '__fish_accudoc_needs_command' -a 'generate' -d 'Generate documentation from scan results'
complete -c accudoc -n '__fish_accudoc_needs_command' -a 'export' -d 'Quick export (scan + generate in one command)'
complete -c accudoc -n '__fish_accudoc_needs_command' -a 'site' -d 'Generate static documentation website'
complete -c accudoc -n '__fish_accudoc_needs_command' -a 'info' -d 'Show AccuDoc version and information'
complete -c accudoc -n '__fish_accudoc_needs_command' -a 'cache' -d 'Manage scan result cache'
complete -c accudoc -n '__fish_accudoc_needs_command' -a 'check-links' -d 'Check for broken links in documentation'
complete -c accudoc -n '__fish_accudoc_needs_command' -a 'plugins' -d 'Manage AccuDoc plugins'
complete -c accudoc -n '__fish_accudoc_needs_command' -a 'batch' -d 'Process multiple repositories from batch file'
complete -c accudoc -n '__fish_accudoc_needs_command' -a 'branch-compare' -d 'Compare two git branches'
complete -c accudoc -n '__fish_accudoc_needs_command' -a 'version-check' -d 'Check package versions and dependencies'
complete -c accudoc -n '__fish_accudoc_needs_command' -a 'spellcheck' -d 'Check spelling in documentation'
complete -c accudoc -n '__fish_accudoc_needs_command' -a 'multi-repo' -d 'Analyze multiple related repositories'
complete -c accudoc -n '__fish_accudoc_needs_command' -a 'coverage' -d 'Analyze test coverage'
complete -c accudoc -n '__fish_accudoc_needs_command' -a 'readability' -d 'Analyze documentation readability'
complete -c accudoc -n '__fish_accudoc_needs_command' -a 'db-schema' -d 'Extract and document database schemas'
complete -c accudoc -n '__fish_accudoc_needs_command' -a 'monorepo' -d 'Analyze monorepo structure'
complete -c accudoc -n '__fish_accudoc_needs_command' -a 'breaking-changes' -d 'Detect breaking changes'
complete -c accudoc -n '__fish_accudoc_needs_command' -a 'code-quality' -d 'Analyze code quality metrics'
complete -c accudoc -n '__fish_accudoc_needs_command' -a 'grammar' -d 'Check grammar in documentation'
complete -c accudoc -n '__fish_accudoc_needs_command' -a 'doc-coverage' -d 'Analyze documentation coverage'
complete -c accudoc -n '__fish_accudoc_needs_command' -a 'dataflow' -d 'Analyze data flow in code'

# Duplicate for accudoc_cli.py
complete -c accudoc_cli.py -n '__fish_accudoc_needs_command' -a 'scan' -d 'Scan repository and generate analysis'
complete -c accudoc_cli.py -n '__fish_accudoc_needs_command' -a 'generate' -d 'Generate documentation from scan results'
complete -c accudoc_cli.py -n '__fish_accudoc_needs_command' -a 'export' -d 'Quick export (scan + generate in one command)'
complete -c accudoc_cli.py -n '__fish_accudoc_needs_command' -a 'site' -d 'Generate static documentation website'
complete -c accudoc_cli.py -n '__fish_accudoc_needs_command' -a 'info' -d 'Show AccuDoc version and information'
complete -c accudoc_cli.py -n '__fish_accudoc_needs_command' -a 'cache' -d 'Manage scan result cache'
complete -c accudoc_cli.py -n '__fish_accudoc_needs_command' -a 'check-links' -d 'Check for broken links in documentation'
complete -c accudoc_cli.py -n '__fish_accudoc_needs_command' -a 'plugins' -d 'Manage AccuDoc plugins'
complete -c accudoc_cli.py -n '__fish_accudoc_needs_command' -a 'batch' -d 'Process multiple repositories from batch file'
complete -c accudoc_cli.py -n '__fish_accudoc_needs_command' -a 'branch-compare' -d 'Compare two git branches'
complete -c accudoc_cli.py -n '__fish_accudoc_needs_command' -a 'version-check' -d 'Check package versions and dependencies'
complete -c accudoc_cli.py -n '__fish_accudoc_needs_command' -a 'spellcheck' -d 'Check spelling in documentation'
complete -c accudoc_cli.py -n '__fish_accudoc_needs_command' -a 'multi-repo' -d 'Analyze multiple related repositories'
complete -c accudoc_cli.py -n '__fish_accudoc_needs_command' -a 'coverage' -d 'Analyze test coverage'
complete -c accudoc_cli.py -n '__fish_accudoc_needs_command' -a 'readability' -d 'Analyze documentation readability'
complete -c accudoc_cli.py -n '__fish_accudoc_needs_command' -a 'db-schema' -d 'Extract and document database schemas'
complete -c accudoc_cli.py -n '__fish_accudoc_needs_command' -a 'monorepo' -d 'Analyze monorepo structure'
complete -c accudoc_cli.py -n '__fish_accudoc_needs_command' -a 'breaking-changes' -d 'Detect breaking changes'
complete -c accudoc_cli.py -n '__fish_accudoc_needs_command' -a 'code-quality' -d 'Analyze code quality metrics'
complete -c accudoc_cli.py -n '__fish_accudoc_needs_command' -a 'grammar' -d 'Check grammar in documentation'
complete -c accudoc_cli.py -n '__fish_accudoc_needs_command' -a 'doc-coverage' -d 'Analyze documentation coverage'
complete -c accudoc_cli.py -n '__fish_accudoc_needs_command' -a 'dataflow' -d 'Analyze data flow in code'

# scan command options
complete -c accudoc -n '__fish_accudoc_using_command scan' -s o -l output -d 'Output file' -r
complete -c accudoc -n '__fish_accudoc_using_command scan' -s f -l format -d 'Output format' -xa 'json markdown'
complete -c accudoc -n '__fish_accudoc_using_command scan' -s e -l exclude -d 'Exclude patterns' -r
complete -c accudoc -n '__fish_accudoc_using_command scan' -l include-hidden -d 'Include hidden files'
complete -c accudoc -n '__fish_accudoc_using_command scan' -l no-cache -d 'Disable caching'

complete -c accudoc_cli.py -n '__fish_accudoc_using_command scan' -s o -l output -d 'Output file' -r
complete -c accudoc_cli.py -n '__fish_accudoc_using_command scan' -s f -l format -d 'Output format' -xa 'json markdown'
complete -c accudoc_cli.py -n '__fish_accudoc_using_command scan' -s e -l exclude -d 'Exclude patterns' -r
complete -c accudoc_cli.py -n '__fish_accudoc_using_command scan' -l include-hidden -d 'Include hidden files'
complete -c accudoc_cli.py -n '__fish_accudoc_using_command scan' -l no-cache -d 'Disable caching'

# generate command options
complete -c accudoc -n '__fish_accudoc_using_command generate' -s o -l output -d 'Output file' -r
complete -c accudoc -n '__fish_accudoc_using_command generate' -s t -l template -d 'Template' -xa 'default minimal detailed api'
complete -c accudoc -n '__fish_accudoc_using_command generate' -l format -d 'Output format' -xa 'markdown html text'
complete -c accudoc -n '__fish_accudoc_using_command generate' -l theme -d 'HTML theme' -xa 'default dark minimal corporate'

complete -c accudoc_cli.py -n '__fish_accudoc_using_command generate' -s o -l output -d 'Output file' -r
complete -c accudoc_cli.py -n '__fish_accudoc_using_command generate' -s t -l template -d 'Template' -xa 'default minimal detailed api'
complete -c accudoc_cli.py -n '__fish_accudoc_using_command generate' -l format -d 'Output format' -xa 'markdown html text'
complete -c accudoc_cli.py -n '__fish_accudoc_using_command generate' -l theme -d 'HTML theme' -xa 'default dark minimal corporate'

# export command options
complete -c accudoc -n '__fish_accudoc_using_command export' -s o -l output -d 'Output file' -r
complete -c accudoc -n '__fish_accudoc_using_command export' -s t -l template -d 'Template' -xa 'default minimal detailed api'
complete -c accudoc -n '__fish_accudoc_using_command export' -l format -d 'Output format' -xa 'markdown html text'
complete -c accudoc -n '__fish_accudoc_using_command export' -l theme -d 'HTML theme' -xa 'default dark minimal corporate'
complete -c accudoc -n '__fish_accudoc_using_command export' -l no-cache -d 'Disable caching'

complete -c accudoc_cli.py -n '__fish_accudoc_using_command export' -s o -l output -d 'Output file' -r
complete -c accudoc_cli.py -n '__fish_accudoc_using_command export' -s t -l template -d 'Template' -xa 'default minimal detailed api'
complete -c accudoc_cli.py -n '__fish_accudoc_using_command export' -l format -d 'Output format' -xa 'markdown html text'
complete -c accudoc_cli.py -n '__fish_accudoc_using_command export' -l theme -d 'HTML theme' -xa 'default dark minimal corporate'
complete -c accudoc_cli.py -n '__fish_accudoc_using_command export' -l no-cache -d 'Disable caching'

# site command options
complete -c accudoc -n '__fish_accudoc_using_command site' -s o -l output -d 'Output directory' -r
complete -c accudoc -n '__fish_accudoc_using_command site' -l theme -d 'Site theme' -xa 'default dark minimal'
complete -c accudoc -n '__fish_accudoc_using_command site' -l title -d 'Site title' -r
complete -c accudoc -n '__fish_accudoc_using_command site' -l no-search -d 'Disable search functionality'

complete -c accudoc_cli.py -n '__fish_accudoc_using_command site' -s o -l output -d 'Output directory' -r
complete -c accudoc_cli.py -n '__fish_accudoc_using_command site' -l theme -d 'Site theme' -xa 'default dark minimal'
complete -c accudoc_cli.py -n '__fish_accudoc_using_command site' -l title -d 'Site title' -r
complete -c accudoc_cli.py -n '__fish_accudoc_using_command site' -l no-search -d 'Disable search functionality'

# branch-compare command options
complete -c accudoc -n '__fish_accudoc_using_command branch-compare' -s b -l base -d 'Base branch' -r
complete -c accudoc -n '__fish_accudoc_using_command branch-compare' -s c -l compare -d 'Compare branch' -r
complete -c accudoc -n '__fish_accudoc_using_command branch-compare' -s o -l output -d 'Output file' -r
complete -c accudoc -n '__fish_accudoc_using_command branch-compare' -s f -l format -d 'Output format' -xa 'markdown json'
complete -c accudoc -n '__fish_accudoc_using_command branch-compare' -s l -l list -d 'List available branches'

complete -c accudoc_cli.py -n '__fish_accudoc_using_command branch-compare' -s b -l base -d 'Base branch' -r
complete -c accudoc_cli.py -n '__fish_accudoc_using_command branch-compare' -s c -l compare -d 'Compare branch' -r
complete -c accudoc_cli.py -n '__fish_accudoc_using_command branch-compare' -s o -l output -d 'Output file' -r
complete -c accudoc_cli.py -n '__fish_accudoc_using_command branch-compare' -s f -l format -d 'Output format' -xa 'markdown json'
complete -c accudoc_cli.py -n '__fish_accudoc_using_command branch-compare' -s l -l list -d 'List available branches'

# dataflow command options
complete -c accudoc -n '__fish_accudoc_using_command dataflow' -s o -l output -d 'Output file' -r
complete -c accudoc -n '__fish_accudoc_using_command dataflow' -s f -l format -d 'Output format' -xa 'markdown json'
complete -c accudoc -n '__fish_accudoc_using_command dataflow' -l no-diagrams -d 'Exclude Mermaid diagrams'

complete -c accudoc_cli.py -n '__fish_accudoc_using_command dataflow' -s o -l output -d 'Output file' -r
complete -c accudoc_cli.py -n '__fish_accudoc_using_command dataflow' -s f -l format -d 'Output format' -xa 'markdown json'
complete -c accudoc_cli.py -n '__fish_accudoc_using_command dataflow' -l no-diagrams -d 'Exclude Mermaid diagrams'

# Generic options for analysis commands
set -l analysis_commands version-check spellcheck coverage readability db-schema monorepo breaking-changes code-quality grammar doc-coverage

for cmd in $analysis_commands
    complete -c accudoc -n "__fish_accudoc_using_command $cmd" -s o -l output -d 'Output file' -r
    complete -c accudoc -n "__fish_accudoc_using_command $cmd" -s f -l format -d 'Output format' -xa 'markdown json'
    
    complete -c accudoc_cli.py -n "__fish_accudoc_using_command $cmd" -s o -l output -d 'Output file' -r
    complete -c accudoc_cli.py -n "__fish_accudoc_using_command $cmd" -s f -l format -d 'Output format' -xa 'markdown json'
end
