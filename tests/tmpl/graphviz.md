```{.graphviz im_out="${im_out}"${if(im_fmt)} im_fmt="${im_fmt}"${endif}${if(caption)} caption="${caption}"${endif}${if(label)} #${label}${endif}}
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
