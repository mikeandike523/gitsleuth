# GitSleuth

A collection of git utilities, developed as I work on projects

## Requirements

* Python 3.10^
* virtualenv pip package `python -m pip install virtualenv`
* Graphviz

## Installation

1. `git clone https://github.com/mikeandike523/gitsleuth`
2. `cd gitsleuth`
3. `python -m virtualenv pyenv`
4. `call env.bat`
5. `python -m pip install -r requirements.txt`
6. Add the `gitsleuth` directory to the system path

## Usage

* `gitsleuth -h` - List available commands
* `gitsleuth <command> -h` - Get help with a specific command
* `gitsleuth <command> <arguments>` - Run a command with arguments

## Commands

*Use the `-h` flag in gitsleuth to view the command options*

*  `trace-local` - Create a git history trace of local repository and save to pdf
* `setup-tracking` - Automatically check out and setup tracking for any remote branches not already in the local repo
