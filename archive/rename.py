import os

src = "z_image"
dest = "z_result"
i = 0
for path, subdirs, files in os.walk(src):
    for name in sorted(files):
        os.rename(os.path.join(path, name), os.path.join(dest, str(i) + '_' + name + '.jpg'))
        i = i+1
