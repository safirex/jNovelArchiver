import re




def checkTitle(str):
    # make sure the title is conform to windows url settings (260 char max)
    str=str.replace('?','')
    str=str.replace('!','')
    str=str.replace(':','')
    str=str.replace('"','')
    str=str.replace('*','')
    str=str.replace('/','')
    str=str.replace('\\','')
    str=str.replace('|','')
    str=str.replace('<','')
    str=str.replace('>','')
    str=str[:250-len('./novel_list/')]
    return str

class Chapter():
    def new(self,num,url):
        self.reset()
        self.__init__(num,url)
        return self

    def reset(self):
        dic = vars(self)
        for i in dic.keys():
            print(dic[i])
            dic[i] = 0

    def __init__(self,num,url=''):
        self.num=num
        self.content=[]
        self.title=''
        self.url=url

    def setContent(self,content):
        self.content=content

    def setTitle(self,Title):
        self.title=Title

    def setUrl(self) -> str:
        """"will define Url chapter"""
        pass
    def getUrl(self):
        return self.url

    def validateTitle(self,title):
        rstr = r"[\/\\\:\*\?\"\<\>\|]"
        new_title = re.sub(rstr, "_", title)
        return new_title

    def cleanText(self,chapter_content):
        chapter_content = chapter_content.replace('</p>','\r\n')
        chapter_content = chapter_content.replace('<br />', '')
        chapter_content = chapter_content.replace('<br/>', '')
        chapter_content = chapter_content.replace('<rb>', '')
        chapter_content = chapter_content.replace('</rb>', '')
        chapter_content = chapter_content.replace('<rp>', '')
        chapter_content = chapter_content.replace('</rp>', '')
        chapter_content = chapter_content.replace('<rt>', '')
        chapter_content = chapter_content.replace('</rt>', '')
        chapter_content = chapter_content.replace('<ruby>', '')
        chapter_content = chapter_content.replace('</ruby>', '')
        return chapter_content


    def createFile(self,dir):
        print("titre"+self.title)
        print(self.num)
        chapter_title=checkTitle(self.title)
        print("titre"+chapter_title)
        print('saving '+str(self.num)+' '+chapter_title)
        file = open('%s/%d_%s.txt'%(dir,self.num,chapter_title), 'w+', encoding='utf-8')
        file.write(chapter_title+'\n')
        file.write(self.content)
        file.close()
        print('\n\n')



class SyosetuChapter(Chapter):
    def __init__(self,novelNum,num):
        self.novelNum=novelNum
        super(SyosetuChapter,self).__init__(num)
        self.setUrl()

    def setUrl(self):
        self.url='https://ncode.syosetu.com/%s/%s/'%(self.novelNum,self.num)

    def getTitle(self,html):
        title=re.findall('<p class="novel_subtitle">(.*?)</p>',html)[0]
        replacething=re.findall('_u3000',title)
        for y in replacething:
            chapter_title=chapter_title.replace(y,' ')
        title=self.validateTitle(title)
        self.setTitle(title)
        return title

    def getContent(self,html):
        chapter_content=re.findall(r'<div id="novel_honbun" class="novel_view">(.*?)</div>',html,re.S)[0]
        replacething=re.findall(r'<p id=' + '.*?' + '>', chapter_content)
        for y in replacething:
            chapter_content=chapter_content.replace(y,'')
        chapter_content=self.cleanText(chapter_content)
        self.setContent(chapter_content)
        return chapter_content

class N18SyosetuChapter(SyosetuChapter,Chapter):
    def __init__(self,novelNum,num):
        super(N18SyosetuChapter,self).__init__(novelNum,num)
        self.setUrl()

    def setUrl(self):
        self.url='https://novel18.syosetu.com/%s/%s/'%(self.novelNum,self.num)

    def getContent(self,html):
        chapter_content=re.findall(r'<div class="novel_view" id="novel_honbun">(.*?)</div>',html,re.S)[0]
        replacething=re.findall(r'<p id=' + '.*?' + '>', chapter_content)
        for y in replacething:
            chapter_content=chapter_content.replace(y,'')
        chapter_content=self.cleanText(chapter_content)
        self.setContent(chapter_content)
        return chapter_content

    def createFile(self,dir):
        chapter_title=checkTitle(self.title)

        print('saving '+str(self.num)+' '+chapter_title)
        file = open('%s/%d_%s.txt'%(dir,self.num,chapter_title), 'w+', encoding='utf-8')
        file.write(chapter_title+'\n')
        file.write(self.content)
        file.close()
        print('\n\n')


"""
class WuxiaWorldChapter(Chapter):
    
    def __init__(self,chapterUrl,num):
        super(WuxiaWorldChapter,self).__init__(num)
        self.setUrl(chapterUrl)

    def setUrl(self,url):
        self.url=url

    def getTitle(self,html):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html)
        title=''
        for h in soup.find_all('title'):
            title=h.string

        #title=re.findall('<h4 class="" (*<>) (.*?)</h4>',html)[0]
        replacething=re.findall('_u3000',title)
        for y in replacething:
            chapter_title=chapter_title.replace(y,' ')
        title=self.validateTitle(title)
        self.setTitle(title)
        return title

    def getContent(self,html):
        from bs4 import BeautifulSoup

        #can be made better with soup.id["chapter-content"]
        soup = BeautifulSoup(html)
        chapter_content=''
        for div in soup.find_all('div'):
            id=div.get("id")
            if(id!=None):
                if(id=="chapter-content"):
                    chapter_content=div.text
                    break
        self.setContent(chapter_content)
        return chapter_content
"""


class WuxiaWorldChapter(Chapter):
        
    def __init__(self,chapterUrl,num):
        super(WuxiaWorldChapter,self).__init__(num)
        self.setUrl(chapterUrl)
        self.titleDiv='title'
        self.contentDiv='"chapter-content"'

    def setUrl(self,url):
        self.url=url

    def getTitle(self,html):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html)
        title=self.extractDiv(html,self.titleDiv)
        title=self.validateTitle(title)
        self.setTitle(title)
        return title

    def getContent(self,html):
        from bs4 import BeautifulSoup

        #can be made better with soup.id["chapter-content"]
        soup = BeautifulSoup(html)
        chapter_content=''
        for div in soup.find_all('div'):
            id=div.get("id")
            if(id!=None):
                if(id=="chapter-content"):
                    chapter_content=div.text
                    break
        self.setContent(chapter_content)
        return chapter_content

    def getContent2(self,html):
        chapter_content= self.extractId(html,self.contentDiv)
        self.setContent(chapter_content)
        return chapter_content
        
    def extractId(self,html,idDiv):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html,features="html5lib")
        chapter_content=""
        for line in soup.find_all(id=idDiv):
            chapter_content+=line.text
        return chapter_content

    def extractClass(html,classDiv):
        'TODO'
        pass

    def extractDiv(html,div):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html,features="html5lib")
        content=''
        for h in soup.find_all(div):
            content+=h.string
        return content