# coding: utf-8
import requests
import re
import Chapters
class Novel:
    def __init__(self,codeNovel,titreNovel):
        self.code=codeNovel
        self.titre=titreNovel

    def download(self) -> str:
        """download chapter from site."""
        pass

    def processNovel(self) -> str:
        """"will process the html and download the chapter"""
        pass

    def getNovelTitle(self,html) -> str:
        """"returns the novel title from the parsed html TOC page"""
        pass


    #instantiate an object depending of the code
    def updateObject(self):
        if(len(self.code)>7 and self.code.find('n18n')==0):
            return N18SyosetuNovel(self)
        elif (len(self.code)>=6 and len(self.code)<=7 and self.code.find('n')==0):
            return SyosetuNovel(self)
        elif(len(self.code)==len('1177354054888541019')):
            return KakuyomuNovel(self)
        elif(self.code.lower().find('wuxiaworld')==0):
            return WuxiaWorldNovel(self)
        else:
            return 0

    def createFile(self,chapterNumber,chapter_title,chapter_content):
        chapter_title=checkTitle(chapter_title)
        print('saving %s %s'%(chapterNumber,chapter_title))
        file = open('%s/%d_%s.txt'%(self.getDir(),chapterNumber,chapter_title), 'w+', encoding='utf-8')
        file.write(chapter_title+'\n')
        file.write(chapter_content)
        file.close()
        print('\n\n')

    def setLastChapter(self,chap):
        self.chap=chap
    def getLastChapter(self):
        return self.chap
    def setDir(self,dir):
        self.dir=dir
    def getDir(self):
        return self.dir
    def getTitle(self):
        return self.titre
    def setCode(self,code):
        self.code=code

    def setUrl(self):
        """"define the url of the novel"""
        pass

    def processNovel(self):
        print("novel "+self.titre)
        print('last chapter: '+str(self.getLastChapter()))
        url=self.setUrl()
        headers = self.headers
        print('accessing: '+url)
        print()
        rep=requests.get(url,headers=headers)
        rep.encoding='utf-8'
        html=rep.text

        if(self.getLastChapter()==0):
            self.processTocResume(html)
        #get the number of chapters (solely for user feedback)
        online_chapter_list=self.getChapterList(html)
        if(len(online_chapter_list)>=1):
            #get the chapters url
            lastDL=self.getLastChapter()
            online_chapter_list=online_chapter_list[lastDL:]
            print("there are %d chapters to udpate"%len(online_chapter_list))
            print(online_chapter_list)
            for chapter_num in online_chapter_list:
                chap=self.processChapter(int(chapter_num))
                chap.createFile(self.dir+'/')
            #will add new files for every revised chapters
            self.updatePerDate(html)
        else:
            print("this web novel has most likely been terminated")

    def processChapter(self,chapter_num)-> Chapters.Chapter:
        chapter=self.getChapter(self.code,chapter_num)
        #Chapters.SyosetuChapter(self.code,chapter_num)
        chapter_rep=requests.get(chapter.getUrl(),headers=self.headers)
        chapter_rep.encoding='utf-8'
        chapter_html=chapter_rep.text
        chapter.getTitle(chapter_html)
        chapter.getContent(chapter_html)
        return chapter

    def fetchTocPageHtml(self) ->str:
        '''fetch the html content of the TOC page'''
        html=self.fetchTocRawHtml()
        html=self.parseRawHtml(html)
        return html

    def fetchTocRawHtml(self):
        '''fetch the raw html of the toc of the novel'''
        pass

    def parseRawHtml(self) ->str :
        '''parse the raw htlm with the site specialised balises'''
        pass


    def getTocSynopsis(self,html) ->str:
        '''return the synopsis from the parsed html content
        of the TOC page'''        
        pass

    def processTocResume(self,html=''):
        '''create a file containing the Toc Page infos'''
        if(html==''):
            html=self.fetchTocPageHtml()
        resume=self.getTocSynopsis(html)
        title='novel title= '+self.getNovelTitle(html)
        resume=title+'\n\n'+resume
        self.createFile(0,'TOC',resume)
    
    def fetchTocSynopsis(self):
        self.fetchTocPageHtml()


    def getNovelTitle(self,html):
        if(html==''):
            html=self.fetchTocPageHtml()
        writer=self.getNovelTitle(html)
        
        print('title = ')
        print(writer)
        return writer




class SyosetuNovel(Novel):
    def __init__(self,Novel):
        self.site='https://ncode.syosetu.com/'
        self.headers={"user-agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
        super(SyosetuNovel,self).__init__(Novel.code,Novel.titre)
    
    def fetchTocPageHtml(self):
        url='https://ncode.syosetu.com/%s/'%self.code
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
        rep=requests.get(url,headers=headers)
        rep.encoding='utf-8'
        html=rep.text
        return html

    def getTocSynopsis(self,html):
        text=re.findall('<div id="novel_ex">'+'(.*?)'+'</div>',html,re.S)[0]
        text=self.cleanText(text)
        return text


    def updatePerDate(self,html):
        from bs4 import BeautifulSoup
        from datetime import date
        import os
        soup = BeautifulSoup(html, 'html.parser')
        online_chap_list=[]
        for h in soup.find_all('dl'):
            tmpChapTitle=h.find('a').text
            tmpChapUpdateDate=h.find('dt').text[1:11].replace('/','-')
            tmp=[tmpChapTitle,tmpChapUpdateDate]
            online_chap_list.append(tmp)

        dirList=os.listdir(self.getDir())
        for offlineChap in dirList:
            fileDir=self.getDir()+'/'+offlineChap
            modifTime= date.fromtimestamp(os.stat(fileDir).st_mtime)
            offChapNum =int( offlineChap[:offlineChap.find('_')])

            #time to check if a chap has been modified since download
            if (offChapNum !=0) & (len(online_chap_list)-1>=offChapNum):
                onlineDate=online_chap_list[offChapNum-1][1]
                onlineDate=date.fromisoformat(onlineDate)
                if(onlineDate > modifTime):
                    #modif after last revision of chapter
                    print('need update man')
                    chap=self.processChapter(int(offChapNum))
                    chap.createFile(self.dir+'/')
                    print('updated chap '+str(offChapNum))
        print("fin update")

    



    def cleanText(self,chapter_content):
        chapter_content = chapter_content.replace('</p>','\r\n')
        chapter_content = chapter_content.replace('<br />', '')
        chapter_content = chapter_content.replace('<rb>', '')
        chapter_content = chapter_content.replace('</rb>', '')
        chapter_content = chapter_content.replace('<rp>', '')
        chapter_content = chapter_content.replace('</rp>', '')
        chapter_content = chapter_content.replace('<rt>', '')
        chapter_content = chapter_content.replace('</rt>', '')
        chapter_content = chapter_content.replace('<ruby>', '')
        chapter_content = chapter_content.replace('</ruby>', '')
        return chapter_content

    def validateTitle(self,title):
        rstr = r"[\/\\\:\*\?\"\<\>\|]"
        new_title = re.sub(rstr, "_", title)
        return new_title

    def getNovelTitle(self,html):
        if(html==''):
            url='https://ncode.syosetu.com/%s/'%self.code
            headers = {"user-agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
            print('accessing: '+url)
            print()
            rep=requests.get(url,headers=headers)
            rep.encoding='utf-8'
            html=rep.text
        writer=re.findall(r'<p class="novel_title">(.*?)</p>',html,re.S)
        print('title = ')
        print(writer)
        return writer[0]


