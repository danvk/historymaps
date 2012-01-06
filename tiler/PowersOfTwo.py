# $Id: PowersOfTwo.py,v 1.3 2005/06/27 15:29:09 migurski Exp $

import math
from PIL import Image

chatty_default = False
efficient_default = True



def prepare(filename, chatty=chatty_default):
    """
    Prepare a large image for tiling.
    
    Load an image from a file. Resize the image so that it is square,
    with dimensions that are an even power of two in length (e.g. 512,
    1024, 2048, ...). Then, return it.
    """

    src = Image.open(filename)

    if chatty:
        print "original size: %s" % str(src.size)
    
    full_size = (1, 1)

    while full_size[0] < src.size[0] or full_size[1] < src.size[1]:
        full_size = (full_size[0] * 2, full_size[1] * 2)
    
    img = Image.new('RGBA', full_size)
    
    src.thumbnail(full_size, Image.ANTIALIAS)
    img.paste(src, (int((full_size[0] - src.size[0]) / 2), int((full_size[1] - src.size[1]) / 2)))
    
    if chatty:
        print "full size: %s" % str(full_size)
        
    return img



def tile(im, level, quadrant=(0, 0), size=(256, 256), efficient=efficient_default, chatty=chatty_default):
    """
    Extract a single tile from a larger image.
    
    Given an image, a zoom level (int), a quadrant (column, row tuple;
    ints), and an output size, crop and size a portion of the larger
    image. If the given zoom level would result in scaling the image up,
    throw an error - no need to create information where none exists.
    """

    scale = int(math.pow(2, level))
    
    if efficient:
        # efficient: crop out the area of interest first, then scale and copy it

        inverse_size    = (float(im.size[0]) / float(size[0] * scale),     float(im.size[1]) / float(size[1] * scale))
        top_left        = (int(quadrant[0] *  size[0] * inverse_size[0]),  int(quadrant[1] *  size[1] * inverse_size[1]))
        bottom_right    = (int(top_left[0] + (size[0] * inverse_size[0])), int(top_left[1] + (size[1] * inverse_size[1])))
    
        if inverse_size[0] < 1.0 or inverse_size[1] < 1.0:
            raise Exception('Requested zoom level (%d) is too high' % level)
    
        if chatty:
            print "crop(%s).resize(%s)" % (str(top_left + bottom_right), str(size))

        zoomed = im.crop(top_left + bottom_right).resize(size, Image.ANTIALIAS).copy()
        return zoomed

    else:
        # inefficient: copy the whole image, scale it and then crop out the area of interest

        new_size        = (size[0] * scale,         size[1] * scale)
        top_left        = (quadrant[0] * size[0],   quadrant[1] * size[1])
        bottom_right    = (top_left[0] + size[0],   top_left[1] + size[1])
        
        if new_size[0] > im.size[0] or new_size[1] > im.size[1]:
            raise Exception('Requested zoom level (%d) is too high' % level)
    
        if chatty:
            print "resize(%s).crop(%s)" % (str(new_size), str(top_left + bottom_right))

        zoomed = im.copy().resize(new_size, Image.ANTIALIAS).crop(top_left + bottom_right).copy()
        return zoomed



def subdivide(img, level=0, quadrant=(0, 0), size=(256, 256), filename='tile-%d-%d-%d.jpg'):
    """
    Recursively subdivide a large image into small tiles.

    Given an image, a zoom level (int), a quadrant (column, row tuple;
    ints), and an output size, cut the image into even quarters and
    recursively subdivide each, then generate a combined tile from the
    resulting subdivisions. If further subdivision would result in
    scaling the image up, use tile() to turn the image itself into a
    tile.
    """

    if img.size[0] <= size[0] * math.pow(2, level):

        # looks like we've reached the bottom - the image can't be
        # subdivided further. # extract a tile from the passed image.
        out_img = tile(img, level, quadrant=quadrant, size=size)
        out_img.save(filename % (level, quadrant[0], quadrant[1]))

        print '.', '  ' * level, filename % (level, quadrant[0], quadrant[1])
        return out_img

    # haven't reach the bottom.
    # subdivide deeper, construct the current image out of deeper images.
    out_img = Image.new('RGBA', (size[0] * 2, size[1] * 2))
    out_img.paste(subdivide(img, level=(level + 1), quadrant=((quadrant[0] * 2) + 0, (quadrant[1] * 2) + 0), filename=filename), (0,       0      ))
    out_img.paste(subdivide(img, level=(level + 1), quadrant=((quadrant[0] * 2) + 0, (quadrant[1] * 2) + 1), filename=filename), (0,       size[1]))
    out_img.paste(subdivide(img, level=(level + 1), quadrant=((quadrant[0] * 2) + 1, (quadrant[1] * 2) + 0), filename=filename), (size[0], 0      ))
    out_img.paste(subdivide(img, level=(level + 1), quadrant=((quadrant[0] * 2) + 1, (quadrant[1] * 2) + 1), filename=filename), (size[0], size[1]))

    out_img = out_img.resize(size, Image.ANTIALIAS)
    
    out_img.save(filename % (level, quadrant[0], quadrant[1]))

    print '-', '  ' * level, filename % (level, quadrant[0], quadrant[1])
    return out_img



if __name__ == '__main__':
    import sys
    
    img = prepare(sys.argv[-1], chatty=True)
    
    tile(img, 0, chatty=True).show()
    
    #tile(img, 1, quadrant=(0, 0), chatty=True).show()
    #tile(img, 1, quadrant=(1, 0), chatty=True).show()
    #tile(img, 1, quadrant=(0, 1), chatty=True).show()
    tile(img, 1, quadrant=(1, 1), chatty=True).show()
    
    #tile(img, 2, quadrant=(1, 1), chatty=True).show()
    #tile(img, 2, quadrant=(2, 1), chatty=True).show()
    #tile(img, 2, quadrant=(1, 2), chatty=True).show()
    tile(img, 2, quadrant=(2, 2), chatty=True).show()
    
    #tile(img, 3, quadrant=(3, 3), chatty=True).show()
    #tile(img, 3, quadrant=(4, 3), chatty=True).show()
    #tile(img, 3, quadrant=(3, 4), chatty=True).show()
    tile(img, 3, quadrant=(4, 4), chatty=True).show()
    
    #tile(img, 4, quadrant=(7, 7), chatty=True).show()
    #tile(img, 4, quadrant=(8, 7), chatty=True).show()
    #tile(img, 4, quadrant=(7, 8), chatty=True).show()
    tile(img, 4, quadrant=(8, 8), chatty=True).show()
    
    #tile(img, 4, quadrant=(15, 15), chatty=True).show()
    #tile(img, 4, quadrant=(16, 15), chatty=True).show()
    #tile(img, 4, quadrant=(15, 16), chatty=True).show()
    tile(img, 5, quadrant=(16, 16), chatty=True).show()

