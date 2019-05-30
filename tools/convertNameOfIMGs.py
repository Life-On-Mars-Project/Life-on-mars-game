from PIL import Image
import glob, os



for i,infile in enumerate(glob.glob('*.png')):   #("*.png"):
    file, ext = os.path.splitext(infile)
    im = Image.open(infile)
    file = 'Jump' + str(i)
    print('im saved', file)
    im.save(file + ".png", "PNG")
    os.remove(infile)
