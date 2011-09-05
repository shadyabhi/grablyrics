#!/usr/bin/python2

#I grabbed this script from random place & it needs improvement.OB
#This script grab lyrics of song playing in mpd

import urllib, os, shutil, commands, sys, string, re, BeautifulSoup, HTMLParser
from optparse import OptionParser, SUPPRESS_HELP

validChars = "-_.() %s%s" % (string.ascii_letters, string.digits)
lyricsfolder = os.path.expanduser ('~/.lyrics/')
verbose = 0
align = ""
wordDict = {
    '&quot;' : '"',
    '\r\n'   : '\n',
    '&gt;'   : '>',
    '&lt;'   : '<'
}

def remove_html_tags(data):
    p = re.compile(r'<[^<]*?/?>')
    data = p.sub('', data)
    p = re.compile(r'/<!--.*?-->/')
    return p.sub('',data)

# multi-word replace
def mReplace(text, wordDict):
    for key in wordDict:
        text = text.replace(key, str(wordDict[key]))
    return text

def checkmissing(artistname,songname):
    if os.path.isfile(lyricsfolder + "/missingsongs.txt"):
        try:
            lastmissing = open(lyricsfolder + "/missingsongs.txt","r").readlines()[-1]
        except IndexError:
            lastmissing = "foobar"
        if lastmissing == artistname + " : " + songname +"\n":
            if verbose: print "Already failed to find lyrics for song: %s" % lastmissing
            return True


#### start lyrics sites...
def lyricsmania(artist,title):
    artist = urllib.quote(artist.lower().replace(' ','_'))
    title = urllib.quote(title.lower().replace(' ','_')) 
    if verbose: print "Trying to fetch lyrics from lyricsmania.com"
    try:
        url = 'http://www.lyricsmania.com/%s_lyrics_%s.html' % (title, artist)
        if verbose: print url
        lyrics = urllib.urlopen(url)
    except:                                                                    
        if verbose: print "Could not connect to lyricsmania.com. Exiting..." 
        return                                                       
    text = lyrics.read()
    text = text.replace('<div id="rect_ad','')    
    f = file ('/home/shadyabhi/.config/conky/test.txt', 'w')
    f.write (text)
    soup = BeautifulSoup.BeautifulSoup(text)
    lyrics = soup.findAll(attrs= {"id" : "songlyrics_h"})
    if lyrics:                                                                 
        return re.sub(r'','','\n'.join(remove_html_tags(str(lyrics[0]).replace("<br />","")).split('\n')[1:-2])) 
    else:                                                                                                
        if verbose: print "Lyrics not foud at lyricsmania.com" 
        return


def lyricsondemand(artist,title):
    artist = urllib.quote(artist.lower().replace(' ',''))
    title = urllib.quote(title.lower().replace(' ','')) 
    if verbose: print "Trying to fetch lyrics from lyricsondemand.com"
    try:
        url = 'http://www.lyricsondemand.com/%s/%slyrics/%slyrics.html' % (artist[0],artist, title)
        lyrics = urllib.urlopen(url)
        if verbose: print url
    except:                                                                    
        if verbose: print "Could not connect to lyricsondemand.com. Exiting..."     
        return                                                       
    text = lyrics.read()
    soup = BeautifulSoup.BeautifulSoup(text)
    lyrics = soup.findAll('font',face="Verdana",size="2")[0:]
    if lyrics:                                                                 
        return re.sub(r'','','\n'.join(remove_html_tags(str(lyrics[0]).replace("<br />","")).split('\n')[1:-2])) 
    else:                                                                                                
        if verbose: print "Lyrics not foud at lyricsondemand.com" 
        return


def lyricwiki(artist,title):
    artist = artist.replace(' ','_').title()
    title = title.replace(' ','_').title()
    artist = urllib.quote(artist).replace('%26','&')
    title = urllib.quote(title)     
    if verbose: print "Trying to fetch lyrics from lyricwiki.org"
    try: 
        lyrics = urllib.urlopen('http://lyricwiki.org/%s:%s' % (artist, title))
    except:                                                                    
        if verbose: print "Could not connect to lyricwiki.org. Exiting..."     
        return                                                       
    text = lyrics.read()                                                       
    soup = BeautifulSoup.BeautifulSoup(text)
    lyrics = soup.findAll(attrs= {"class" : "lyricbox"})                       
    if lyrics:                                                                 
        return re.sub(r' Send.*?Ringtone to your Cell ','','\n'.join(remove_html_tags(lyrics[0].renderContents().replace('<br />','\n')).replace('\n\n\n','').split('\n')[0:-7]))
    else:                                                                                                
        if verbose: print "Lyrics not found at lyricwiki.org" 
        return   

def lyricsmode(artist,title):
    artist = urllib.quote(artist.lower().replace(' ','_'))
    title = urllib.quote(title.lower().replace(' ','_'))
    if verbose: print "Trying to fetch lyrics from lyricsmode.com"
    try:
        lyrics = urllib.urlopen('http://www.lyricsmode.com/lyrics/%s/%s/%s.html' % (artist[0],artist, title))
    except:
        if verbose: print "Could not connect to lyricsmode.com. Exiting..."
        return
    text = lyrics.read().decode('latin-1').replace( u'\xb7','')
    soup = BeautifulSoup.BeautifulSoup(text)
    #lyricsmode places the lyrics in a span with an id of "lyrics"
    lyrics = soup.findAll(attrs= {"id" : "lyrics"})
    if not lyrics:
        if verbose: print "Lyrics not found at lyricsmode.com"
        return []
    else:
        #this function removes formatting and converts html entities into ascii since lyricsmode obfuscates the lyrics.
        return remove_html_tags(unicode(BeautifulSoup.BeautifulStoneSoup(
                                lyrics[0].renderContents(),
                                convertEntities=BeautifulSoup.BeautifulStoneSoup.HTML_ENTITIES
                                )).replace('<br />','\n').strip('\r\n\t\t'))

def metrolyrics(artist,title):                                                             
    artist = urllib.quote(artist.lower().replace(' ','-'))                                  
    title = urllib.quote(title.lower().replace(' ','-'))                                     
    if verbose: print "Trying to fetch lyrics from metrolyrics.com"                           
    try:                                                                                       
        lyrics = urllib.urlopen("http://www.metrolyrics.com/%s-lyrics-%s.html" % (title,artist))
    except:                                                                
        if verbose: print "Could not connect to metrolyrics.com. Exiting..."
        return         
    text = lyrics.read()
    text = text.replace('</sc"+"ript>"','') #beautifulsoup chokes on this particular tag so we have to get rid of it. 
    soup = BeautifulSoup.BeautifulSoup(text)      
    lyrics = soup.findAll(attrs= {"id" : "lyrics"})
    if not lyrics:                                          
        if verbose: print "Lyrics not found at metrolyrics.com"  
        return 
    else:                                                      
        #this removes formatting and converts from html entities
        return '\n'.join(map(lambda x: x.strip(),remove_html_tags(unicode(BeautifulSoup.BeautifulStoneSoup(
                lyrics[0].renderContents(),convertEntities=BeautifulSoup.BeautifulStoneSoup.HTML_ENTITIES)
                ))[2:].replace('\r','\n').split('\n'))[:-2])

def absolutelyrics(artist,title):
    artist = urllib.quote(artist.lower().replace(' ','_'))
    title = urllib.quote(title.lower().replace(' ','_'))
    if verbose: print "Trying to fetch lyrics from absolutelyrics.com"
    try:
        lyrics = urllib.urlopen("http://www.absolutelyrics.com/lyrics/view/%s/%s/" % (artist,title))
    except:
        if verbose: print "Could not connect to absolutelyrics.com. Exiting..."
        return
    text = lyrics.read()
    text = text.replace(u"</scr'+'ipt>",'') #beautifulsoup chokes on this particular tag so we have to get rid of it.
    soup = BeautifulSoup.BeautifulSoup(text)
    lyrics = soup.findAll(attrs= {"id" : "realText"})
    if not lyrics:
        if verbose: print "Lyrics not found at absolutelyrics.com"
        return
    else:
        #this removes formatting and converts from html entities
        return remove_html_tags(str(lyrics[0]).replace("<br />","\n")) 
              
def lyricstime(artist,title):
    artist = urllib.quote(artist.lower().replace(' ','-'))
    title = urllib.quote(title.lower().replace(' ','-'))
    if verbose: print "Trying to fetch lyrics from lyricstime.com"
    try:
        lyrics = urllib.urlopen("http://www.lyricstime.com/%s-%s-lyrics.html" % (artist,title))
    except:
        if verbose: print "Could not connect to lyricstime.com"
        return
    text = lyrics.read()
    text = text.replace('</SCR\'+\'IPT>','')
    soup = BeautifulSoup.BeautifulSoup(text)
    lyrics = soup.findAll(attrs= {"id" : "songlyrics"})
    if not lyrics:
        if verbose: print "Lyrics not found at lyricstime.com"
        return
    else:
        return remove_html_tags(str(lyrics[0]).replace('<br />','')).replace('\n\r\n','')

def leoslyrics(artist,title):
    '''leoslyrics provides a nice api that returns easy to handle xml'''
    artist = urllib.quote(artist.lower())
    title = urllib.quote(title.lower())
    if verbose: print "Trying to fetch lyrics from leoslyrics.com"
    try:
        lyrics = urllib.urlopen('http://api.leoslyrics.com/api_search.php?auth=duane&artist=%s&songtitle=%s' % (artist, title))
    except:
        if verbose: print "Could not connect to leoslyrics.com"
        return
    text = lyrics.read()
    print text
    soup = BeautifulSoup.BeautifulSoup(text)
    if soup.findAll("response")[0].renderContents() == 'SUCCESS' and soup.findAll("result")[0].attrs[2][1] == 'true':
        try:
            lyrics = urllib.urlopen('http://api.leoslyrics.com/api_lyrics.php?auth=duane&hid=%s' % soup.findAll("result")[0].attrs[1][1]).read()
        except:
            if verbose: print "Could not connect to leoslyrics.com"
            return
        soup = BeautifulSoup.BeautifulSoup(lyrics)
        lyrics = soup.findAll('text')[0]
        return '\n'.join(filter(lambda x: not x.startswith('From:'),map(lambda x: x.strip(),mReplace(lyrics.renderContents(),{'&#xD;':'','\r\n':'\n'}).split('\n'))))
    else:
        if verbose: print "Lyrics not found at leoslyrics.com"
        return
        
def songlyrics(artist,title):
    artist = urllib.quote(artist.lower().replace(' ','-'))
    title = urllib.quote(title.lower().replace(' ','-'))
    if verbose: print "Trying to fetch lyrics from songlyrics.com"
    try:
        lyrics = urllib.urlopen("http://www.songlyrics.com/%s/%s-lyrics/" % (artist,title))
    except:
        if verbose: print "Could not connect to songlyrics.com Exiting..."
        return
    text = lyrics.read()
    soup = BeautifulSoup.BeautifulSoup(text)
    lyrics = soup.findAll(attrs= {"id" : "songLyricsDiv"})
    if not lyrics:
        if verbose: print "Lyrics not found at songlyrics.com"
        return
    else:
        if str(lyrics[0]).startswith('<p id="songLyricsDiv" class="songLyricsV14" style="font-size: 14px">\n                                         \tSorry, we have no'):
            if verbose: print "Lyrics not found at songlyrics.com"
            return
        #this removes formatting and an advertisement.
        return '\n'.join(filter(lambda x: not x.endswith('www.songlyrics.com ]'),map(lambda x: x.strip(),str(lyrics[0]).split('<br />')))[1:-4])
        
#### end lyric sites...

def fetchlyrics(artistname,songname):
    lyricssite='lyricsmania'                   
    lyrics = lyricsmania(artistname,songname)
    if not lyrics:
        lyricssite='lyricsondemand'                   
        lyrics = lyricsondemand(artistname,songname)
    if not lyrics:
        lyricssite='lyricwiki'                   
        lyrics = lyricwiki(artistname,songname)
    if not lyrics:
        lyricssite="lyricsmode"
        lyrics = lyricsmode(artistname,songname)
    if not lyrics:
        lyricssite="metrolyrics"
        lyrics = metrolyrics(artistname,songname)
    if not lyrics:
        lyricssite="absolutelyrics"
        lyrics = absolutelyrics(artistname,songname)
    if not lyrics:
        lyricssite="lyricstime"
        lyrics = lyricstime(artistname,songname)
    if not lyrics:
        lyricssite="leoslyrics"
        lyrics = leoslyrics(artistname,songname)
    if not lyrics:
        lyricssite="songlyrics"
        lyrics = songlyrics(artistname,songname)        
    if verbose and lyrics: print "Found lyrics from %s. Writing to file." % (lyricssite)
    return lyrics

def printlyrics(lyrics):
    if align: print '\n'.join(map(lambda x:align + x,lyrics))
    else: print '\n'.join(lyrics)

def getlyrics(artistname,songname): 
    #make names lowercase for folders and remove trailing newflines
    artistname = mReplace(artistname.strip(),{'\'':'','(Live)':''})                              
    songname = mReplace(songname.strip(),{'\'':'','(Live)':''})                           

    #set lyrics folder, the folder used by default rhythmbox lyrics plugin is ~/.lyrics
    artistfolder = os.path.join(lyricsfolder,''.join(c for c in artistname[:128].lower() if c in validChars))
    #check if lyrics folder exists, if not then create it                                                        
    if not os.path.isdir(lyricsfolder):                                                                           
        if verbose: print "Lyrics folder: %s doesn't exist. Creating it..." % lyricsfolder                        
        os.mkdir(lyricsfolder)                                                                                    

    lyricfile = os.path.join(artistfolder,''.join(c for c in songname[:128].lower() if c in validChars) + '.lyric')
    
    #make the names ready for the intertubes urls
    #check if the lyric file already exists      
    if os.path.isfile(lyricfile) == False:       
        lyrics = fetchlyrics(artistname,songname)
        if lyrics:
            #remove html entities
            lyrics = str(BeautifulSoup.BeautifulStoneSoup(lyrics,convertEntities=BeautifulSoup.BeautifulStoneSoup.HTML_ENTITIES))
            #check if the artist folder exists, if not then create it
            if not os.path.isdir(artistfolder):                     
                if verbose: print "Artist folder: %s doesn't exist. Creating it..." % artistfolder
                os.mkdir(artistfolder) 
            #write the lyrics to their appropriate file
            f = file (lyricfile, 'w')
            f.write (lyrics)
            f = file (lyricfile, 'r')
            lyrics = mReplace(f.read(),wordDict).split('\n')
            if verbose: print "Found lyrics. Writing to %s" % (lyricfile)
            printlyrics(lyrics)
            f.close ()
            return True
        else:
        #append the info to the unfound list
            f = file (lyricsfolder + "/missingsongs.txt", 'a')
            f.write (artistname + " : " + songname +"\n")
            f.close ()
            if verbose: print "Failed to find lyrics for song: %s  :  %s" % (artistname, songname)
            return False
    else:
        if verbose: print "Lyrics file already exist for: %s  :  %s" % (artistname, songname)
        f = file (lyricfile, 'r')
        lyrics = mReplace(f.read(),wordDict).split('\n')
        printlyrics(lyrics)
        f.close ()
        return True

def main():
    artistname = commands.getoutput("mpc --format %artist% | head -n 1").lower()
    songname = commands.getoutput("mpc --format %title% | head -n 1").lower()
    if not songname or not artistname: sys.exit(infoErr) 
    elif verbose: print "Artist: %s        Songname: %s" % ( artistname, songname)
    if checkmissing(artistname,songname): 
        sys.exit()
    if getlyrics(artistname,songname) is False:
		sys.exit(1)
    
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False, help="request verbose output.")
    parser.add_option("-a", "--align", dest="align",metavar="VALUE" , help='''Add an alignment setting for conky (${alignr},${alignc},${goto}). Make sure to single quote the arguments so that bash doesn't interpret it as a variable. This option is still experimental.''')
    (options, args) = parser.parse_args()
    if options.verbose: 
        verbose = True
    else: verbose = False
    if options.align: 
       align =  options.align
    else: align = ''
    
    main()
    sys.exit()
