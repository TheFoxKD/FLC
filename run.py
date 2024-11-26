#!/usr/bin/env python3


if __name__ == "__main__":
    from os import environ
    from pathlib import Path
    from sys import base_prefix

    environ["TCL_LIBRARY"] = str(Path(base_prefix) / "lib" / "tcl8.6")
    environ["TK_LIBRARY"] = str(Path(base_prefix) / "lib" / "tk8.6")

    print(environ["TCL_LIBRARY"])
    print(environ["TK_LIBRARY"])
    from src.gui.windows.main_window import MainWindow

    app = MainWindow()
    app.mainloop()
