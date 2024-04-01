# GitSleuth

A collection of git utilities, developed as I work on projects

## Requirements

* Python 3.10 or above

### Command Specific Requirements

* If using gitsleuth `trace-local` command, GraphViz must be installed on your system and the `dot` command must be on the PATH

## Installation

* Superuser priveleges required (user must be able to use sudo)
* `curl https://raw.githubusercontent.com/mikeandike523/gitsleuth/main/install.sh | bash`
   Warning! Although this installation method is common practice, there are security risks
   Consider downloading the install script first, examining it, and then executing it
* Some actions in the install script use `sudo` so you may be prompted to enter your password


## Usage

* `gitsleuth --help` - List available commands
* `gitsleuth <command> --help` - Get help with a specific command
* `gitsleuth <command> <arguments>` - Run a command with arguments

## Commands

* `trace-local`    - Create a git history trace of local repository and save to pdf
* `setup-tracking` - Automatically check out and setup tracking for any remote branches not already in the local repo
* `source-tree `   - Show the files that are included by git according to the structure of .gitignore files in the working tree
                   
                     Parameters:

                     `<DISPLAY_FORMAT>` (positional argument #1): "list" or "tree", either outputs a simple list of filenames, or displays them in a tree format
                     `--checklist` (optional flag): If this flag is added, each item in the list will prefixed by a checkbox using markdown syntax. Works only with DISPLAY_FORMAT of "list"
