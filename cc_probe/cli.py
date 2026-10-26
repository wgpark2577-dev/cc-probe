"""cc-probe: ask a GCC-family compiler for its builtin macros and include paths."""

import argparse
import json
import os
import re
import subprocess
import sys

DEFINE_RE = re.compile(r"#define\s+(\w+(?:\([^)]*\))?)\s?(.*)")


def run_preprocessor(compiler, flags, lang, extra):
    """Preprocess an empty input with the given compiler and flags."""
    cmd = [compiler, *flags, "-E", "-x", lang, *extra, "-"]
    result = subprocess.run(cmd, input="", capture_output=True, text=True, errors="replace")
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(cmd)}\n{result.stderr.strip()}")
    return result


def parse_macros(text):
    """Parse `-dM -E` output into {name: value}."""
    macros = {}
    for line in text.splitlines():
        m = DEFINE_RE.match(line)
        if m:
            macros[m.group(1)] = m.group(2)
    return macros


def parse_include_paths(text):
    """Parse `-v` output into quote ("...") and system (<...>) include paths."""
    paths = {"quote": [], "system": []}
    section = None
    for line in text.splitlines():
        if line.startswith('#include "..." search starts here:'):
            section = "quote"
        elif line.startswith("#include <...> search starts here:"):
            section = "system"
        elif line.startswith("End of search list."):
            break
        elif section and line.startswith(" "):
            path = line.strip().removesuffix(" (framework directory)")
            paths[section].append(os.path.normpath(path))
    return paths


def probe(compiler, flags, lang="c"):
    macros = parse_macros(run_preprocessor(compiler, flags, lang, ["-dM"]).stdout)
    includes = parse_include_paths(run_preprocessor(compiler, flags, lang, ["-v"]).stderr)
    return {
        "compiler": compiler,
        "flags": flags,
        "lang": lang,
        "version": macros.get("__VERSION__", "").strip('"'),
        "include_paths": includes,
        "macros": macros,
    }


def print_report(info):
    print(f"Compiler : {info['compiler']} {' '.join(info['flags'])}".rstrip())
    print(f"Language : {info['lang']}")
    print(f"Version  : {info['version'] or '(unknown)'}")
    for kind in ("quote", "system"):
        paths = info["include_paths"][kind]
        if paths:
            print(f"\nInclude paths ({kind}, {len(paths)}):")
            for p in paths:
                print(f"  {p}")
    print(f"\nMacros ({len(info['macros'])}):")
    for name, value in sorted(info["macros"].items()):
        print(f"  #define {name} {value}".rstrip())


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="cc-probe",
        description="Show the builtin macros and include paths of a GCC-family compiler.",
        epilog="example: cc-probe arm-none-eabi-gcc -mcpu=cortex-m4 -mthumb",
    )
    parser.add_argument("--lang", choices=["c", "c++"], default="c", help="source language (default: c)")
    parser.add_argument("--json", action="store_true", help="print the result as JSON")
    parser.add_argument("compiler", help="compiler executable, e.g. gcc or arm-none-eabi-gcc")
    parser.add_argument("flags", nargs=argparse.REMAINDER, help="target flags such as -mcpu=... -std=...")
    args = parser.parse_args(argv)

    try:
        info = probe(args.compiler, args.flags, args.lang)
    except FileNotFoundError:
        sys.exit(f"cc-probe: compiler not found: {args.compiler}")
    except RuntimeError as e:
        sys.exit(f"cc-probe: {e}")

    if args.json:
        print(json.dumps(info, indent=2, ensure_ascii=False))
    else:
        print_report(info)


if __name__ == "__main__":
    main()
