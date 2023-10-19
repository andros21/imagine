``` imagine
                                          \\\///
                                         / _  _ \
                                       (| (.)(.) |)
                .--------------------.OOOo--()--oOOO.-------------------.
                |                                                       |
                |        ____                          _                |
                |       /  _/____ ___   ____ _ ____ _ (_)____   ___     |
                |       / / / __ `__ \ / __ `// __ `// // __ \ / _ \    |
                |     _/ / / / / / / // /_/ // /_/ // // / / //  __/    |
                |    /___//_/ /_/ /_/ \__,_/ \__, //_//_/ /_/ \___/     |
                |                           /____/                      |
                |                                                       |
                '-------------------.oooO-------------------------------'
                                     (   )   Oooo.
                                      \ (    (   )
                                       \_)    ) /
                                             (_/
```

## A pandoc filter to process codeblocks

<a href="https://github.com/andros21/imagine/actions/workflows/ci.yml">
<img src="https://img.shields.io/github/actions/workflow/status/andros21/imagine/ci.yml?branch=master&label=ci&logo=github" alt="ci"></a>
<a href="https://github.com/andros21/imagine/actions/workflows/cd.yml">
<img src="https://img.shields.io/github/actions/workflow/status/andros21/imagine/cd.yml?label=cd&logo=github" alt="cd"></a>
<a href="https://github.com/andros21/imagine/tags">
<img src="https://img.shields.io/github/v/tag/andros21/imagine?color=blue&label=tag&sort=semver&logo=github" alt="tag"></a>
<br><br>

Imagine is a pandoc filter that will turn codeblocks tagged with certain
classes into images

The following class are currently supported to render code blocks in
images:

- [**Gnuplot**](#gnuplot)
- [**Graphviz**](#graphviz)
- [**Plantuml**](#plantuml)
- [**Matplotlib**](#matplotlib)

If not supported class is specified in the codeblock, by default
`imagine` it replicates the codeblock and in case `pandoc -t latex` it
converts it in a
[`minted`](https://www.overleaf.com/learn/latex/Code_Highlighting_with_minted)
codeblock (syntax highlight on!)

> [!IMPORTANT]
> Refer to [`minted`](https://ctan.org/pkg/minted)
> documentation for supported languages

> [!WARNING]
> Supported `pandoc` API versions 1.23

### Examples

#### [Gnuplot](http://www.gnuplot.info)

<figure>
<img src="pd-images/976d41ce35f0d61505511ecf3c454b1f75fe8bf7.png" />
</figure>

#### [Graphviz](https://graphviz.org/)

<figure>
<img src="pd-images/930b097432ed038af41e415da8d22b02e0e4083b.png" />
</figure>

#### [Plantuml](https://plantuml.com/)

<figure>
<img src="pd-images/efbf3d7478a6c494bedbbebe16f56f972d775373.png" />
</figure>

#### [Matplotlib](https://matplotlib.org/)

<figure>
<img src="pd-images/d3edd7513770418f05b32336802f65db82e91485.png" />
</figure>
