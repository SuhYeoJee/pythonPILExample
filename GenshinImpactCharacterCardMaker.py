from igzgModule import *
from PIL import Image, ImageDraw, ImageFont

class CardMaker:
    def __init__(self):
        self.cardShapeImage = Image.open('./.formwork/card_shape.png').convert('RGBA')
        self.nameSpaceImage = Image.open('./.formwork/name_space.png').convert('RGBA')
        self.font = ImageFont.truetype("./.font/SuseongDotum.ttf", 40)

        self.backgroundImage = self.iconImage = self.cardText = ''
        self.cardImage = self.cardDraw = ''
    
    def setNewImage(self):
        self.cardImage = Image.new('RGBA', self.cardShapeImage.size)
        self.cardDraw  = ImageDraw.Draw(self.cardImage)
        return self

    def setBackgroundImage(self,backgroundFileName):
        self.backgroundImage = Image.open(f'./Namecard_Background_/{backgroundFileName}').convert('RGBA')
        return self
    
    def setIconFile(self,iconFileName):
        self.iconImage = Image.open(f'./_Icon/{iconFileName}').convert('RGBA')
        return self
    
    def setCardText(self, cardText):
        self.cardText = cardText
        return self
    
    def makeCardImage(self):
        self.setNewImage()
        self.pasteBackground().pasteIconImage()
        self.pasteNameSpace().writeCardText()
        return self.cardImage
    
    def pasteBackground(self):
        cW, cH = self.cardShapeImage.size
        bgW, bgH = self.backgroundImage.size
        self.backgroundImage = self.backgroundImage.resize((int(bgW * (cH / bgH)), cH), Image.ANTIALIAS)
        self.backgroundImage = self.backgroundImage.crop(((bgW - cW) // 2, 0, (bgW + cW) // 2, cH))

        self.cardImage.paste(self.backgroundImage, (0, 0), self.cardShapeImage)
        return self

    def pasteNameSpace(self):
        self.cardImage.paste(self.nameSpaceImage, (0, 0), self.nameSpaceImage)
        return self

    def pasteIconImage(self):
        x_offset = (self.cardImage.width - self.iconImage.width) // 2
        self.cardImage.paste(self.iconImage, (x_offset, 0), self.iconImage)
        self.cardImage.putalpha(self.cardShapeImage.getchannel("A"))

        return self

    def writeCardText(self):
        textWidth, textHeight = self.cardDraw.textsize(self.cardText, self.font)
        textX = (self.cardImage.width - textWidth) // 2
        textY = self.cardImage.height - textHeight - 8

        self.cardDraw.text((textX, textY), self.cardText, (60, 70, 95, 255), self.font)
        return self

class InputReader:
    def __init__(self):
        self.inputList = getFileInput('input.txt')
        self.charDict = { x.split('\t')[0].strip().replace(' ','_'):[ y.strip().replace(': ','_') for y in x.split('\t')[1:]] for x in getFileInput("charDict") if x[0] != '#'}
        self.targetList = [self.charDict[x] for x in self.inputList if x in self.charDict.keys()]
        self.cardFolderPath = "./_Card/"
        mkdirExistOk(self.cardFolderPath)

    def getBackgroundFileName(self,inputLine):
        return ("Namecard_Background_" + self.charDict[inputLine][1] + ".png").replace(' ','_')
    
    def getIconFileName(self,inputLine):
        return (self.charDict[inputLine][0]+ "_Icon.png").replace(' ','_')
    
    def getCardFilePath(self,inputLine):
        return (self.cardFolderPath + self.charDict[inputLine][0] + "_Card.png").replace(' ','_')
    

if __name__ == "__main__":
    inputReader = InputReader()
    cardMaker = CardMaker()
    totalCnt    = len(inputReader.inputList)

    for idx,inputLine in enumerate(inputReader.inputList,start=1):
        strongPrint(f" [{idx}/{totalCnt}] {inputLine} ")

        backgroundFileName = inputReader.getBackgroundFileName(inputLine)
        iconFileName       = inputReader.getIconFileName(inputLine)
        cardFilePath       = inputReader.getCardFilePath(inputLine)

        cardMaker.setBackgroundImage(backgroundFileName).setIconFile(iconFileName).setCardText(inputLine)
        cardMaker.makeCardImage().save(cardFilePath)
