# grassplain

an (unserious) command line argument parser generator, for when argparse is too much and too slow

- [what are the features?](#what-are-the-features)
- [frequently questioned answers](#frequently-questioned-answers)
- [cool, how do i use it?](#cool-how-do-i-use-it)
- [could it be better?](#could-it-be-better)
- [what's the configuration file structure?](#whats-the-configuration-file-structure)
- [what's the licence?](#whats-the-licence)

## what are the features?

- uses a [toml file](example-meadow.toml) to define the arguments and options

- generates a single python file that you can use as a module or insert into your project \
  (note: insertion is not a feature)

- returns a [typed NamedTuple](https://docs.python.org/3/library/typing.html#typing.NamedTuple)
  with the parsed arguments

- supports what you'd expect for basic usage:
  - positional arguments
  - short and long options
  - flags/boolean options \
    (these are actually parsed into integers, e.g., `-v` is `1` and `-vvv` is `3`. ints in python
    are falsy-truthy so it's fine)
  - flag stacking \
    (e.g., `-abc value` is the same as `-a -b -c value`)
  - help and version flags
  - subcommands + `subcommand --help`
  - nested subcommands \
    (e.g., `subcommand subsubcommand --help`)

- **however,** grassplain does NOT know about your code, so you check for types after the fact

## frequently questioned answers:

- **but why?**

  argparse is slow... (enough so for my use case in which i still had to use python, ahem)  
  and if i was going to write a cli parser for a project, hell, why not make it a bit generic?

- **why toml?**

  for this use case it's pretty good, i'd say

- **why should i use it?**

  you probably shouldn't, but if you aren't doing anything too fancy and want an argument parser
  that is:
  
  - a) quick and dirty (see 'why should i NOT use it?')
  - b) ahead-of-time, so parsing starts when code execution starts

  this might ~just~ work for you

- **why should i NOT use it?**

  grassplain is neither fully featured, batteries including, nor battle tested. it exists for my
  own use case, and that's about it — i'm not trying to beat argparse, click, or typer. just doing
  my own thing (❁´◡`❁)

## cool, how do i use it?

1. install with `pip install grassplain` (or use pipx)

2. read the example file, understand it and modify it/create your own

3. run `grassplain path/to/your/config.toml > custom.py` to generate the parser

    for this example, let's use the following really basic config:

    ```toml
    [global.arguments.target]
    description = "witty example description here"
    ```

4. and do something like this in your code:

    ```python
    from ... import parse_args, Arguments
    import sys
    
    def _show_version() -> None:
       print("v0.16.7")
       sys.exit(0)

    # generated_parser.Behaviour is a typed NamedTuple
    args: Arguments = parse_args(sys.argv, version_function=_show_version)
    print(args.target)
    ```

    (remember to modify the import statement, and the _show_version function if needed)

5. et voilà :)

   ```text
   $ python example.py help
   usage: example.py [-h] [-v] TARGET
   
   positional arguments:
     TARGET    witty example description here
   
   global options:
     -h, --help     show this help message and exit
     -v, --version  show program's version number and exit

   $ python example.py "don't be sad. the time is coming. and then we'll rest."
   don't be sad. the time is coming. and then we'll rest.
   ```

## could it be better?

1. yeah, it's currently ~reeealllly~ naively written

2. i mean, this ~is~ an open source project (open an issue or a pull request)

3. the 'backend' is modular, so i don't know, eventually i (or you!) could write a variant that
   outputs zig or anything else

## what's the configuration file structure?

```toml
[meta]
description = "<description here>"
max_line_length = 80
min_description_padding = 12
max_description_padding = 25

[metas.extra]
"<header>" = "<body text>"

[global.arguments."<argument name>"]
description = "<description here>"
number_of = 1  # set to -1 for unlimited

[global.options."<option name>"]
description = "<description here>"
number_of = 1  # set to -1 for unlimited
default = ""  # when reading, if the value is empty, then the option was not set

[global.flags."<long flag name>"]
short = "<short flag character>"
description = "<description here>"
default = 1

[subcommands."<subcommand name>"]
description = "<description here>"

# defined just like their global counterparts
[subcommands."<subcommand name>".arguments."<option name>"]
[subcommands."<subcommand name>".options."<option name>"]
[subcommands."<subcommand name>".flags."<option name>"]

# subcommands can have subcommands
[subcommands."<subcommand name>".subcommands."<subcommand name>"]
description = "<description here>"
```

## what's the licence?

- source code:
    ```text
    This is free and unencumbered software released into the public domain.

    Anyone is free to copy, modify, publish, use, compile, sell, or
    distribute this software, either in source code form or as a compiled
    binary, for any purpose, commercial or non-commercial, and by any
    means.
    
    In jurisdictions that recognize copyright laws, the author or authors
    of this software dedicate any and all copyright interest in the
    software to the public domain. We make this dedication for the benefit
    of the public at large and to the detriment of our heirs and
    successors. We intend this dedication to be an overt act of
    relinquishment in perpetuity of all present and future rights to this
    software under copyright law.
    
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
    IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
    OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
    OTHER DEALINGS IN THE SOFTWARE.
    
    For more information, please refer to <http://unlicense.org/>
    ```

- outputted code: \
    same as the source codes' licence (basically none, go ham)
