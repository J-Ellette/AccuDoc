# AccuDoc Shell Completion Scripts

This directory contains shell completion scripts for the AccuDoc CLI, providing intelligent tab completion for commands, options, and file paths.

## Supported Shells

- **Bash** - Most common Unix shell
- **Zsh** - Modern shell with advanced features
- **Fish** - User-friendly shell with rich completions

## Features

- **Command Completion**: Tab completion for all AccuDoc commands
- **Option Completion**: Tab completion for command-specific options and flags
- **Smart Value Completion**: Context-aware completion for:
  - File formats (markdown, html, json, etc.)
  - Templates (default, minimal, detailed, api)
  - Themes (default, dark, minimal, corporate)
  - File paths (directories, .py files, .json files)
- **Help Text**: Descriptive help for each command and option

## Installation

### Bash

#### System-wide installation (requires root):
```bash
sudo cp completions/accudoc-completion.bash /etc/bash_completion.d/accudoc
```

#### User installation:
```bash
# Create completions directory if it doesn't exist
mkdir -p ~/.bash_completion.d

# Copy completion script
cp completions/accudoc-completion.bash ~/.bash_completion.d/accudoc

# Add to your ~/.bashrc
echo 'source ~/.bash_completion.d/accudoc' >> ~/.bashrc

# Reload your shell
source ~/.bashrc
```

### Zsh

#### System-wide installation (requires root):
```bash
sudo cp completions/_accudoc /usr/share/zsh/site-functions/_accudoc
```

#### User installation:
```bash
# Create completions directory if it doesn't exist
mkdir -p ~/.zsh/completions

# Copy completion script
cp completions/_accudoc ~/.zsh/completions/_accudoc

# Add to your ~/.zshrc (if not already there)
echo 'fpath=(~/.zsh/completions $fpath)' >> ~/.zshrc
echo 'autoload -U compinit && compinit' >> ~/.zshrc

# Reload your shell
source ~/.zshrc
```

### Fish

#### System-wide installation (requires root):
```bash
sudo cp completions/accudoc.fish /usr/share/fish/vendor_completions.d/accudoc.fish
```

#### User installation:
```bash
# Create completions directory if it doesn't exist
mkdir -p ~/.config/fish/completions

# Copy completion script
cp completions/accudoc.fish ~/.config/fish/completions/accudoc.fish

# Reload completions
fish -c 'fish_update_completions'
```

## Verification

After installation, verify that completions are working:

### Bash/Zsh
```bash
# Type the following and press TAB
accudoc_cli.py <TAB>

# Should show available commands
# Type partial command and press TAB
accudoc_cli.py da<TAB>

# Should complete to 'dataflow'
```

### Fish
```bash
# Type the following and press TAB
accudoc_cli.py <TAB>

# Should show available commands with descriptions
```

## Usage Examples

### Command Completion
```bash
# Type and press TAB to see all commands
$ accudoc_cli.py <TAB>
scan       generate   export     site       info       cache
check-links plugins   batch      dataflow   ...

# Type first letter(s) and TAB to autocomplete
$ accudoc_cli.py dat<TAB>
$ accudoc_cli.py dataflow
```

### Option Completion
```bash
# After a command, TAB shows available options
$ accudoc_cli.py dataflow <TAB>
-o  --output  -f  --format  --no-diagrams

# Option values are also completed
$ accudoc_cli.py dataflow --format <TAB>
markdown  json
```

### File Path Completion
```bash
# File paths are completed intelligently
$ accudoc_cli.py dataflow ~/pr<TAB>
$ accudoc_cli.py dataflow ~/projects/

# For batch command, only .json files are shown
$ accudoc_cli.py batch <TAB>
batch-example.json  config.json  ...
```

## Troubleshooting

### Bash Completions Not Working

1. **Check if bash-completion is installed:**
   ```bash
   # Ubuntu/Debian
   sudo apt install bash-completion
   
   # macOS (using Homebrew)
   brew install bash-completion
   ```

2. **Verify bash-completion is loaded:**
   ```bash
   # Should be in your ~/.bashrc or /etc/bash.bashrc
   if [ -f /etc/bash_completion ]; then
       . /etc/bash_completion
   fi
   ```

3. **Reload completions:**
   ```bash
   source ~/.bashrc
   # or
   exec bash
   ```

### Zsh Completions Not Working

1. **Check fpath:**
   ```bash
   echo $fpath
   # Should include your completions directory
   ```

2. **Rebuild completion cache:**
   ```bash
   rm -f ~/.zcompdump
   compinit
   ```

3. **Reload shell:**
   ```bash
   exec zsh
   ```

### Fish Completions Not Working

1. **Check completions path:**
   ```bash
   echo $fish_complete_path
   # Should include ~/.config/fish/completions
   ```

2. **Update completions:**
   ```bash
   fish_update_completions
   ```

3. **Reload shell:**
   ```bash
   exec fish
   ```

## Development

### Adding New Commands

When adding a new command to AccuDoc CLI, update all three completion scripts:

1. **Bash** (`accudoc-completion.bash`):
   - Add command to `commands` variable
   - Add case block for command-specific options

2. **Zsh** (`_accudoc`):
   - Add command to `_accudoc_commands` function
   - Create new function for command-specific completions

3. **Fish** (`accudoc.fish`):
   - Add command to the command list completions
   - Add command-specific option completions

### Testing Completions

After modifying completion scripts, test them:

```bash
# Bash
source completions/accudoc-completion.bash
accudoc_cli.py <TAB>

# Zsh
autoload -U compinit && compinit
_accudoc

# Fish
source completions/accudoc.fish
accudoc_cli.py <TAB>
```

## Contributing

If you find issues with completions or want to add support for more shells:

1. Test the existing completions thoroughly
2. Document any issues or improvements
3. Submit a pull request with your changes
4. Include examples of the improved behavior

## License

These completion scripts are part of AccuDoc and are released under the same license as the main project.

## Support

For issues with shell completions, please:
1. Check the troubleshooting section above
2. Verify your shell version and configuration
3. Open an issue on the AccuDoc GitHub repository with:
   - Your shell type and version
   - Installation method used
   - Error messages or unexpected behavior
   - Output of relevant diagnostic commands
