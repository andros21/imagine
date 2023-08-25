```{.imagine im_out="ocb"}
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
<img src="https://img.shields.io/github/actions/workflow/status/andros21/imagine/ci.yml?branch=master&label=ci&logo=github" alt="ci">
</a>
<a href="https://github.com/andros21/imagine/actions/workflows/cd.yml">
<img src="https://img.shields.io/github/actions/workflow/status/andros21/imagine/cd.yml?label=cd&logo=github" alt="cd">
</a>
<a href="https://github.com/andros21/imagine/tags">
<img src="https://img.shields.io/github/v/tag/andros21/imagine?color=blue&label=tag&sort=semver&logo=github" alt="tag">
</a>
<br><br>

Imagine is a pandoc filter that will turn codeblocks tagged
with certain classes into images

The following class are currently supported to render
code blocks in images:

- [**Gnuplot**](#gnuplot)
- [**Graphviz**](#graphviz)
- [**Plantuml**](#plantuml)
- [**Matplotlib**](#matplotlib)

If not supported class is specified in the codeblock, by
default `imagine` it replicates the codeblock and in case
`pandoc -t latex` it converts it in a
[`minted`](https://www.overleaf.com/learn/latex/Code_Highlighting_with_minted)
codeblock (syntax highlight on!)

> [!IMPORTANT]
> Refer to [`minted`](https://ctan.org/pkg/minted) documentation for supported
> languages

> [!WARNING]
> Supported `pandoc` API versions 1.23

### Examples

#### [Gnuplot](http://www.gnuplot.info)

```{.gnuplot im_fmt="png" im_out="img"}
set dummy u,v
set key bmargin center horizontal Right noreverse enhanced autotitles nobox
set parametric
set view 50, 30, 1, 1
set isosamples 50, 20
set hidden3d back offset 1 trianglepattern 3 undefined 1 altdiagonal bentover
set ticslevel 0
set title "Interlocking Tori"
set urange [ -3.14159 : 3.14159 ] noreverse nowriteback
set vrange [ -3.14159 : 3.14159 ] noreverse nowriteback
splot cos(u)+.5*cos(u)*cos(v),sin(u)+.5*sin(u)*cos(v),.5*sin(v) with lines,\
1+cos(u)+.5*cos(u)*cos(v),.5*sin(v),sin(u)+.5*sin(u)*cos(v) with lines
```

#### [Graphviz](https://graphviz.org/)

```{.graphviz im_fmt="png" im_out="img"}
graph G {
   fontname="Helvetica,Arial,sans-serif"
   node [fontname="Helvetica,Arial,sans-serif"]
   edge [fontname="Helvetica,Arial,sans-serif"]
   layout=neato
   run -- intr;
   intr -- runbl;
   runbl -- run;
   run -- kernel;
   kernel -- zombie;
   kernel -- sleep;
   kernel -- runmem;
   sleep -- swap;
   swap -- runswap;
   runswap -- new;
   runswap -- runmem;
   new -- runmem;
   sleep -- runmem;
}
```

#### [Plantuml](https://plantuml.com/)

```{.plantuml im_fmt="png" im_out="img"}
@startuml
@startyaml
doe: "a deer, a female deer"
ray: "a drop of golden sun"
pi: 3.14159
xmas: true
french-hens: 3
calling-birds:
   - huey
   - dewey
   - louie
   - fred
xmas-fifth-day:
   calling-birds: four
   french-hens: 3
   golden-rings: 5
   partridges:
      count: 1
      location: "a pear tree"
   turtle-doves: two
@endyaml
```

#### [Matplotlib](https://matplotlib.org/)

```{.matplotlib im_fmt="png" im_out="img"}
x = np.linspace(-20, 20, 500)
V = np.sin(x)/x

fig, ax = plt.subplots(figsize=(6,4))
ax.plot(x, V, 'r', label="$sinc(x)$")

ax.set_xlabel('$x$')
ax.set_ylabel('$y$')
ax.legend()
```
