# 0.3.0 - andros21
- add `pandoc_minted.py` script to parse minted code blocks
  and generate correct tex to include
- improve condition logic for caption and label attributes
- `im_fmt==tex` available in `matplotlib` that include(input) the image as latex code
  using 'pgf' backend matplotlib to generate pgfplots

# 0.2.0 - andros21
- new `im_fmt==tex` in `gnuplot` that include(input) the image as latex code
- new plot tool `matplotlib`
- reformat python source code (using `black` and `isort`)

# 0.1.7 - hertogp
- new `im_merge` option for a `Div` element
    + See feature request at https://github.com/hertogp/imagine/issues/16
    + *merges* `Image` elements of subsequent `CodeBlocks` into a single `Para`
    + See Examples/inline.md and Examples/inline.pdf

- new `ocb` directive for the `im_out` option
    + retain original code block but without imagine class/options
    + with imagine removed, codeblock is formatted along any remaining class
      language.  Example:
      ```{.shebang .lua im_out=ocb,stdout}
      #!/usr/bin/env lua
      print("here is stdout")
      ```
      `ocb` retains the codeblock but removes `.shebang` and `im_out`, so the
      code block is rendered as lua-code.  `stdout` adds another codeblock with
      stdout seen and with `lua` as its class.


# 0.1.6 - hertogp

- options resolved in this order (using gle and im_fmt as an example):
    + by codeblock attributes     {.gle im_fmt="svg"}
    + by klass specific metadata  imagine.gle.im_fm: svg
    + by imagine metadata         imagine.gle.im_fmt: svg
    + by imagine code             im_fmt = 'png' (on Handler parent class)

- added options:
    + `im_dir` to set path to store input/output files
    + `im_log` to set level of verbosity during processing

- removed output format limitations/checks (mostly)
    + `im_fmt` is whatever you want it to be, beware.
    + now, its possible to whatever output format a cli-tool produces

- broke large sample.md into examples per utility
    + allows for easier testing
    + see examples/Makefile
    + could not test octave due to bug in libosmesa6
    + pyxplot was not tested
      (not an apt-get pkg under bionic, manual install is required)


# 0.1.5 - hertogp

- renamed options to `im_<xxx>` to reduce possibility for namespace conflicts:
    + `im_out=fcb,stdout,stderr,image`  specify what to output in which order
    + `im_opt="cli options"`            add these options on the command line
    + `im_prg=cli-command`              use this command (no derive by class)

- reduce footprint of filter
    + by default pandoc-imagine now removes all of its own classes
    + all other classes are retained when outputting an image or codeblock

- fixed some pylint warnings (len(sequence) for example...)

# 0.1.4 - hertogp

- `pay_the_pypir.awk` to fix README.rst for PYPI
    + fix .. code:: by removing any 'roles' which PYPI doesnt seem to like
    + make urls for images on github absolute

# 0.1.3 - hertogp

- code compatibility for PY2 and PY3

# 0.1.2 - hertogp

Still fiddlin' with PYPI
- added main() for upload


# 0.1.1 - hertogp

Tryin' to get PYPI render README properly
- _readme.md is now source to generate README.md and README.rst


# 0.1.0 - hertogp

Initial version

<!-- coding: utf-8, vim:set ft=pandoc: -->
