#!/usr/bin/env python3
"""Luaroad - A modern Steam unlocker manager with Lua plugins.

This is the entry point for the Luaroad application.
"""

import sys
import os


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    from luaroad_app.app import LuaroadApp
    app = LuaroadApp()
    app.start()


if __name__ == "__main__":
    main()
