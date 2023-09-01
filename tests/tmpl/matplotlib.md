```{.matplotlib im_out="${im_out}"${if(im_fmt)} im_fmt="${im_fmt}"${endif}${if(caption)} caption="${caption}"${endif}${if(label)} #${label}${endif}${if(minted_flags)} ${minted_flags}${endif}}
x = np.linspace(-20, 20, 500)
V = np.sin(x)/x

fig, ax = plt.subplots(figsize=(6,4))
ax.plot(x, V, 'r', label="sinc(x)")

ax.set_xlabel('x')
ax.set_ylabel('y')
ax.legend()
```
