from igzgModule import *
from PIL import Image, ImageDraw, ImageFont
import os

class BaseListImageMaker:
    def __init__(self):
        self.imagePathList = []
        self.imageList = ''
        self.listImage = ''

    def setImagePathList(self, imagePathList):
        self.imagePathList = imagePathList
        return self
    
    def loadImages(self):
        self.imageList = [Image.open(x).convert('RGBA') for x in self.imagePathList]

    def initListImageX(self, offset:int=0):
        wishlistW = sum(x.width for x in self.imageList) + ((len(self.imageList)-1)*offset)
        wishlistH = max(x.height for x in self.imageList)
        self.listImage = Image.new('RGBA', (wishlistW, wishlistH), (0, 0, 0, 0))

    def initListImageY(self, offset:int=0):
        wishlistW = max(x.width for x in self.imageList)
        wishlistH = sum(x.height for x in self.imageList) + ((len(self.imageList)-1)*offset)
        self.listImage = Image.new('RGBA', (wishlistW, wishlistH), (0, 0, 0, 0))

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
            self.initListImageX(-60)
            self.pasteImagesX(-60)
        except ValueError:
            self.listImage = Image.new('RGBA', (1, 256), (0, 0, 0, 0))
        return self.listImage
    
    def makeWishlistImage(self):
        self.loadImages()
        self.initListImageX(15)
        self.pasteImagesX(15)
        return self.listImage
    
    def makeImage(self):
        self.loadImages()
        self.initListImageY(10)
        self.pasteImagesY(10)
        return self.listImage    

class VersionInfoMaker(BaseListImageMaker):
    def __init__(self):
        self.version = ''
        self.wishlistImage = ''
        self.resultlistImage = ''
        self.versionInfoImage = ''
        self.versionNumber = ''
        self.rightBracket = Image.open('./.formwork/right_bracket.png')
        self.leftBracket = Image.open('./.formwork/left_bracket.png')
        self.VIH = 0
        self.font = ImageFont.truetype("./.font/SuseongDotum.ttf", 80)

    def setWishlistImage(self,wishlistImage):
        self.wishlistImage = wishlistImage
        WW, WH = self.wishlistImage.size
        self.VIH = WH+40
        self.rightBracket = self.rightBracket.resize((self.rightBracket.width,self.VIH))
        self.leftBracket  = self.leftBracket.resize((self.leftBracket.width,self.VIH))
        return self
    
    def setResultlistImage(self,resultlistImage):
        self.resultlistImage = resultlistImage
        return self
    
    def setVersionNumber(self, versionNumber):
        self.versionNumber = versionNumber
        return self

    def drawWishlistBox(self):
        WW, WH = self.wishlistImage.size
        wishlistBox = Image.new("RGBA", (WW+60,self.VIH), (40, 47, 64,255))
        wishlistBox.paste(self.wishlistImage, (30, 20), self.wishlistImage)
        return wishlistBox

    def drawResultlistBox(self):
        RW, RH = self.resultlistImage.size
        posY = (self.VIH - RH)//2
        resultlistBox = Image.new("RGBA", (RW+40,self.VIH), (221, 213, 194,255))
        resultlistBox.paste(self.resultlistImage, (30, posY), self.resultlistImage)
        return resultlistBox

    def writeVersion(self):
        versionBoxDraw = ImageDraw.Draw(self.listImage)
        textWidth, textHeight = versionBoxDraw.textsize(self.versionNumber, self.font)
        textY = (self.VIH - textHeight) // 2
        versionBoxDraw.text((30, textY-10), self.versionNumber, (60, 70, 95, 255), self.font)

    def makeVersionInfoImage(self):
        self.imageList = [self.leftBracket, self.drawWishlistBox(),self.drawResultlistBox()]
        if self.resultlistImage.width > 1:
            self.imageList.append(self.rightBracket)
        self.initListImageX()
        self.pasteImagesX()
        self.writeVersion()
        return self.listImage


class InputReader:
    def __init__(self):
        self.inputList = getFileInput('input.txt')
        self.wishData  = getJsonData('charWishlist.json')
        self.charDict  = {x.split('\t')[0].strip().replace(' ','_'):[ y.strip().replace(': ','_').replace(' ','_') for y in x.split('\t')[1:]] for x in getFileInput("charDict") if x[0] != '#'}
        
        self.itemFolderPath = "./_Item/"
        self.cardFolderPath = "./_Card/"
        self.wishlistFolderPath = "./_Wishlist/"
        mkdirExistOk(self.wishlistFolderPath)

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

    def getWishlistFilePath(self,versionNumber):
        return (self.wishlistFolderPath + versionNumber + "_Wishlist.png").replace(' ','_')
    

if __name__ == "__main__":
    inputReader      = InputReader()
    listImageMaker   = ListImageMaker()
    versionInfoMaker = VersionInfoMaker()
    totalCnt = len(inputReader.inputList)

    temp = []
    for idx,inputLine in enumerate(inputReader.inputList,start=1):
        versionNumber, *wishResult = inputLine.split('\t')
        strongPrint(f" [{idx}/{totalCnt}] {versionNumber} ")

        wishlistFilePath = inputReader.getWishlistFilePath(versionNumber)
        if not (os.path.exists(wishlistFilePath)):
            cardPathList     = inputReader.getCardPathList(versionNumber)
            itemPathList     = inputReader.getItemPathList(wishResult)

            wishlistImage   = listImageMaker.setImagePathList(cardPathList).makeWishlistImage()
            resultlistImage = listImageMaker.setImagePathList(itemPathList).makeResultlistImage()
            versionInfoMaker.setWishlistImage(wishlistImage).setResultlistImage(resultlistImage).setVersionNumber(versionNumber)
            versionInfoMaker.makeVersionInfoImage().save(wishlistFilePath)
        temp.append(wishlistFilePath)

    wishlistImage   = listImageMaker.setImagePathList(temp).makeImage().save('test.png')
