#!/usr/bin/env python
"""
Filter to wrap Pandoc's CodeBlocks into minted blocks when using latex.
Pandoc's `fence_code_attributes` can be used to provide:

- the language (first class)
- minted's argumentless options (following classes)
- minted's options with arguments (attributes)
see: https://gist.github.com/jepio/3ecaa6bba2a53ff74f2e
"""

from pandocfilters import RawBlock, toJSONFilter

TEMPLATE = r"""
\begin{{minted}}[{options}]{{{lang}}}
{cont}
\end{{minted}}
""".strip()


def latex(x):
    return RawBlock("latex", x)


def join_options(opts):
    return ",\n".join(opts)


def process_atts(kws):
    """Preprocess the attributes provided by pandoc - they come as a list of
    2-lists, convert to a list of strings"""
    return ["%s=%s" % (l, r) for l, r in kws]


def main():
    "main entry point"

    def mintedify(key, value, format_, meta):
        if key == "CodeBlock":
            (ident, classes, attributes), contents = value
            if format_ == "latex" and classes:
                language, *pos = classes
                atts = process_atts(attributes)
                return [
                    latex(
                        TEMPLATE.format(
                            lang=language,
                            options=join_options(pos + atts),
                            cont=contents,
                        )
                    )
                ]

    toJSONFilter(mintedify)


if __name__ == "__main__":
    main()
