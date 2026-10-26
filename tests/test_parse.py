import os
import unittest

from cc_probe.cli import parse_include_paths, parse_macros

MACROS_OUTPUT = """\
#define __VERSION__ "12.2.1 20230214"
#define __ARM_ARCH 7
#define __ARM_FEATURE_DSP 1
#define __thumb__ 1
#define __has_include(STR) __has_include__(STR)
#define __EMPTY
"""

VERBOSE_OUTPUT = """\
ignoring nonexistent directory "/usr/local/include/x86_64-linux-gnu"
#include "..." search starts here:
 /work/project/inc
#include <...> search starts here:
 /usr/lib/gcc/x86_64-linux-gnu/12/include
 /usr/local/include
 /usr/include/../include
 /Library/Frameworks (framework directory)
End of search list.
COMPILER_PATH=/usr/libexec/gcc/x86_64-linux-gnu/12/
"""


class ParseMacrosTest(unittest.TestCase):
    def test_object_like(self):
        macros = parse_macros(MACROS_OUTPUT)
        self.assertEqual(macros["__ARM_ARCH"], "7")
        self.assertEqual(macros["__VERSION__"], '"12.2.1 20230214"')

    def test_function_like_and_empty(self):
        macros = parse_macros(MACROS_OUTPUT)
        self.assertEqual(macros["__has_include(STR)"], "__has_include__(STR)")
        self.assertEqual(macros["__EMPTY"], "")


class ParseIncludePathsTest(unittest.TestCase):
    def test_sections(self):
        paths = parse_include_paths(VERBOSE_OUTPUT)
        self.assertEqual(paths["quote"], [os.path.normpath("/work/project/inc")])
        self.assertEqual(
            paths["system"],
            [
                os.path.normpath("/usr/lib/gcc/x86_64-linux-gnu/12/include"),
                os.path.normpath("/usr/local/include"),
                os.path.normpath("/usr/include"),
                os.path.normpath("/Library/Frameworks"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
