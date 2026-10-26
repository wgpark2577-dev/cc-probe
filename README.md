# cc-probe

Ask a GCC-family compiler what it actually defines and where it looks for headers.

When you set up clangd, a static analyzer or a CI job for an embedded project, you need
the compiler's **builtin macros** (`__ARM_ARCH`, `__ARM_FEATURE_DSP`, ...) and its
**system include paths**. These change with target flags like `-mcpu`, so cc-probe runs
the compiler with your flags and reports both.

## Install

```bash
pip install .
```

## Usage

```bash
cc-probe arm-none-eabi-gcc -mcpu=cortex-m4 -mthumb
cc-probe --lang c++ arm-none-eabi-g++ -mcpu=cortex-m0plus -std=c++17
cc-probe --json gcc -O2 > gcc.json
```

Options (`--lang`, `--json`) go **before** the compiler; everything after the compiler is
passed to it as flags.

Example output:

```
Compiler : arm-none-eabi-gcc -mcpu=cortex-m4 -mthumb
Language : c
Version  : 12.2.1 20230214

Include paths (system, 3):
  ...\lib\gcc\arm-none-eabi\12.2.1\include
  ...\lib\gcc\arm-none-eabi\12.2.1\include-fixed
  ...\arm-none-eabi\include

Macros (419):
  #define __ARM_ARCH 7
  #define __ARM_FEATURE_DSP 1
  ...
```

## How it works

cc-probe runs two commands on an empty input:

```bash
<compiler> <flags> -E -x c -dM -   # builtin macros
<compiler> <flags> -E -x c -v  -   # include search paths (printed to stderr)
```

## Tests

```bash
python -m unittest discover tests
```

## License

MIT
