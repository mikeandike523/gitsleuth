import os
from typing import Callable, List, Optional
from enum import Enum

from gitignore_parser import parse_gitignore


def is_child_of(potential_parent: str, potential_child: str) -> bool:
    # cheap way to do this
    norm_potential_parent = os.path.normpath(potential_parent)
    norm_potential_child = os.path.normpath(potential_child)
    return norm_potential_child.startswith(norm_potential_parent)


def get_is_ignored_checker(directory: str) -> Callable[[str], bool]:

    if not os.path.isabs(directory):
        raise Exception(f"Absolute paths are required for root directory")

    files = os.listdir(directory)
    # It is perfectly fine if there is no ".gitignore" file.
    # This just means that there are no files that are ignored
    if ".gitignore" not in files:
        return lambda _: False

    gitignore_path = os.path.join(directory, ".gitignore")

    # Oddly enough, the gitignore_parser library's `parse_gitignore` function returns a function that
    # takes in an absolute path, i.e. the location of the gitignore file is specified as an absolute path,
    # and for checking files, the absolute path of the file must be given

    matcher = parse_gitignore(gitignore_path)

    # If I recall correctly the gitignore_parser library throws an error when checking files that aren't relative to the root
    # In this case, lbyl design is appropriate and we should check relative paths first

    def checker(path: str) -> bool:

        basename = os.path.basename(path)

        if basename == ".git":
            return True

        if not os.path.isabs(path):
            raise Exception(f"Absolute paths are required for files being checked")

        if not is_child_of(directory, path):
            # Do not error here, rather return False since that is the intended behaviour of ".gitignore" files
            # Nevertheless, in general this should not occur
            return False

        return matcher(path)

    return checker


def get_ignore_checker_given_repo_root_and_containing_directory(
    repo_root_directory: str, directory: Optional[str] = None
) -> Callable[[str], bool]:
    """
    It is not sufficient to check if a file is ignored by the .gitignore in the same folder (sibling .gitignore)
    To truly see if a file is ignored, it is necessary to go up the chain of parents (stopping at the repo root)
    to see if it was ignored by some complex glob in the parent .gitignore
    """

    if not os.path.isabs(repo_root_directory):
        raise Exception(f"Absolute paths are required for root directory")

    if directory is None:
        return get_is_ignored_checker(repo_root_directory)

    if os.path.normpath(directory) == os.path.normpath(repo_root_directory):
        return get_is_ignored_checker(repo_root_directory)

    if not os.path.isabs(directory):
        raise Exception(f"Absolute paths are required for repo subdirectory")

    if not is_child_of(repo_root_directory, directory):
        raise Exception(
            "The subdirectory from which to establish a robust checker was not in the repo"
        )

    def combinator_boolean_or(
        callables: List[Callable[[str], bool]]
    ) -> Callable[[str], bool]:
        def boolean_or(path: str) -> bool:
            for callable in callables:
                if callable(path):
                    return True
            return False

        return boolean_or

    directory_list = []
    stop_directory = os.path.normpath(repo_root_directory)
    current_directory = os.path.normpath(directory)
    while current_directory != stop_directory:
        directory_list.append(current_directory)
        current_directory = os.path.dirname(current_directory)
    directory_list.append(stop_directory)

    return combinator_boolean_or(list(map(get_is_ignored_checker, directory_list)))


def get_robust_ignore_checker(repo_root_directory: str) -> Callable[[str], bool]:
    checker_cache = {}

    def make_checker(containing_directory_path: str) -> Callable[[str], bool]:
        if containing_directory_path in checker_cache:
            return checker_cache[containing_directory_path]
        checker = get_ignore_checker_given_repo_root_and_containing_directory(
            repo_root_directory, containing_directory_path
        )
        checker_cache[containing_directory_path] = checker
        return checker

    def check_file(path: str) -> bool:
        sub_checker = make_checker(os.path.dirname(path))
        return sub_checker(path)

    return check_file


class PathReturnMode(Enum):
    ABSOLUTE = "absolute"
    RELATIVE = "relative"


class CollectMode(Enum):
    INCLUDED = "included"
    EXCLUDED = "excluded"


def collect_included_or_excluded_files(
    repo_root_directory: str,
    collect_mode: CollectMode,
    path_return_mode: Optional[PathReturnMode] = PathReturnMode.RELATIVE,
) -> List[str]:
    checker = get_robust_ignore_checker(repo_root_directory)

    def should_skip(absolute_path: str) -> bool:
        return os.path.isdir(absolute_path) and checker(absolute_path)

    def should_collect(absolute_path: str) -> bool:
        return (not os.path.isdir(absolute_path)) and (
            checker(absolute_path)
            if collect_mode == CollectMode.EXCLUDED
            else not checker(absolute_path)
        )

    collected_relpaths = []

    def inner(preceding: List[str]):
        path_to_listdir = os.path.join(*([repo_root_directory] + preceding))
        items = os.listdir(path_to_listdir)
        for item in items:
            if item == ".git":
                continue
            item_path = os.path.join(path_to_listdir, item)
            if os.path.islink(item_path):
                name = os.path.join(*(preceding + [item]))
                target = os.readlink(item_path)
                base = os.path.normpath(repo_root_directory)
                if os.path.isabs(target):
                    if target.startswith(base):
                        target = os.path.relpath(target, repo_root_directory)
                else:
                    fp = os.path.normpath(os.path.join(path_to_listdir, target))
                    if fp.startswith(base):
                        fp = os.path.relpath(fp, repo_root_directory)
                        target = fp

                fullname = f"{name} -> {target if len(preceding) == 0 else ('/'.join(['..' for _ in preceding])+"/"+os.path.basename(target))}"
                collected_relpaths.append(fullname)
                continue
            if should_skip(item_path):
                if should_collect(item_path):
                    collected_relpaths.append(os.path.join(*(preceding + [item])))
                continue
            if os.path.isdir(item_path):
                inner(preceding + [item])
            else:
                if should_collect(item_path):
                    collected_relpaths.append(os.path.join(*(preceding + [item])))

    inner([])
    if path_return_mode == PathReturnMode.RELATIVE:
        return collected_relpaths
    return list(
        filter(
            lambda x: not len(x.strip()) == 0,
            map(
                lambda path: os.path.normalize(os.path.join(repo_root_directory, path)),
                collected_relpaths,
            ),
        )
    )


class RepoIgnoreChecker:
    """
    Neatly encapsulates gitignore patterns relative to a given repopsitory
    Technically, the repository does not need to be a true git repository, but it likely will be
    """

    def __init__(self, repo_root_directory: str):
        self.repo_root_directory = repo_root_directory
        self.robust_checker = get_robust_ignore_checker(repo_root_directory)

    # Want to be super explicit about how inputs are handled
    # A good name is worth a thousand words of docstring
    def check_abs_path(self, absolute_path: str) -> bool:
        if not is_child_of(self.repo_root_directory, absolute_path):
            return False  # This will be the same result as calling `self.robust_checker`, but will be faster
        if not os.path.isabs(absolute_path):
            raise Exception(f'Argument "{absolute_path}" is not an absolute path')
        return self.robust_checker(absolute_path)

    # Want to be super explicit about how inputs are handled
    # A good name is worth a thousand words of docstring
    def check_repo_relative_path(self, repo_relative_path: str) -> bool:
        if os.path.isabs(repo_relative_path):
            raise Exception(f'Argument "{repo_relative_path}" is not a relative path')
        absolute_path = os.path.join(self.repo_root_directory, repo_relative_path)
        return self.check_abs_path(absolute_path)

    def collect_included_files(
        self, return_mode: Optional[PathReturnMode] = PathReturnMode.RELATIVE
    ) -> List[str]:
        return collect_included_or_excluded_files(
            self.repo_root_directory, CollectMode.INCLUDED, return_mode
        )

    def collect_excluded_files(
        self, return_mode: Optional[PathReturnMode] = PathReturnMode.RELATIVE
    ) -> List[str]:
        return collect_included_or_excluded_files(
            self.repo_root_directory, CollectMode.EXCLUDED, return_mode
        )
