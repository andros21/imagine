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
\begin{{listing}}[!ht]
\begin{{minted}}[{options}]{{{lang}}}
{cont}
\end{{minted}}
{caption}
{label}
\end{{listing}}
""".strip()


def latex(x):
    return RawBlock("latex", x)


def join_options(opts):
    return ",\n".join(opts)


def process_atts(kws):
    """Preprocess the attributes provided by pandoc - they come as a list of
    2-lists, convert to a list of strings"""
    atts = {"caption": "", "label": "", "minted": []}
    for ll, rr in kws:
        if ll.lower() == "caption" or ll.lower() == "label":
            atts["%s" % ll] = "\\%s{%s}" % (ll, rr)
        else:
            atts["minted"].append("%s=%s" % (ll, rr))
    return atts


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
                            options=join_options(pos + atts["minted"]),
                            cont=contents,
                            caption=atts["caption"],
                            label=atts["label"],
                        )
                    )
                ]

    toJSONFilter(mintedify)


if __name__ == "__main__":
    main()
