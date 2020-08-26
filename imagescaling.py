from pygame import Surface, transform

def scale_to_width(surfaceIn, width):
    '''
    resizes an image such that its width matches the given width
    '''
    ratio = surfaceIn.get_height()/surfaceIn.get_width()
    return transform.smoothscale(surfaceIn, (width, int(width*ratio)))

def scale_to_height(surfaceIn, height):
    '''
    resizes an image such that its height matches the given height
    '''
    ratio = surfaceIn.get_width()/surfaceIn.get_height()
    return transform.smoothscale(surfaceIn, (int(height*ratio), height))
