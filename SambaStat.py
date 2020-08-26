import numpy as np
import cv2, os, pprint, shutil, platform
import time as tm
from multiprocessing import Process
from pygame import *
from imagescaling import *
font.init()

computer_name = platform.node()

if computer_name == 'pi':
    rootDir = '/mnt/raid0/share'
    screen = display.set_mode((720,480),FULLSCREEN)
else:
    rootDir = '/10.204.60.228/share'
    screen = display.set_mode((720,480))
    
running = True
clockity = time.Clock()
lastCheck = 0
checkFreqSecs = 180
hideChar = '-'
previewHeight = 80
folderIndent = 40
scrollY = 0
fileIconHorizontalSpacing = 5
fileIconVerticalSpacing = 5
directoryLabelHeightSpace= 38

rootDir = rootDir[:-1] if rootDir[-1] == '/' else rootDir
showCenterOfVideo = True
mouse.set_visible(False)

imageFormats = {'jpg','png', 'gif','bmp','pcx', 'tga', 'tif', 'lbm', 'pbm', 'pgm', 'ppm', 'xpm'}
videoFormats = {'mp4', 'avi', 'mov'}
musicFormats = {'mp3', }
documentFormats = {'txt', 'docx', 'pdf', 'xlsx', 'pptx', 'py','jar','java','class', 'scad','stl','obj','gz', 'zip'}

dirFont = font.Font('consola.ttf', 30)
fileLabelFont = font.Font('consola.ttf', 24)


def numDifferences(list1, list2):
    shorterLength = min(len(list1), len(list2))
    longerLength = max(len(list1),len(list2))
    differences = longerLength-shorterLength
    for i in range(shorterLength):
        differences+=list1[i] != list2[i]
    return differences

def stringDif(baseString, longerString) -> str:
    '''
        returns the part of longerString that is not included in baseString
        longerString should be longer than baseString
    '''
    for i in range(len(baseString)):
        if baseString[i]!=longerString[i]:
            return longerString[i:]
    return longerString[i+1:]

fileIcon = scale_to_height(image.load('fileIconExtension.png').convert_alpha(), previewHeight)
musicIcon = scale_to_height(image.load('music.png').convert_alpha(), previewHeight)

playTriangle = Surface((10,10),SRCALPHA)
draw.polygon(playTriangle, (255,255,255, 140), ((0,0), (10,5), (0,10)))
picsDrawn= False

outSurf = Surface((720,480))

while running:
    for e in event.get():
        if e.type == QUIT:
            running = False
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE or e.key == K_q:
                running = False
    screen.fill((0,0,0))
    if tm.time()-lastCheck > checkFreqSecs:
        outSurf.fill((0,0,0))
        fileY = 5
        directorySize = 0
        fileDirectory = list(os.walk(rootDir))
        outSurf.blit(dirFont.render(rootDir, True, (255,255,255)), (5, fileY))
        for folder in fileDirectory:
            hideDirectory = False
            folder = (folder[0].replace('\\','/'),)+folder[1:]
            if any([i.startswith(hideChar) for i in folder[0].split('/')]):
                hideDirectory = True
            indent = folderIndent*(folder[0].count('/')-rootDir.count('/'))+5
            if fileY + directoryLabelHeightSpace > outSurf.get_height() and not hideDirectory:
                    tempSurf = Surface((720, outSurf.get_height()+480))
                    tempSurf.blit(outSurf, (0,0))
                    outSurf = tempSurf
                    print('extend')
            if not hideDirectory:
                outSurf.blit(dirFont.render(stringDif(rootDir, folder[0]), True, (255,255,255)), (indent, fileY))
                fileY += directoryLabelHeightSpace
                offsetX = 0
            picsDrawn = False
            for file in folder[2]:
                event.clear()
                filePath = folder[0]+'/'+file
                fileExt = filePath.split('.')[-1].lower()
                lastModified = os.path.getmtime(filePath)
                if file.startswith(hideChar) or hideDirectory:
                    print('hidden')
                    continue
                else:
                    print(filePath)
                if (fileExt in imageFormats) or (fileExt in videoFormats) or (fileExt in musicFormats) or (fileExt in documentFormats): #if the file is going to be drawn
                    if fileY + previewHeight + previewHeight//10 > outSurf.get_height(): # if the current surface is not large enough to support new files being drawn
                        tempSurf = Surface((720, outSurf.get_height()+480))
                        tempSurf.blit(outSurf, (0,0))
                        outSurf = tempSurf
                        print('extend')
                if fileExt in imageFormats: #Image file
                    filePic = image.load(filePath).convert_alpha()
                    preview = scale_to_height(filePic, previewHeight)
                    if indent+folderIndent+offsetX+preview.get_width() > outSurf.get_width()-10:
                        offsetX = 0
                        fileY += previewHeight + fileIconVerticalSpacing
                    outSurf.blit(preview, (indent+folderIndent+offsetX, fileY))
                    offsetX+=preview.get_width()+fileIconHorizontalSpacing
                    picsDrawn = True
                elif fileExt in videoFormats: #Video File
                    
                    cap = cv2.VideoCapture(filePath)
                    if showCenterOfVideo:
                        videoLength = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                        cap.set(cv2.CAP_PROP_POS_FRAMES, videoLength//2)
                    ret, frame = cap.read()
                    convertSuccess = True
                    try:
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    except cv2.error:
                        print("cvtColor Error")
                        convertSuccess = False
                    cap.release()
                    print(convertSuccess)
                    if convertSuccess:
                        frameSurf = transform.flip(transform.rotate(surfarray.make_surface(frame),-90),True,False)
                        preview = scale_to_height(frameSurf, previewHeight)
                    else:
                        fontRender = dirFont.render('Video Error', True, (0,0,0))
                        frameSurf = Surface((fontRender.get_width()+20, 120))
                        frameSurf.fill((255,0,0))
                        frameSurf.blit(fontRender, (frameSurf.get_width()//2 - fontRender.get_width()//2, frameSurf.get_height()//2-fontRender.get_height()//2))
                        preview = scale_to_height(frameSurf, previewHeight)
                    if indent+folderIndent+offsetX+preview.get_width() > outSurf.get_width()-10:
                        offsetX = 0
                        fileY += previewHeight + fileIconVerticalSpacing
                    preview.blit(playTriangle, (preview.get_width()//2-playTriangle.get_width()//2, preview.get_height()//2-playTriangle.get_height()//2))
                    outSurf.blit(preview, (indent+folderIndent+offsetX, fileY))
                    offsetX+=preview.get_width()+fileIconHorizontalSpacing
                    picsDrawn = True
                elif fileExt in musicFormats: #Music file
                    preview = musicIcon
                    if indent+folderIndent+offsetX+preview.get_width() > outSurf.get_width()-10:
                        offsetX = 0
                        fileY += previewHeight + fileIconVerticalSpacing
                    outSurf.blit(preview, (indent+folderIndent+offsetX, fileY))
                    draw.circle(outSurf, (220, 220, 220), (indent+folderIndent+offsetX+5, fileY+5), 5)
                    offsetX+=preview.get_width()+fileIconHorizontalSpacing
                    picsDrawn = True
                elif fileExt in documentFormats: #Document
                    preview = fileIcon
                    if indent+folderIndent+offsetX+preview.get_width() > outSurf.get_width()-10:
                        offsetX = 0
                        fileY += previewHeight + fileIconVerticalSpacing
                    outSurf.blit(preview, (indent+folderIndent+offsetX, fileY))
                    extensionLabel = fileLabelFont.render('.'+fileExt,True,(0,0,0))
                    outSurf.blit(extensionLabel, (indent+folderIndent+offsetX+3, fileY+6))
                    offsetX+=preview.get_width()+fileIconHorizontalSpacing
                    picsDrawn = True
                if picsDrawn:
                    screen.blit(outSurf,(0,0))
                    display.flip()
            if picsDrawn:
                fileY +=previewHeight + fileIconVerticalSpacing
        tempOut = Surface((720, fileY+(28 if picsDrawn else previewHeight + previewHeight//10)))
        tempOut.blit(outSurf, (0,0))
        outSurf= tempOut
        lastCheck = tm.time()
    else:
        screen.blit(outSurf, (0,int(scrollY)))
        timeRemaining = checkFreqSecs-(tm.time()-lastCheck)
        scrollY = -outSurf.get_height() * (tm.time()-lastCheck)/checkFreqSecs
        if computer_name == 'pi':
            diskData = shutil.disk_usage("/mnt/raid0")
            timeRender = dirFont.render('%.2f %.2fGB/%.2fGB'%(timeRemaining, (diskData.total-diskData.free)/1073741824, diskData.total/1073741824), True, (255,255,255), (0,0,0))
            timeRender.set_alpha(128)
            screen.blit(timeRender, (715-timeRender.get_width(),475-timeRender.get_height()))
    display.flip()
    clockity.tick(10)
quit()
