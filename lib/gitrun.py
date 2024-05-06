import os
import shutil
import subprocess
import sys
import re

from lib.temporary_cwd import TemporaryCWD

def format_optional_bytes(bts):
    if bts is None:
        return None
    try:
        return bts.decode("utf-8")
    except:
        return f"(binary) hex={bts.hex()}"
    
class NoGitError(Exception):
    pass

def get_git_excutable():
    try:
        return shutil.which("git")
    except Exception as e:
        raise NoGitError(f"Could not get git executable: {str(e)}")

class GitrunError(Exception):

    def __init__(self, return_code, stdout, stderr):
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr
        super().__init__(f"""
GitrunError

Return Code: {return_code}
Stdout:
{format_optional_bytes(stdout)}
Stderr:
{format_optional_bytes(stderr)}
""")
        


def gitrun(args,cwd=None):
    if cwd is None:
        cwd=os.getcwd()
    git_executable = shutil.which("git")
    with TemporaryCWD(cwd):
        proc = subprocess.Popen([git_executable]+list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()

        if proc.returncode == 0:
            if stderr is not None:
                if len(stderr) > 0:
                    sys.stderr.write(format_optional_bytes(stderr))
            if stdout is None:
                return ""
            try:
                text = stdout.decode("utf-8")
                text = text.replace("\r\n","\n")
                text = text.strip()
                # text = re.sub(r"\n+","\n",text)
                return text
            except:
                raise Exception(f"Stdout was not valid text:\nhex={stdout.hex()}")
        else:
            raise GitrunError(proc.returncode,stdout,stderr)