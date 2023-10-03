from igzgModule import *
from PIL import Image, ImageDraw, ImageFont

class COLOR:
    BLANK      = (0,0,0,0)
    GRAY       = (42,42,42,255)
    DEEPGRAY   = (36,36,36,255)
    BLACK      = (31,31,31,255)
    YELLOW     = (238,230,217,255)
    DEEPYELLOW = (211,188,141,255)
    BRONZE     = (127,115,92,255)
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

    def getListImage(self, imageList:list=[], offset:int=0, isX:bool=True):
        if imageList: self.setImageList(imageList)
        else: self._loadImages()
        self._initListImage(offset,isX)
        self._pasteImages(offset,isX)
        return self.listImage

    def _loadImages(self):
        # self.imageList = [Image.open(x).convert('RGBA') for x in self.imagePathList]
        self.imageList = []
        for i in self.imagePathList:
            temp = Image.open(i.split('.png')[0]+'.png').convert('RGBA')
            if i.split('.png')[-1].isdecimal():
                text = 'C'+i.split('.png')[-1]
                font = ImageFont.truetype("./.font/SuseongDotum.ttf", 30)

                tempDraw = ImageDraw.Draw(temp)
                textWidth, textHeight = tempDraw.textsize(text, font)
                textX = (temp.width - textWidth) // 2
                textY = (temp.height - textHeight)
                tempDraw.text((textX, textY-10), text, COLOR.BLACK, font,stroke_width=5, stroke_fill=COLOR.YELLOW)

            self.imageList.append(temp)


    def _initListImage(self, offset:int=0, isX:bool=True):
        if isX:
            wishlistW = sum(x.width for x in self.imageList) + ((len(self.imageList)-1)*offset)
            wishlistH = max(x.height for x in self.imageList)
        else:
            wishlistW = max(x.width for x in self.imageList)
            wishlistH = sum(x.height for x in self.imageList) + ((len(self.imageList)-1)*offset)
        self.listImage = Image.new('RGBA', (wishlistW, wishlistH), COLOR.BLANK )

    def _pasteImages(self, offset:int=0, isX:bool=True):
        pos = 0
        for image in self.imageList:
            if isX:
                self.listImage.paste(image, (pos, 0), image)
                pos += (image.width + offset)
            else:
                self.listImage.paste(image, (0, pos), image)
                pos += (image.height + offset)            
        
class ListImageMaker(BaseListImageMaker):
    def makeResultlistImage(self):
        try:
            self._loadImages()
            self.imageList = [x.resize((300,300),Image.BICUBIC) for x in self.imageList]
            self.getListImage(self.imageList,-60)
        except ValueError:
            self.listImage = ''
        return self.listImage
    
    def makeWishlistImage(self):
        self.listImage = self.getListImage(offset=15)
        return self.listImage
    
    def makeTotalWishlistImage(self):
        self.listImage  = self.getListImage(self.imageList, 30, isX=False)
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
        self.VIH = self.wishlistImage.height+40
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
        textX = (190 - textWidth) // 2
        textY = (self.VIH - textHeight) // 2
        versionBoxDraw.text((textX, textY-10), self.versionNumber, COLOR.BLACK, self.font,stroke_width=8, stroke_fill=COLOR.YELLOW)

    def makeVersionInfoImage(self):
        if self.versionNumber == '상시':
            self.getListImage([self.leftBracket, self.drawWishlistBox()])
            self.getListImage([self.listImage, self.drawResultlistBox()],isX=False)
            boxSize = (2170,750)
        else:
            self.imageList = [self.leftBracket, self.drawWishlistBox(),self.drawResultlistBox()]
            self.getListImage(self.imageList)
            boxSize = (2170,410)
        self.writeVersion()
        self.listImage = self.drawFixedSizeWrapper(self.listImage, boxSize, (30,30), COLOR.DEEPGRAY)
        self.listImage = self.drawRoundBorder(self.listImage, (10,10),5,COLOR.DEEPBRONZE)
        self.versionInfoImage = self.listImage
        return self.versionInfoImage

class TotalImageMaker(BaseListImageMaker, BoxDrawer):
    def __init__(self,wishImage):
        self.wishImage = wishImage
        self.font = ImageFont.truetype("./.font/SuseongDotum.ttf", 150)

    def wrapTotalWishImage(self):
        resultImage = self.drawDynamicSizeWrapper(self.wishImage,(200,150),COLOR.GRAY)
        resultImage = self.drawRoundBorder(resultImage,(5,5),5,COLOR.BRONZE)
        self.wishImage = self.drawDynamicSizeWrapper(resultImage,(100,100),COLOR.BLACK)
        self.titleImage = self._writeTitle()
        self.wishImage = self.getListImage([self.titleImage, self.wishImage],isX=False)
        return self.wishImage

    def wrapStandardWishImage(self):
        resultImage = self.drawDynamicSizeWrapper(self.wishImage,(200,150),COLOR.GRAY)
        resultImage = self.drawRoundBorder(resultImage,(5,5),5,COLOR.BRONZE)
        self.wishImage = self.drawDynamicSizeWrapper(resultImage,(100,10),COLOR.BLACK)
        return self.wishImage

    def _writeTitle(self):
        self.titleImage = Image.new("RGBA", (self.wishImage.width, 200), COLOR.BLACK )
        titleImageDraw = ImageDraw.Draw(self.titleImage)

        titleText = "원신 캐릭터 이벤트 기원 기록표"
        textWidth, textHeight = titleImageDraw.textsize(titleText, self.font)
        testPos = ((self.wishImage.width - textWidth)//2, (200 - textHeight)//2-30)

        titleImageDraw.text(testPos, titleText, COLOR.DEEPYELLOW, self.font)
        return self.titleImage


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
        # return [(self.itemFolderPath + self.charDict[x.split('c')[0]][0] + "_Item.png").replace(' ','_') for x in nameList]
        return [(self.itemFolderPath + self.charDict[x.split('c')[0]][0] + "_Item.png"+x.split('c')[-1]).replace(' ','_') for x in nameList]

if __name__ == "__main__":
    inputReader      = InputReader()
    listImageMaker   = ListImageMaker()
    versionInfoMaker = VersionInfoMaker()
    totalCnt = len(inputReader.inputList)

    versionInfoImageList = []
    for idx,inputLine in enumerate(inputReader.inputList,start=1):
        versionNumber, *wishResult = inputLine.split('\t')
        strongPrint(f" [{idx}/{totalCnt}] {versionNumber} ")

        cardPathList     = inputReader.getCardPathList(versionNumber)
        wishlistImage    = listImageMaker.setImagePathList(cardPathList).makeWishlistImage()

        itemPathList     = inputReader.getItemPathList(wishResult)
        resultlistImage  = listImageMaker.setImagePathList(itemPathList).makeResultlistImage()

        versionInfoMaker.setWishlistImage(wishlistImage).setResultlistImage(resultlistImage).setVersionNumber(versionNumber)
        versionInfoImageList.append(versionInfoMaker.makeVersionInfoImage())

    if versionNumber == '상시':
        totalWishlistImage   = listImageMaker.setImageList(versionInfoImageList[:-1]).makeTotalWishlistImage()
        resultImage = TotalImageMaker(totalWishlistImage).wrapTotalWishImage()
        standardImage = TotalImageMaker(versionInfoImageList[-1]).wrapStandardWishImage()
        resultImage   = listImageMaker.getListImage([resultImage,standardImage], isX=False)
        resultImage   = versionInfoMaker.drawDynamicSizeWrapper(resultImage,(0,500),COLOR.BLACK)
    else:
        totalWishlistImage   = listImageMaker.setImageList(versionInfoImageList).makeTotalWishlistImage()
        resultImage = TotalImageMaker(totalWishlistImage).wrapTotalWishImage()

    font = ImageFont.truetype("./.font/SuseongDotum.ttf", 23)
    text = "이 이미지는 HoYoverse에서 제공하는 원신(Genshin Impact)의 2차 창작물입니다. 사용된 모든 리소스에 대한 저작권은 HoYoverse에게 있으며, 원본 작품인 원신의 모든 저작권은 HoYoverse에 속합니다."
    tempDraw = ImageDraw.Draw(resultImage)
    textWidth, textHeight = tempDraw.textsize(text, font)
    textX = (resultImage.width - textWidth) // 2
    textY = (resultImage.height - textHeight)
    tempDraw.text((textX, textY-50), text, COLOR.BRONZE, font)

    W,H = resultImage.size
    resultImage = resultImage.resize((W//2,H//2),Image.BICUBIC)
    resultImage.save('res.png')
