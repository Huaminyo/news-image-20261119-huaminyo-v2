#!/usr/bin/env python3
"""Copy the pre-rendered front page to the harness output directory.

Stdlib only: the entry image is rendered by build_newspaper.py during
development and committed as entry.png; this script just places it where
the harness expects it.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    os.makedirs("/output", exist_ok=True)
    shutil.copyfile(os.path.join(HERE, "entry.png"), "/output/entry.png")


if __name__ == "__main__":
    main()
