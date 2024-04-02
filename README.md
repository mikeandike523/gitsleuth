# GitSleuth

A collection of git utilities, developed as I work on projects

## Requirements

todo

### Command Specific Requirements

* If using gitsleuth `trace-local` command, GraphViz must be installed on your system and the `dot` command must be on the PATH

## Installation

todo


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
