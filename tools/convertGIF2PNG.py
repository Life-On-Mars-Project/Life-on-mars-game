from PIL import Image
import glob, os



im = Image.open('transi.gif')

try:
    i = 0
    while True:
         im.save(str(i)+'.png', 'PNG')
         i += 1
         im.seek(im.tell()+1)
except EOFError:
    print('fini')
