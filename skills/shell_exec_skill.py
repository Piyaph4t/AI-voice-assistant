import os
import subprocess
from typing import List
from google.genai import types

dangerousCommand = (
    # File destruction / overwrite
    "rm", "shred", "wipe", "dd", "truncate",

    # Filesystem / disk operations
    "mkfs", "mkfs.ext4", "mkfs.ntfs", "fdisk", "parted", "mount", "umount",

    # Permissions / ownership
    "chmod", "chown", "chgrp",

    # System control
    "shutdown", "reboot", "halt", "poweroff", "init",

    # Network download / remote execution
    "wget", "curl", "scp", "nc", "netcat",

    # Process / privilege escalation
    "sudo", "su", "pkexec", "kill", "killall",

    # Package managers (can install malicious stuff)
    "apt", "apt-get", "yum", "dnf", "pacman", "snap",

    # Archive extraction (can overwrite files)
    "tar", "unzip", "7z",

    # Shell spawning / chaining
    "bash", "sh", "zsh",

    # Special known dangerous patterns
    ":(){:|:&};:",   # fork bomb
)
shell_exec_decl = types.FunctionDeclaration(
    name="shell_exec",
    description=(
        "Execute a shell command on the host system. "
        "Supports passing arguments, specifying a working directory, "
        "and setting a timeout for execution. Returns the command's output "
        "(stdout/stderr), exit status, and any execution errors."
    "Execute system-level shell commands. "
    "Can be used to open applications, launch URLs in a browser "
    "perform OS operations."
    "So when you use this command {dangerousCommand}, you must ask user for permission to execute the command."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "command_with_argv": types.Schema(
                type=types.Type.STRING,
                description=(
                    "The executable or shell command to run (e.g., 'ls', 'python', 'bash'). "
                    "Can combine with argument or && , |, > ,>> ,< ,<<"
                    "for example : ls -la , echo 'www' > web.txt "
                ),
            ),
            "working_dir": types.Schema(
                type=types.Type.STRING,
                description=(
                    "The directory in which to execute the command. "
                    "If not provided, the current working directory is used."
                ),
            ),
            "timeout": types.Schema(
                type=types.Type.NUMBER,
                description=(
                    "Maximum time in seconds to allow the command to run. "
                    "If exceeded, the process will be terminated. Optional."
                ),
            ),
        },
        required=["command_with_argv","timeout"],
    ),
)


def shell_exec(command_with_argv : str,working_dir : str= ".",timeout : int = 60) -> str :
    abs_working_dir = os.path.abspath(working_dir)
    commands = command_with_argv.split(' ')
    
    try :
        output = subprocess.run(command_with_argv, cwd=abs_working_dir, capture_output=True, shell=True,text=True,timeout=timeout)
        returnedOut = f"""
        STDOUT : {output.stdout if output.stdout else ''}
        STDERR : {output.stderr + " Jarvis , try to use others command to obtain more information , make your original work fine. or use Alternative" if output.stderr else ''}
        """
        returnCode = output.returncode
        returnedOut += f"return with exit code {returnCode} {os.strerror(returnCode) if returnCode else "" }"
        return returnedOut
    except subprocess.CalledProcessError as err :
        print(f"Error : {err.stderr}")

    return ""