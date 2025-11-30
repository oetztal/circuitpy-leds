#!/usr/bin/env python3

import os
import pathlib
import shutil

target_path = "/Volumes/CIRCUITPY"
package_name =  "circuitpy_leds"

if __name__ == "__main__":
    main_code = os.path.join(target_path, "code.py")
    if os.path.exists(main_code):
        os.remove(main_code)

    src_path = pathlib.Path(__file__).parent.resolve()
    shutil.rmtree(os.path.join(target_path, "lib", package_name), ignore_errors=True)
    shutil.copytree(src_path / package_name, os.path.join(target_path, "lib", package_name))
    shutil.copyfile(src_path / "main.py", main_code)
