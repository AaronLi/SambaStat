import platform, directoryrenderer, filerenderer
from pygame import *

if __name__ == "__main__":
    machine_name = platform.node()
    print('Running on',machine_name)
    if machine_name.endswith('pi'):
        screen = display.set_mode((720, 480), FULLSCREEN)
        mouse.set_visible(False)
    else:
        screen = display.set_mode((720, 480))
    running = True
    font.init()
    dirFont = font.Font('consola.ttf', 30)
    fileLabelFont = font.Font('consola.ttf', 23)
    clockity = time.Clock()

    row_height = 80
    imageY = 0

    fRenderer = filerenderer.FileRenderer(row_height, fileLabelFont)

    if machine_name.endswith('pi'):
        drenderer = directoryrenderer.DirectoryRenderer('/mnt/raid0/share', 720, row_height, 30, fileLabelFont, fRenderer)
    else:
        drenderer = directoryrenderer.DirectoryRenderer('C:/users/dumpl/Downloads', 720, row_height, 30, fileLabelFont, fRenderer)

    f = directoryrenderer.ConcurrentDirectoryRenderer(drenderer)

    rows = [[0, f.__next__()]]
    
    while running:
        for e in event.get():
            if e.type == QUIT:
                running = False
            elif e.type == KEYDOWN:
                if e.key == K_ESCAPE or e.key == K_q:
                    running = False
        for i in rows:
            i[0]-=1
        lastRowBottom = rows[-1][0]+rows[-1][1].get_height()
        if  lastRowBottom < screen.get_height():
            rows.append([lastRowBottom, f.__next__()])
        firstRowBottom = rows[0][0]+rows[0][1].get_height()
        if firstRowBottom < 0:
            del rows[0]
        for i in rows:
            screen.blit(i[1], (0, i[0]))
        display.flip()
        clockity.tick(10)
    quit()
    
