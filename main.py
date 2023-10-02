from igzgModule import *
from PIL import Image, ImageDraw, ImageFont

class COLOR:
    BLACK      = (31,31,31,255)
    DEEPGRAY   = (36,36,36,255)
    GRAY       = (42,42,42,255)
    YELLOW     = (238,230,217,255)
    DEEPYELLOW = (211,188,141,255)
    BLANK      = (0,0,0,0)
    BRONZE = (127,115,92,255)
    DEEPBRONZE = (90,87,80,255)

class BoxDrawer:
    def __init__(self):
        self.image = ''

    def drawFixedSizeWrapper(self, image, size:tuple, pos:tuple, color:tuple):
        wrapper = Image.new("RGBA", size, color)
        wrapper.paste(image, pos, image)
        return wrapper
    
    def drawDynamicSizeWrapper(self, image, margin:tuple, color:tuple):
        size   = tuple(x + y for x, y in zip(image.size, margin))
        result = tuple(x //2 for x in margin)
        wrapper = Image.new("RGBA", size, color)
        wrapper.paste(image, result, image)
        return wrapper

    def drawRoundBorder(self, image, margin:tuple, borderWidth:int, color:tuple):
        pos = tuple(x - y for x, y in zip(image.size, margin))
        ImageDraw.Draw(image).rounded_rectangle([margin,pos], 10, fill=None, outline=color, width=borderWidth)
        return image

class BaseListImageMaker:
    def __init__(self):
        self.imagePathList = []
        self.imageList = []
        self.listImage = ''

    def setImagePathList(self, imagePathList):
        self.imagePathList = imagePathList
        return self
    
    def setImageList(self, imageList):
        self.imageList = imageList
        return self    
    
    def loadImages(self):
        self.imageList = [Image.open(x).convert('RGBA') for x in self.imagePathList]

    def initListImageX(self, offset:int=0):
        wishlistW = sum(x.width for x in self.imageList) + ((len(self.imageList)-1)*offset)
        wishlistH = max(x.height for x in self.imageList)
        self.listImage = Image.new('RGBA', (wishlistW, wishlistH), COLOR.BLANK )

    def initListImageY(self, offset:int=0):
        wishlistW = max(x.width for x in self.imageList)
        wishlistH = sum(x.height for x in self.imageList) + ((len(self.imageList)-1)*offset)
        self.listImage = Image.new('RGBA', (wishlistW, wishlistH), COLOR.BLANK )

    def pasteImagesX(self, offset:int=0):
        posX = 0
        for image in self.imageList:
            self.listImage.paste(image, (posX, 0), image)
            posX += (image.width + offset)

    def pasteImagesY(self, offset:int=0):
        posY = 0
        for image in self.imageList:
            self.listImage.paste(image, (0, posY), image)
            posY += (image.height + offset)            

class ListImageMaker(BaseListImageMaker):
    def makeResultlistImage(self):
        try:
            self.loadImages()
            self.imageList = [x.resize((300,300),Image.BICUBIC) for x in self.imageList]
            self.initListImageX(-60)
            self.pasteImagesX(-60)
        except ValueError:
            self.listImage = ''
        return self.listImage
    
    def makeWishlistImage(self):
        self.loadImages()
        self.initListImageX(15)
        self.pasteImagesX(15)
        return self.listImage
    
    def makeVersionImage(self):
        self.initListImageY(30)
        self.pasteImagesY(30)
        return self.listImage    

class VersionInfoMaker(BaseListImageMaker, BoxDrawer):
    def __init__(self):
        self.wishlistImage = self.VIH = self.rightBracket = self.leftBracket = ''
        self.resultlistImage = ''
        self.versionInfoImage = ''
        self.versionNumber = self.versionBackground = ''
        self.font = ImageFont.truetype("./.font/SuseongDotum.ttf", 80)
        
    def drawBrackets(self):
        corner_radius = 20
        width = 200
        brackets = Image.new("RGBA", (width, self.VIH), COLOR.BLANK )
        ImageDraw.Draw(brackets).rounded_rectangle([(0, 0), (width, self.VIH)], corner_radius, COLOR.YELLOW)

        self.versionBackground = Image.open(f'./Namecard_Background_/version/{self.versionNumber}.png').convert('RGBA')
        bgW, bgH = self.versionBackground.size
        bgi = self.versionBackground.resize((int(bgW * (self.VIH / bgH)), self.VIH), Image.ANTIALIAS)
        bgi = bgi.crop(((bgW - (width//2)) // 2, 0, (bgW + 3*(width//2)) // 2, self.VIH))
        brackets.paste(bgi, (0, 0), brackets)

        self.rightBracket = brackets.crop((width-corner_radius, 0, width, self.VIH))
        self.leftBracket  = brackets.crop((0, 0, width-corner_radius, self.VIH))

    def setWishlistImage(self,wishlistImage):
        self.wishlistImage = wishlistImage
        WW, WH = self.wishlistImage.size
        self.VIH = WH+40
        return self
    
    def setResultlistImage(self,resultlistImage):
        self.resultlistImage = resultlistImage
        return self
    
    def setVersionNumber(self, versionNumber):
        self.versionNumber = versionNumber
        self.drawBrackets()
        return self

    def drawWishlistBox(self):
        self.wishlistImage = self.drawDynamicSizeWrapper(self.wishlistImage,(60,40),COLOR.BLACK)
        return self.wishlistImage

    def drawResultlistBox(self):
        try:
            marginY = self.VIH - self.resultlistImage.height
            self.resultlistImage = self.drawDynamicSizeWrapper(self.resultlistImage, (60,marginY),COLOR.BLANK)
        except AttributeError:
            self.resultlistImage = Image.new("RGBA", (1, self.VIH), COLOR.BLANK )
        return self.resultlistImage

    def writeVersion(self):
        versionBoxDraw = ImageDraw.Draw(self.listImage)
        textWidth, textHeight = versionBoxDraw.textsize(self.versionNumber, self.font)
        textY = (self.VIH - textHeight) // 2
        versionBoxDraw.text((25, textY-10), self.versionNumber, COLOR.BLACK, self.font,stroke_width=10, stroke_fill=COLOR.YELLOW)
        
    def makeVersionInfoImage(self):
        self.imageList = [self.leftBracket, self.drawWishlistBox(),self.drawResultlistBox()]
        # if self.resultlistImage.width > 100: self.imageList.append(self.rightBracket)
        self.initListImageX()
        self.pasteImagesX()
        self.writeVersion()

        self.listImage = self.drawFixedSizeWrapper(self.listImage, (2230,410), (30,30), COLOR.DEEPGRAY)
        self.listImage = self.drawRoundBorder(self.listImage, (10,10),5,COLOR.DEEPBRONZE)
        self.versionInfoImage = self.listImage
        return self.versionInfoImage


class InputReader:
    def __init__(self):
        self.inputList = getFileInput('input.txt')
        self.wishData  = getJsonData('charWishlist.json')
        self.charDict  = {x.split('\t')[0].strip().replace(' ','_'):[ y.strip().replace(': ','_').replace(' ','_') for y in x.split('\t')[1:]] for x in getFileInput("charDict") if x[0] != '#'}
        
        self.itemFolderPath = "./_Item/"
        self.cardFolderPath = "./_Card/"

    def getCardPathList(self,versionNumber:str):
        targetWishlist= next((x['wishlist'] for x in self.wishData['wishlists'] if x['version_number'] == versionNumber), [])
        nameList = [x for phase in targetWishlist for x in (targetWishlist[phase] + (['x'] *(2 - len(targetWishlist[phase]))))]

        return [self.getCardFilePath(x) for x in nameList]

    def getCardFilePath(self,name):
        if name == 'x':
            cardFilePath = self.cardFolderPath + 'x'+ "_Card.png"
        else: 
            cardFilePath = self.cardFolderPath + self.charDict[name][0] + "_Card.png"
        return cardFilePath.replace(' ','_')

    def getItemPathList(self,nameList:list):
        return [(self.itemFolderPath + self.charDict[x][0] + "_Item.png").replace(' ','_') for x in nameList]


if __name__ == "__main__":
    inputReader      = InputReader()
    listImageMaker   = ListImageMaker()
    versionInfoMaker = VersionInfoMaker()
    totalCnt = len(inputReader.inputList)

    temp = []
    for idx,inputLine in enumerate(inputReader.inputList,start=1):
        versionNumber, *wishResult = inputLine.split('\t')
        strongPrint(f" [{idx}/{totalCnt}] {versionNumber} ")

        cardPathList     = inputReader.getCardPathList(versionNumber)
        itemPathList     = inputReader.getItemPathList(wishResult)

        wishlistImage   = listImageMaker.setImagePathList(cardPathList).makeWishlistImage()
        resultlistImage = listImageMaker.setImagePathList(itemPathList).makeResultlistImage()
        versionInfoMaker.setWishlistImage(wishlistImage).setResultlistImage(resultlistImage).setVersionNumber(versionNumber)
        versionImage = versionInfoMaker.makeVersionInfoImage()
        temp.append(versionImage)

    wishlistImage   = listImageMaker.setImageList(temp).makeVersionImage()

    resultImage = versionInfoMaker.drawDynamicSizeWrapper(wishlistImage,(200,200),COLOR.GRAY)
    resultImage = versionInfoMaker.drawRoundBorder(resultImage,(5,5),5,COLOR.BRONZE)
    resultImage = versionInfoMaker.drawDynamicSizeWrapper(resultImage,(100,100),COLOR.BLACK)
    W,H = resultImage.size
    resultImage = resultImage.resize((W//2,H//2),Image.BICUBIC)
    resultImage.save('res.png')
