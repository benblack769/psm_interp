import sys

SYS_NAME = sys.platform.lower()
def is_mac():
    return SYS_NAME == "darwin"
def is_windows():
    return SYS_NAME == "windows" or SYS_NAME == "win32"
def is_linux():
    return SYS_NAME == "linux" or SYS_NAME == "linux2"
def is_unix():
    return not is_windows()
"""Note that "gcc" on macs is not actually gcc but clang(with LLVM).
If you are using the actual gcc on your mac, or clang on a different
OS then you should change this.
"""
def is_gcc():
    return not is_mac()
