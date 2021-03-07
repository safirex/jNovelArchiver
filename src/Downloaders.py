# coding: utf-8
import requests
import re
import Chapters

class Novel:
    def __init__(self,codeNovel,titreNovel):
        self.code=codeNovel
        self.titre=titreNovel

    def download(self) -> str:
        #download chapter from site.
        pass
    

    def processNovel(self) -> str:
        """"will process the html and download the chapter"""
        pass

    def getNovelTitle(self) -> str:
        """"fetch the novel title from the TOC page"""
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

class SyosetuNovel(Novel):
    def __init__(self,Novel):
        self.site='https://ncode.syosetu.com/'
        self.headers={"user-agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
        super(SyosetuNovel,self).__init__(Novel.code,Novel.titre)

    def processNovel(self):
        print("sysosetu novel "+self.titre)
        print('last chapter: '+str(self.getLastChapter()))

        url='https://ncode.syosetu.com/%s/'%self.code
        headers = self.headers
        print('accessing: '+url)
        print()
        rep=requests.get(url,headers=headers)
        rep.encoding='utf-8'
        html=rep.text
        
        if(self.getLastChapter()==0):
            self.processTocResume(html)

        #get the number of chapters (solely for user feedback)
        online_chapter_list=re.findall(r'<a href="/'+self.code+'/'+'(.*?)'+'/">.*?</a>',html,re.S)

        #get the chapters url
        #chapter_list=re.findall(r'<a href="/'+self.code+'/'+'.*?'+'/">.*?</a>',html,re.S)
        lastDL=self.getLastChapter()
        online_chapter_list=online_chapter_list[lastDL:]
        #chapter_list=chapter_list[lastDL:]
        print("there are %d chapters to udpate"%len(online_chapter_list))
        print(online_chapter_list)

        #chapter_list=re.findall(r'<a href="(.*?)">(.*?)<',str(chapter_list))
        #i=lastDL+1
        for chapter_num in online_chapter_list:
            chap=self.processChapter(int(chapter_num))
            chap.createFile(self.dir+'/')

    def processTocResume(self,html=''):
        if(html==''):
            url='https://ncode.syosetu.com/%s/'%self.code
            headers = {"user-agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
            rep=requests.get(url,headers=headers)
            rep.encoding='utf-8'
            html=rep.text
        #print(html)
        resume=re.findall('<div id="novel_ex">'+'(.*?)'+'</div>',html,re.S)[0]
        resume=self.cleanText(resume)
        title='novel title= '+self.getNovelTitle()
        resume=title+'\n\n'+resume
        self.createFile(0,'TOC',resume)

    def processChapter(self,chapter_num):
        chapter=Chapters.SyosetuChapter(self.code,chapter_num)
        chapter_rep=requests.get(chapter.getUrl(),headers=self.headers)
        chapter_rep.encoding='utf-8'
        chapter_html=chapter_rep.text
        chapter.getTitle(chapter_html)
        chapter.getContent(chapter_html)
        return chapter
        #self.createFile(i,chapter_title,chapter_content)
        #self.setLastChapter(i)



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

    def getNovelTitle(self):
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

class KakuyomuNovel(Novel):
    def __init__(self,Novel):
        super().__init__(Novel.code,Novel.titre)

    def getChapterTitle(self,str):
        chapter_title=re.findall('<p class="widget-episodeTitle js-vertical-composition-item">(.*?)<',str)[0]
        return chapter_title



    def processNovel(self):
        print("Kakuyomu novel "+self.titre)
        print('last chapter: '+str(self.getLastChapter()))
        url='https://kakuyomu.jp/works/%s'%self.code
        print('accessing '+url)
        chapterListDiv='/works/%s/episodes/(.*?)"'%self.code
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
        rep=requests.get(url,headers=headers)
        rep.encoding='utf-8'
        html=rep.text
        chapList=re.findall(chapterListDiv,html,re.DOTALL)[1:]
        chapList=chapList[self.getLastChapter():]
        print()
        print("there are %d chapters to udpate"%len(chapList))
        print(chapList)
        print()
        for chap in chapList: #last chapter = 0 at beginning
            self.setLastChapter(self.getLastChapter()+1)
            chapter_url=url+'/episodes/'+chap
            print('chapter: '+str(self.getLastChapter())+'  '+chapter_url)
            self.processChapter(chapter_url)


    def processChapter(self,chapter_url):
        rep=requests.get(chapter_url)#,headers=headers)
        html=rep.text
        chapter_title=self.getChapterTitle(html)
        print(chapter_title)
        content=re.findall('<p id="p.*">(.*?)</p>',html)
        contentUPDATED=[]
        for sentence in content:
            sentence = sentence.replace('<br />','\n')
            sentence = sentence.replace('<ruby>','')
            sentence = sentence.replace('</ruby>','')
            sentence = sentence.replace('<rp>','')
            sentence = sentence.replace('</rp>','')
            sentence = sentence.replace('<rt>','')
            sentence = sentence.replace('</rt>','')
            sentence = sentence.replace('<rb>','')
            #signal character superpose
            sentence = sentence.replace('</rb>','//')
            sentence += '\n'
            contentUPDATED.append(sentence)
        self.createFile(chapter_title,contentUPDATED,chapter_url)


    def createFile(self,chapter_title,chapter_content,chapter_url):
        chapter_title=checkTitle(chapter_title)
        file = open('%s/%d_%s.txt'%(self.getDir(),self.getLastChapter(),chapter_title), 'w+', encoding='utf-8')
        file.write(chapter_url+'\n')
        file.write(chapter_title+'\n')
        for sentence in chapter_content:
            file.write(sentence)
        file.close()

    def getNovelTitle(self):
        titlediv='<h1 id="workTitle"><a href="/works/%s">'%self.code
        url='https://kakuyomu.jp/works/%s'%self.code
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
        rep=requests.get(url,headers=headers)
        rep.encoding='utf-8'
        html=rep.text
        titlediv1=html.find(titlediv)+len(titlediv)
        endTitleDiv=html[titlediv1:].find('</a>')+titlediv1
        return html[titlediv1:endTitleDiv]


class N18SyosetuNovel(SyosetuNovel,Novel):
    def __init__(self,novel):
        novel.setCode(novel.code[3:])
        super(N18SyosetuNovel,self).__init__(novel)
        self.site='https://novel18.syosetu.com'


    def processNovel(self):
        import sys
        print("sysosetu novel "+self.titre)
        print('last chapter: '+str(self.getLastChapter()))

        url=self.site+'/%s/'%self.code
        print('accessing: '+url)
        print()
        html=self.connectViaMechanize(url)

        if(self.getLastChapter()==0):
            self.processTocResume(html)
        #get the number of chapters (solely for user feedback)
        online_chapter_list=re.findall('<a href="/'+self.code+'/'+'(.*?)'+'/">',html,re.DOTALL)

        print('<href="/'+self.code+'/'+'(.*?)'+'/">')
        lastDL=self.getLastChapter()
        online_chapter_list=online_chapter_list[lastDL:]
        #chapter_list=chapter_list[lastDL:]

        print("there are %d chapters to udpate"%len(online_chapter_list))
        print(online_chapter_list)

        #chapter_list=re.findall(r'<a href="(.*?)">(.*?)<',str(chapter_list))

        for chapter_num in online_chapter_list:
            chap=self.processChapter(int(chapter_num))
            chap.createFile(self.dir+'/')

    def processChapter(self,chapter_num):
        chapter=Chapters.N18SyosetuChapter(self.code,chapter_num)
        chapter_html=self.connectViaMechanize('%s/%s/%s/'%(self.site,self.code,chapter_num))
        chapter.getTitle(chapter_html)
        chapter.getContent(chapter_html)
        return chapter



    def getNovelTitle(self,html=''):
        #https://novel18.syosetu.com/n8451sz/
        url=self.site+'/%s/'%self.code
        print('\naccessing: '+url)
        #https://novel18.syosetu.com/n8451sz
        #cookies={'autologin':'1872412%3C%3E014ebbec6d4b5ba4b35b8b5853e19625f9e6bf77eb2609658c927a0a8b4989b6'}
        #cookies.update({'ASP.NET_SessionId':'to3210exzz4jerncygdnevl0'})
        #cookies.update({'ses':'qRtZF3-Wlg5ehnQXuig-X1'})
        #print(cookies['autologin'])

        if(html==''):
            html=self.connectViaMechanize(url)
        import sys
        writer=re.findall(r'<p class="novel_title">(.*?)</p>',html)
        #print(writer)
        return writer[0]

    def __createFile__(self,chapterNumber,chapter_title,chapter_content):
        chapter_title=checkTitle(chapter_title)
        print('saving %s %s'%(chapterNumber,chapter_title))
        file = open('%s/%d_%s.txt'%(self.getDir(),chapterNumber,chapter_title), 'w+', encoding='utf-8')
        file.write(chapter_title+'\n')
        file.write(chapter_content)
        file.close()
        print('\n\n')

    def connectViaMechanize(self,url):
        import http.cookiejar as cookielib
        from bs4 import BeautifulSoup
        import mechanize

        print('beginning server cracking beep boop')
        br=mechanize.Browser()
        br.addheaders = [('User-agent', 'Firefox')]

        cj = cookielib.LWPCookieJar()
        # add a cookie to cookie jar
        # Cookie(version, name, value, port, port_specified, domain,
        # domain_specified, domain_initial_dot, path, path_specified,
        # secure, discard, comment, comment_url, rest)

        cj.set_cookie(cookielib.Cookie(0, 'over18', 'yes', '80', False, '.syosetu.com',
            True, False, '/', True, False, None, False, None, None, None))

        #autologinkey=str(self.cookie.get('autologin'))
        #cj.set_cookie(cookielib.Cookie(0, 'autologin', autologinkey, '80', False, '.syosetu.com',
        #    True, False, '/', True, False, None, False, None, None, None))

        #print(cj)
        br.set_handle_redirect(True)
        br.set_cookiejar(cj)
        print('accessing : '+url)
        br.open(url)
        resp=br.response()
        content = resp.get_data()
        soup = BeautifulSoup(content, 'html.parser')
        #print(soup.prettify())
        return str(soup)

def checkTitle(str):
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

"""
class WuxiaWorldNovel(Novel):
    def __init__(self,Novel):
        self.site='https://www.wuxiaworld.com/novel/'
        # "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
        self.headers={"user-agent":"test"}
        code=Novel.titre.replace(' ','-')
        code=code.lower()
        Novel.code=code
        #novel.code = the-trash-of-count
        super(WuxiaWorldNovel,self).__init__(Novel.code,Novel.titre)

    
    def processNovel(self):
        print("WuxiaWorld novel "+self.titre)
        print('last chapter: '+str(self.getLastChapter()))
        url=self.site+self.code
        print('accessing '+url)

        chapterListDiv='/novel/%s/(.*?)"'%self.code
        #rep=requests.get(url,headers=self.headers)
        #rep.encoding='utf-8'
        html=self.connectViaMechanize(url)
        chapList=re.findall(chapterListDiv,html,re.DOTALL)[2:]
        chapList=chapList[self.getLastChapter():]
        print()
        print("there are %d chapters to udpate"%len(chapList))
        print(chapList)
        print()
        for chap in chapList: #last chapter = 0 at beginning
            self.setLastChapter(self.getLastChapter()+1)
            chapter_url=url+'/'+chap
            print('chapter: '+str(self.getLastChapter())+'  '+chapter_url)
            chapter=self.processChapter(chapter_url,self.getLastChapter())
            chapter.createFile(self.dir+'/')

    def processChapter(self,chapter_url,chapter_num):
        chapter=Chapters.WuxiaWorldChapter(chapter_url,chapter_num)
        #chapter_rep=requests.get(chapter.getUrl(),headers=self.headers)
        #chapter_rep.encoding='utf-8'
        chapter_html=self.connectViaMechanize(chapter_url)
        chapter.getTitle(chapter_html)
        print(chapter.title)
        chapter.getContent(chapter_html)
        return chapter

    def connectViaMechanize(self,url):
            import http.cookiejar as cookielib
            from bs4 import BeautifulSoup
            import mechanize

            print('beginning server cracking beep boop')
            br=mechanize.Browser()
            br.addheaders = [('User-agent', 'Chrome')]

            cj = cookielib.LWPCookieJar()
            # add a cookie to cookie jar
            # Cookie(version, name, value, port, port_specified, domain,
            # domain_specified, domain_initial_dot, path, path_specified,
            # secure, discard, comment, comment_url, rest)

            cj.set_cookie(cookielib.Cookie(0, 'over18', 'yes', '80', False, '.syosetu.com',
                True, False, '/', True, False, None, False, None, None, None))

            #autologinkey=str(self.cookie.get('autologin'))
            #cj.set_cookie(cookielib.Cookie(0, 'autologin', autologinkey, '80', False, '.syosetu.com',
            #    True, False, '/', True, False, None, False, None, None, None))

            #print(cj)
            br.set_handle_redirect(True)
            br.set_cookiejar(cj)
            print('accessing : '+url)
            br.open(url)
            resp=br.response()
            content = resp.get_data()
            soup = BeautifulSoup(content, 'html.parser')
            return str(soup)
"""






class WuxiaWorldNovel(Novel):
    def __init__(self,Novel):
        # "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
        self.headers={"user-agent":"test"}
        code=Novel.titre.replace(' ','-')
        code=code.lower()
        Novel.code=code
        #novel.code = the-trash-of-count
        super(WuxiaWorldNovel,self).__init__(Novel.code,Novel.titre)
        self.site='https://www.wuxiaworld.com/novel/'
        self.TOCUrl=self.site+self.code
        self.chapterReader=chapter=Chapters.WuxiaWorldChapter("roar.com",1)
    
    def processNovel(self):
        print("WuxiaWorld novel "+self.titre)
        print('last chapter: '+str(self.getLastChapter()))
        TOCUrl=self.TOCUrl
        TOCChapterListDiv='/novel/%s/(.*?)"'%self.code

        
        print('accessing '+TOCUrl)
        


        #rep=requests.get(url,headers=self.headers)
        #rep.encoding='utf-8'
        html=self.connectViaMechanize(TOCUrl)
        chapList=self.getChapterList(TOCChapterListDiv,html)
        chapList=chapList[self.getLastChapter():]
        print()
        print("there are %d chapters to udpate"%len(chapList))
        print(chapList)
        print()
        for chap in chapList: #last chapter = 0 at beginning
            self.setLastChapter(self.getLastChapter()+1)
            chapter_url=self.getChapterUrl(TOCUrl,chap)
            print('chapter: '+str(self.getLastChapter())+'  '+chapter_url)
            chapter=self.processChapter(chapter_url,self.getLastChapter())
            chapter.createFile(self.dir+'/')


    def getChapterUrl(self,url,chapNum):
        return url+'/'+chapNum
    def getChapterList(self,TOCChapterListDiv,chatper_html):
        return re.findall(TOCChapterListDiv,chatper_html,re.DOTALL)[2:]

    def processChapter(self,chapter_url,chapter_num):
        self.chapterReader.new(chapter_url,chapter_num)
        chapter=self.chapterReader
        chapter_html=self.connectViaMechanize(chapter_url)
        chapter.getTitle(chapter_html)
        print(chapter.title)
        chapter.getContent(chapter_html)
        return chapter

    def connectViaMechanize(self,url):
            import http.cookiejar as cookielib
            from bs4 import BeautifulSoup
            import mechanize

            print('beginning server cracking beep boop')
            br=mechanize.Browser()
            br.addheaders = [('User-agent', 'Chrome')]

            cj = cookielib.LWPCookieJar()
            # add a cookie to cookie jar
            # Cookie(version, name, value, port, port_specified, domain,
            # domain_specified, domain_initial_dot, path, path_specified,
            # secure, discard, comment, comment_url, rest)

            cj.set_cookie(cookielib.Cookie(0, 'over18', 'yes', '80', False, '.syosetu.com',
                True, False, '/', True, False, None, False, None, None, None))

            #autologinkey=str(self.cookie.get('autologin'))
            #cj.set_cookie(cookielib.Cookie(0, 'autologin', autologinkey, '80', False, '.syosetu.com',
            #    True, False, '/', True, False, None, False, None, None, None))

            #print(cj)
            br.set_handle_redirect(True)
            br.set_cookiejar(cj)
            print('accessing : '+url)
            br.open(url)
            resp=br.response()
            content = resp.get_data()
            soup = BeautifulSoup(content, 'html.parser')
            return str(soup)
