import os, imagescaling, platform, filetree, filerenderer, threading, queue
from pygame import *
import time

def listify_directory(directory):
    '''
    Turns the contents of a directory into a list with the full file path
    '''
    rootOut = filetree.TreeNode()
    rootOut.add_file(directory.replace('\\','/').split('/'))
    for directory in os.walk(directory):
        for file in directory[2]:
            filePath = (directory[0]+'/'+file).replace('\\','/')
            rootOut.add_file(filePath.split('/'))
    return rootOut

def find_difference(directory1, directory2):
    '''
    returns all the directories of directory2 including and after the first difference between
    directory2 and directory1
    '''

    for i in range(min(len(directory1), len(directory2))):
        if directory1[i] != directory2[i]:
            return directory2[i:]
    return directory2[min(len(directory1), len(directory2)):]

def DirectoryRenderer(render_directory, screen_width :int, max_line_height :int, file_indent_width :int, draw_font :font.Font, fRenderer :filerenderer.FileRenderer):
    '''
        returns a horizontal element of the screen for use when scrolling through all files in a directory
    '''
    while True:
        outSurf = Surface((screen_width, max_line_height))
        imageX = 0 #added to the depth offset
        cleaned_directory = render_directory.replace('\\','/')
    
        files= listify_directory(cleaned_directory)

        last_directory = []
         
        for i in filetree.TreeTraveller(files):
            depth, directory_path, fileName = i
            if directory_path != last_directory:
                #yield last row that was being worked on
                yield outSurf
                imageX = 0
                outSurf = Surface((screen_width, max_line_height))
                
                #render just the new path if the current path changed
                path_difference = '/'.join(find_difference(last_directory, directory_path))
                if depth>0:
                    path_difference = '/'+path_difference
                render_path = draw_font.render(path_difference, True, (255, 255, 255))
                
                labelSurf = Surface((screen_width, render_path.get_height()))
                labelSurf.blit(render_path, (depth*file_indent_width, 0)) # subtract 1 from the depth because a new directory should be printed on the same lines as an old directory
                yield labelSurf
                last_directory = directory_path

                
            
            full_path = '/'.join(directory_path)+'/'+fileName
            renderedFile = fRenderer.render_file(full_path)
            next_image_pos = (depth+1)*file_indent_width + imageX + 2
            if next_image_pos + renderedFile.get_width() > screen_width:
                yield outSurf
                imageX = 0
                outSurf = Surface((screen_width, max_line_height))
                next_image_pos = (depth+1)*file_indent_width + imageX + 2

            
            outSurf.blit(renderedFile, (next_image_pos, 0))
            imageX+=renderedFile.get_width()
        yield outSurf

def __ConcurrentDirectoryRendererProcess(directoryRenderer, queueOut, preload_amount):
    while True:
        if queueOut.qsize() < preload_amount:
            print('started rendering row... ', end='')
            start = time.time()
            nextElement = surfarray.pixels3d(next(directoryRenderer))
            print('done! %.2f seconds'%(time.time()-start))
            queueOut.put(nextElement, block=True)
        

def ConcurrentDirectoryRenderer(directoryRenderer, preload_amount = 5):
    queueIO = queue.Queue()

    threading.Thread(target=__ConcurrentDirectoryRendererProcess, args=(directoryRenderer, queueIO, preload_amount)).start()

    while True:
        yield surfarray.make_surface(queueIO.get())
