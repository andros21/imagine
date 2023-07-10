#!/usr/bin/env python
# -*- coding: utf-8 -*-

import atexit
import hashlib
import os
import shutil
import sys
import tempfile
from subprocess import PIPE, CalledProcessError, Popen

import panflute as pf


def to_str(s, enc="ascii"):
    """Return encoded byte stream."""
    err = "replace"
    if isinstance(s, str):
        return s
    if isinstance(s, bytes):
        return s.decode(enc, err)
    try:
        return s.encode(enc, err)
    except AttributeError:
        return to_str(str(s))


def to_bytes(s, enc="ascii"):
    """Return decoded char sequence."""
    err = "replace"
    if isinstance(s, bytes):
        return s.encode(enc, err)

    if isinstance(s, str):
        return s.encode(enc, err)

    try:
        return to_bytes(str(s), sys.getdefaultencoding())
    except UnicodeEncodeError:
        return s.encode(enc, err)


def get_filename4code(module, content, ext=None):
    """
    Generate filename based on content.
    The function ensures that the (temporary) directory exists, so that the
    file can be written.
    By default, the directory won't be cleaned up,
    so a filter can use the directory as a cache and
    decide not to regenerate if there's no change.
    In case the user preferres the files to be temporary files,
    an environment variable `PANFLUTE_CLEANUP` can be set to
    any non-empty value such as `1` to
    make sure the directory is created in a temporary location and removed
    after finishing the filter. In this case there's no caching and files
    will be regenerated each time the filter is run.

    _Credits: [jgm/pandocfilters](https://github.com/jgm/pandocfilters)_
    """
    if os.getenv("PANFLUTE_CLEANUP"):
        imagedir = tempfile.mkdtemp(prefix=module)
        atexit.register(lambda: shutil.rmtree(imagedir))
    else:
        imagedir = module + "-images"
    fn = hashlib.sha1(content.encode(sys.getfilesystemencoding())).hexdigest()
    try:
        if not os.path.exists(imagedir):
            os.makedirs(imagedir)
            sys.stderr.write(f"Created directory {imagedir}\n")
    except OSError:
        sys.stderr.write(f"Could not create directory {imagedir}\n")
    if ext:
        fn += "." + ext
    return os.path.join(imagedir, fn)


class HandlerMeta(type):
    """Metaclass to register Handler subclasses (aka workers)."""

    def __init__(cls, name, bases, dct):
        """Register worker classes by cmdmap keys."""
        super(HandlerMeta, cls).__init__(name, bases, dct)
        for klass in dct.get("cmdmap", {}):
            cls.workers[klass.lower()] = cls


class Handler(object, metaclass=HandlerMeta):
    """Baseclass for image art generators."""

    severity = "error warn note info debug".split()
    workers = {}  # dispatch map for Handler, filled by HandlerMeta
    klass = None  # __call__ dispatches a worker & sets this
    meta = {}  # stores user prefs in doc's meta yaml block
    cmdmap = {}  # worker subclass overrides, klass->cli-program

    # Imagine defaults for worker options
    im_dir = "pd"  # dir for images (absolute or relative to cwd)
    im_fmt = "png"  # default format for image creation
    im_log = 0  # log on notification level
    im_opt = ""  # options to pass in to cli-program
    im_out = "img"  # what to output: csv-list img,mcb,ocb
    im_prg = None  # cli program to use to create graphic output

    # im_out is an ordered csv-list of what to produce:
    # - 'img'    outputs a link to an image (if any was produced)
    # - 'mcb'    the minted codeblock without imagine's class or options
    # - 'ocb'    the original codeblock without imagine's class or options

    def __call__(self, elem, doc):
        """Return worker class or self (Handler keeps CodeBlock unaltered)."""
        self.msg(4, "dispatch request for", elem)

        # get classes and keyvals from codeblock attributes
        try:
            klasses = elem.classes
        except Exception as e:
            self.msg(0, "Fatal: invalid codeblock passed in", elem)
            raise e

        # dispatching by class attribute
        for klass in klasses:
            worker = self.workers.get(klass.lower(), MintCodeBlock)
            worker.klass = klass.lower()
            self.msg(4, "- dispatched by class to", worker)
            return worker(elem, doc)

    def __init__(self, elem, doc):
        """Init by decoding the CodeBlock-s value."""
        self.elem = elem  # save original codeblock for later
        self.fmt = getattr(doc, "format", None)

        self.stdout = ""  # catches stdout by self.cmd, if any
        self.stderr = ""  # catches stderr by self.cmd, if any

        if elem is None:
            return  # initial dispatch creation

        # Options from to codeblock, meta data or imagine defaults
        cb = self.get_cb_opts(elem)  # codeblock attrs
        kd = self.get_md_opts(doc.metadata.content).get(
            self.klass, {}
        )  # metadata.klass
        md = self.md_opts  # metadata (toplevel)
        opts = [x for x in dir(self) if x.startswith("im_")]
        for opt in opts:
            # remove imagine related key from keyvals
            self.keyvals.pop(opt, None)
            val = cb.get(
                opt,  # 1 codeblock.opt
                kd.get(
                    opt,  # 2 imagine.klass.opt (meta)
                    md.get(opt, getattr(self, opt)),  # 3 imagine.opt (meta)
                ),
            )  # 4 class.opt (class's code)
            setattr(self, opt, val)

        # post-process options
        self.im_opt = self.im_opt.split()
        self.im_out = set(self.im_out.lower().replace(",", " ").split())
        self.im_log = int(self.im_log)

        if not self.im_prg:
            # if no im_prg was found, fallback to klass's cmdmap
            self.im_prg = self.cmdmap.get(self.klass, None)

        # not fail if 'im_prg' is empty, but convert the CodeBlock
        # in a syntax highlighted CodeBlock using 'minted',
        if self.im_prg is None and "img" in self.im_out:
            self.msg(
                1,
                self.klass,
                "not handled, by default substitute 'img' output type with 'mcb'",
            )
            self.im_out.remove("img")
            self.im_out.add("mcb")

        self.basename = get_filename4code(self.im_dir, str(elem))
        self.outfile = f"{self.basename}.{self.im_fmt}"
        self.inpfile = f"{self.basename}.{self.klass}"

        if not os.path.isfile(self.inpfile):
            self.write("w", self.code, self.inpfile)

    def get_md_opts(self, meta):
        """Pickup user preferences from meta block."""
        dct = {}
        try:
            sep = "."
            for k, v in meta.items():
                if not k.lower().startswith("imagine."):
                    continue
                if k.count(sep) == 1:
                    _, opt = k.split(sep)  # imagine.option: value
                    dct[opt] = pf.stringify(v)
                elif k.count(sep) == 2:
                    _, klass, opt = k.split(sep)  # imagine.klass.option: val
                    # klass = klass.lower()
                    if not dct.get(klass):
                        dct[klass] = {}
                    dct[klass][opt] = pf.stringify(v)

        except AttributeError:
            pass

        self.msg(4, "meta-data:", dct)
        self.md_opts = dct
        return dct

    def get_cb_opts(self, elem):
        """Pickup user preferences from code block."""
        # also removes imagine class/attributes from code block, by
        # retaining only non-Imagine stuff in self.classes and self.keyvals
        dct = {}
        opts = [x for x in dir(self) if x.startswith("im_")]

        self.id_ = elem.identifier
        self.classes = elem.classes
        self.keyvals = elem.attributes
        self.code = elem.text
        self.caption = pf.get_option(self.keyvals, "caption", default="")

        # remove all Imagine-related classes from codeblock attributes
        self.classes = [k for k in self.classes if k not in self.workers]

        for opt in opts:
            val = pf.get_option(self.keyvals, opt, error_on_none=False)
            if val:
                dct[opt] = val

        self.cb_opts = dct
        self.msg(4, "codeblock:", dct)
        return dct

    def read(self, mode, src):
        """Read a file with given mode or return empty string."""
        try:
            with open(src, mode) as f:
                return f.read()
        except (OSError, IOError) as e:
            self.msg(0, f"fail: could not read {src} ({repr(e)})")
            return ""
        return ""

    def write(self, mode, dta, dst):
        """Write a file, return success boolean indicator."""
        if not dta:
            self.msg(3, "skipped writing 0 bytes to", dst)
            return False
        try:
            with open(dst, mode) as f:
                f.write(dta)
            self.msg(3, "wrote:", len(dta), "bytes to", dst)
        except (OSError, IOError) as e:
            self.msg(0, "fail: could not write", len(dta), "bytes to", dst)
            self.msg(0, "exception:", e)
            return False
        return True

    def msg(self, level, *a):
        """Possibly print a message to stderr."""
        if level > self.im_log:
            return
        level %= len(self.severity)
        msg = "%s[%-9s:%5s] %s" % (
            "Imagine",
            self.__class__.__name__,
            self.severity[level],
            " ".join(to_str(s) for s in a),
        )
        print(msg, file=sys.stderr)
        sys.stderr.flush()

    def url(self):
        """Return an image link for existing/new output image-file."""
        # 'pf.Image' is an Inline element. Callers usually wrap it in a 'pf.Figure'
        # When {im_fmt} is 'tex' and pandoc fmt is 'latex'
        # return a pf.RawInline('latex') instead, wrapped in 'pf.Figure' too
        if self.im_fmt == "tex" and self.fmt == "latex":
            return pf.RawInline(f"\input{{{self.outfile[:-4]}}}", format="tex")
        else:
            return pf.Image(url=self.outfile)

    def minted_codeblock(self):
        """Syntax highlight original CodeBlock using minted."""
        keyvals = self.keyvals
        keyvals.pop("caption", None)
        keyvals = ",".join(f"{k}={v}" for k, v in keyvals.items())
        return pf.RawBlock(
            f"""
\\begin{{listing}}[!ht]
\\begin{{minted}}[{keyvals}]{{{self.klass}}}
{self.code}
\\end{{minted}}
\\caption{{{self.caption}}}
\\label{{{self.id_ if len(self.im_out) == 1 else f"mcb:{self.id_}"}}}
\\end{{listing}}
            """,
            format="tex",
        )

    def result(self):
        """Return Figure, minted CodeBlock or original CodeBlock as ordered."""
        rv = []
        for output_elm in self.im_out:
            if output_elm == "img":
                if os.path.isfile(self.outfile):
                    rv.append(
                        pf.Figure(
                            pf.Plain(self.url()),
                            caption=pf.Caption(*pf.convert_text(self.caption)),
                            identifier=self.id_
                            if len(self.im_out) == 1
                            else f"img:{self.id_}",
                            classes=self.classes,
                            attributes=self.keyvals,
                        )
                    )
                else:
                    msg = f"?? missing {self.outfile}"
                    self.msg(1, msg)
                    rv.append(pf.Para(pf.Str(msg)))

            elif output_elm == "mcb":
                if self.fmt == "latex":
                    rv.append(self.minted_codeblock())
                else:
                    rv.append(
                        pf.CodeBlock(
                            text=self.code,
                            identifier=self.id_
                            if len(self.im_out) == 1
                            else f"mcb:{self.id_}",
                            classes=self.classes,
                            attributes=self.keyvals,
                        )
                    )

            elif output_elm == "ocb":
                rv.append(
                    pf.CodeBlock(
                        text=self.code,
                        identifier=self.id_
                        if len(self.im_out) == 1
                        else f"ocb:{self.id_}",
                        classes=self.classes,
                        attributes=self.keyvals,
                    )
                )

        if not rv:
            return None  # no results; None keeps original codeblock
        if len(rv) > 1:
            return rv  # multiple results
        return rv[0]  # just 1 block level element

    def cmd(self, *args, **kwargs):
        """Run, possibly forced, a cmd and return success indicator."""
        forced = kwargs.get("forced", False)  # no need to pop
        stdin = kwargs.get("stdin", None)

        if os.path.isfile(self.outfile) and forced is False:
            self.msg(4, "re-use: {!r}".format(self.outfile))
            return True

        try:
            self.msg(4, "exec: ", *args)
            pipes = {
                "stdin": None if stdin is None else PIPE,
                "stdout": PIPE,
                "stderr": PIPE,
            }
            p = Popen(args, **pipes)

            out, err = p.communicate(to_bytes(stdin))
            self.stdout = out
            self.stderr = err

            # STDERR
            for line in self.stderr.splitlines():
                self.msg(4, "stderr>", line)

            self.msg(2, "stderr>", f"saw {len(self.stderr)} bytes")

            # STDOUT
            for line in self.stdout.splitlines():
                self.msg(4, "stdout>", line)

            self.msg(2, "stdout>", f"saw {len(self.stdout)} bytes")

            if os.path.isfile(self.outfile):
                # Note: not every worker actually produces an output file
                # e.g. because it captures stdout into a fenced codeblock
                # which is added to the document's AST
                self.msg(4, "created: {!r}".format(self.outfile))

            return p.returncode == 0

        except (OSError, CalledProcessError) as e:
            try:
                os.remove(self.outfile)
            except OSError:
                pass
            self.msg(1, "fail:", *args)
            self.msg(1, "msg:", self.im_prg, str(e))
            return False

    def image(self):
        """Abstract method that must be implemented for each worker/class."""
        raise NotImplementedError("Please implement this method for a specific worker")


class MintCodeBlock(Handler):
    """
    Default worker when 'im_prg' is empty, so no class target.
    That means the CodeBlock will be syntax highlighted with 'minted'.
    """

    def image(self):
        """No output file will be created. Simply reqrite original block."""
        return self.result()


class GnuPlot(Handler):
    """
    sudo apt-get install gnuplot
    http://www.gnuplot.info
    notes:
    - graphic data is printed to stdout
    - exception, imagine adds the following lines to the top of the script
       set terminal {im_fmt}
       set output {outfile}
      only when {im_fmt} == 'tex'
    """

    cmdmap = {"gnuplot": "gnuplot"}

    def image(self):
        "gnuplot {im_opt} <fname>.gnuplot > <fname>.{im_fmt}"
        if "img" in self.im_out:
            # stdout captures the graphic image
            args = self.im_opt + [self.inpfile]
            code = self.code
            if self.im_fmt == "tex":
                code = f"set output '{self.outfile}'\n{self.code}"
            self.write("w", code, self.inpfile)
            if self.cmd(self.im_prg, *args):
                if self.stdout:
                    self.write("wb", self.stdout, self.outfile)
                return self.result()
        else:
            return self.result()


class Graphviz(Handler):
    """
    sudo apt-get install graphviz
    http://graphviz.org
    """

    progs = ["dot", "neato", "twopi", "circo", "fdp", "sfdp"]
    cmdmap = dict(zip(progs, progs))
    cmdmap["graphviz"] = "dot"
    im_fmt = "svg"  # override Handler's png default

    def image(self):
        "{im_prg} {im_opt} -T{im_fmt} <fname>.{im_prg} <fname>.{im_fmt}"

        if "img" in self.im_out:
            args = self.im_opt + [f"-T{self.im_fmt}", self.inpfile, "-o", self.outfile]

            if self.cmd(self.im_prg, *args):
                return self.result()
        else:
            return self.result()


class PlantUml(Handler):
    """
    sudo apt-get install plantuml
    http://plantuml.com
    """

    cmdmap = {"plantuml": "plantuml"}

    def image(self):
        "plantuml -t{im_fmt} <fname>.plantuml {im_opt}"

        if "img" in self.im_out:
            args = ["-t" + self.im_fmt, self.inpfile] + self.im_opt
            if self.cmd(self.im_prg, *args):
                return self.result()
        else:
            return self.result()


class Matplotlib(Handler):
    """
    sudo apt-get install python3-matplotlib
    https://matplotlib.org
    Note:
     - Imagine adds the following lines to the top of the script:
        import sys
        import numpy as np
        import matplotlib.pyplot as plt
       to import standard library needed for a matplotlib plot
     - Imagine adds the following lines to the bottom of the script:
        fig.savefig(sys.argv[-1])
       to save result with trasparent background with graphic format
     - Imagine adds the following lines to the bottom of the script:
        fig.savefig(sys.argv[-1], format='pgf', backend='pgf')
       to save result with trasparent background with tex format
    """

    cmdmap = {"matplotlib": "python3"}

    def image(self):
        "<fname>.matplotlib {im_opt} <fname>.{im_fmt}"
        if "img" in self.im_out:
            args = self.im_opt + [self.inpfile, self.outfile]
            code = f"""
import sys
import numpy as np
import matplotlib.pyplot as plt

{self.code}

{
"fig.savefig(sys.argv[-1])"
if self.im_fmt != "tex" else "fig.savefig(sys.argv[-1], format='pgf', backend='pgf')"
}
            """
            self.write("w", code, self.inpfile)
            if self.cmd(self.im_prg, *args):
                return self.result()
        else:
            return self.result()


def main():
    "Main entry point."

    def walker(elem, doc):
        "Walk down the pandoc AST and invoke workers for CodeBlocks."
        if isinstance(elem, pf.CodeBlock):
            return dispatch(elem, doc).image()

    dispatch = Handler(None, None)
    pf.toJSONFilter(walker)


if __name__ == "__main__":
    main()
