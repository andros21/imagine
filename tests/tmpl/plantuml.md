```{.plantuml im_out="${im_out}"${if(im_fmt)} im_fmt="${im_fmt}"${endif}${if(caption)} caption="${caption}"${endif}${if(label)} #${label}${endif}}
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
