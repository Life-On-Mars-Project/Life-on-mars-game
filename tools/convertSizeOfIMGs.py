from PIL import Image
import glob, os



def divide_size_by_X(determinant, X, old_size=''):
    
    for infile in glob.glob(determinant):   #("*.png"):
        file, ext = os.path.splitext(infile)
        im = Image.open(infile)
        if im.size == old_size or old_size == '':
            new_im = Image.new('RGB', (im.size[0]//X, im.size[1]//X))
            px = im.load()
            new_px = new_im.load()
            new_size = new_im.size

            for ligne in range(new_size[0]-1):
                for colonne in range(new_size[1]-1):
                    new_px[ligne, colonne] = px[ligne*X,colonne*X]

            print('im saved')
            new_im.save(file + ".png", "PNG")
        else:
            print('pas bon fichier')


def crop_file_to_fit_image(determinant):
    
    for infile in glob.glob(determinant):
        file, ext = os.path.splitext(infile)
        im = Image.open(infile)
        px = im.load()
        px_ref = px[0,0]
        maxX, maxY, minX, minY = 0,0,im.size[0],im.size[1]

        for x in range(im.size[0]):
            for y in range(im.size[1]):
                if not(px[x,y] == px_ref):
                    if x > maxX:
                        maxX = x
                    if x < minX:
                        minX = x
                    if y > maxY:
                        maxY = y
                    if y < minY:
                        minY = y

        new_im = im.crop((minX,minY,maxX-minX,maxY-minY))
        print('im saved')
        new_im.save(file + ".png", "PNG")
                    
                    
                



























