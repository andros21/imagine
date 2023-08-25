package test

import future.keywords.if

default body := false
default capt := false
default labl := false
default pass := false

is_img {
   data.im_out == "img"
   data.im_fmt != "tex"
}
is_img_tex {
   data.im_out == "img"
   data.im_fmt == "tex"
}
is_mcb {
   data.im_out == "mcb"
}
is_ocb {
   data.im_out == "ocb"
}
has_capt {
   data.caption
}
not_has_capt {
   not data.caption
}
has_labl {
   data.label
}
not_has_labl {
   not data.label
}

img {
   array.slice(input.pandoc_api_version,0,2) == [1,23]
   type1 := input.blocks[0].t
   type1 == "Figure"
   content1 := input.blocks[0].c
   type2 := content1[2][0].t
   type2 == "Plain"
   content2 := content1[2][0].c
   type3 := content2[0].t
   type3 == "Image"
   content3 := content2[0].c
   startswith(content3[2][0], "pd-images")
   endswith(content3[2][0], data.im_fmt)
}
img_tex {
   array.slice(input.pandoc_api_version,0,2) == [1,23]
   type1 := input.blocks[0].t
   type1 == "Figure"
   content1 := input.blocks[0].c
   type2 := content1[2][0].t
   type2 == "Plain"
   content2 := content1[2][0].c
   type3 := content2[0].t
   type3 == "RawInline"
   content3 := content2[0].c
   content3[0] == "tex"
   startswith(content3[1], "\\input{pd-images/")
}
mcb {
   array.slice(input.pandoc_api_version,0,2) == [1,23]
   type := input.blocks[0].t
   type == "RawBlock"
   content := input.blocks[0].c[0]
   rawtex := input.blocks[0].c[1]
   content == "tex"
   startswith(rawtex, sprintf("\n\\begin{listing}[!ht]\n\\begin{minted}[%s]{%s}", [data.minted_flags, data.class]))
   regex.match("(.*)end{listing}(.*)", rawtex)
}
ocb {
   array.slice(input.pandoc_api_version,0,2) == [1,23]
   type := input.blocks[0].t
   type == "CodeBlock"
   content := input.blocks[0].c[1]
   content != ""
}

caption {
   content := input.blocks[0].c[0][2][0]
   content[0] == "caption"
   content[1] == data.caption
}
caption_tex {
   rawtex := input.blocks[0].c[1]
   regex.match(sprintf("(.*)caption{%s}(.*)", [data.caption]), rawtex)
}
label {
   content := input.blocks[0].c[0][0]
   content == data.label
}
label_tex {
   rawtex := input.blocks[0].c[1]
   regex.match(sprintf("(.*)label{%s}(.*)", [data.label]), rawtex)
}

body := img if { is_img } else
:= img_tex if { is_img_tex } else
:= mcb if { is_mcb } else
:= ocb if { is_ocb } else
:= false
capt := caption if { has_capt; not is_mcb } else
:= caption_tex if {has_capt; is_mcb } else
:= not_has_capt
labl := label if { has_labl; not is_mcb } else
:= label_tex if {has_labl; is_mcb } else
:= not_has_labl
pass := {"pass": true} if { body; capt; labl } else
:= {
      "body": body,
      "capt": capt,
      "labl": labl,
      "pass": false
}
