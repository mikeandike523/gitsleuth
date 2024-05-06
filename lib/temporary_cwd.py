import os

class TemporaryCWD:
    def __init__(self, new_cwd):
        self.new_cwd = os.path.realpath(new_cwd)
        self.old_cwd = None

    def __enter__(self):
        current_cwd = os.getcwd()
        if current_cwd == self.new_cwd:
            return  # Silently do nothing if cwd is already the new_cwd
        self.old_cwd = current_cwd
        os.chdir(self.new_cwd)

    def __exit__(self, exc_type, exc_value, traceback):
        if self.old_cwd is not None:
            os.chdir(self.old_cwd)