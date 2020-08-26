import cv2, imagescaling, pygame

imageFormats = {'jpg','png', 'gif','bmp','pcx', 'tga', 'tif', 'lbm', 'pbm', 'pgm', 'ppm', 'xpm'}
videoFormats = {'mp4', 'avi', 'mov'}
musicFormats = {'mp3', }
documentFormats = {'txt', 'docx', 'pdf', 'xlsx', 'pptx', 'py','jar','java','class', 'scad','stl','obj','gz', 'zip'}

musicIcon = pygame.image.load('music.png')
fileIcon = pygame.image.load('fileIconExtension.png')
playTriangle = pygame.Surface((10,10),pygame.SRCALPHA)
pygame.draw.polygon(playTriangle, (255,255,255, 140), ((0,0), (10,5), (0,10)))

class FileRenderer:
    def __init__(self, imageHeight, fileNameFont):
        self.imageHeight = imageHeight
        self.fileNameFont = fileNameFont

    def render_file(self, filepath):
        splittedFile = filepath.split('.')
        fileExt = splittedFile[-1].lower()

        if len(splittedFile) == 1: #no file extension, nothing to render
            return pygame.Surface((0, 0))
        
        if fileExt in imageFormats: #Image file
            try:
                filePic = pygame.image.load(filepath)
                preview = imagescaling.scale_to_height(filePic, self.imageHeight)
            except:
                print('an error occured while trying to display',filepath)
                filePic = self.render_error('Image Error')
                preview = imagescaling.scale_to_height(filePic, self.imageHeight)
            return preview
        elif fileExt in videoFormats: #Video File
            
            cap = cv2.VideoCapture(filepath)
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
            if convertSuccess:
                frameSurf = pygame.transform.flip(pygame.transform.rotate(pygame.surfarray.make_surface(frame),-90),True,False)
                preview = imagescaling.scale_to_height(frameSurf, self.imageHeight)
            else:
                print('an error occured while trying to display',filepath)
                preview = self.render_error('Video Error')
            preview.blit(playTriangle, (preview.get_width()//2-playTriangle.get_width()//2, preview.get_height()//2-playTriangle.get_height()//2))
            return preview
        elif fileExt in musicFormats: #Music file
            preview = imagescaling.scale_to_height(musicIcon,self.imageHeight)
            pygame.draw.circle(preview, (220, 220, 220), (5, 5), 5)
            return preview
        else: #Just render the file with its extension
            preview = imagescaling.scale_to_height(fileIcon, self.imageHeight)
            extensionLabel = self.fileNameFont.render('.'+fileExt,True,(0,0,0))
            preview.blit(extensionLabel, (4, 6))
            return preview
    def render_error(self, message):
        fontRender = self.fileNameFont.render(message, True, (0,0,0))
        frameSurf = pygame.Surface((fontRender.get_width()+20, 120))
        frameSurf.fill((255,0,0))
        frameSurf.blit(fontRender, (frameSurf.get_width()//2 - fontRender.get_width()//2, frameSurf.get_height()//2-fontRender.get_height()//2))
        preview = imagescaling.scale_to_height(frameSurf, self.imageHeight)
        return preview
