# coding=utf-8
from optparse import OptionParser
import re, urllib2, socket
import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool
from colorama import Fore
from gevent.queue import Queue
import requests,json, hashlib,gevent,time


__author__ = 'Hexman'


def cmsreg_main_thread():
    pass



def cmsreg_start_thread(url):
    cmsreg_ThreadPool = ThreadPool(processes=20)
    cms_result = [cmsreg_thread.get() for cmsreg_thread in [threadpool.map_async(cmsreg_main_thread, url)]]
    print cms_result
    return "something"



def cmsreg_start_processes():
    cmsreg_ProcessesPool = multiprocessing.Pool(processes=20)
    result_url = [cms_reg.get() for cms_reg in [threadpool.map_async(cmsreg_start_thread, out)]]



class gwhatweb(object):
    def __init__(self, url):
        self.tasks = Queue()
        self.url = url.rstrip("/")
        fp = open('cmslist1.json')
        webdata = json.load(fp, encoding="utf-8")
        for i in webdata:
            self.tasks.put(i)
        fp.close()
        print(Fore.LIGHTBLUE_EX+"[*]webdata total:%d" % len(webdata))

    def _GetMd5(self, body):
        m2 = hashlib.md5()
        m2.update(body)
        return m2.hexdigest()

    def _clearQueue(self):
        while not self.tasks.empty():
            self.tasks.get()

    def _worker(self):
        data = self.tasks.get()
        test_url = self.url + data["url"]
        rtext = ''
        try:
            r = requests.get(test_url, timeout=10)
            if (r.status_code != 200):
                return
            rtext = r.text
            if rtext is None:
                return
        except:
            rtext = ''

        if data["re"]:
            if (rtext.find(data["re"]) != -1):
                result = data["name"]
                print(Fore.LIGHTGREEN_EX+"[+]CMS:%s" % (result))
                self._clearQueue()
                return True
        else:
            md5 = self._GetMd5(rtext)
            if (md5 == data["md5"]):
                result = data["name"]
                print(Fore.LIGHTGREEN_EX+"[+]CMS:%s" % (result))
                self._clearQueue()
                return True

    def _boss(self):
        while not self.tasks.empty():
            self._worker()

    def whatweb(self,):
        maxsize = 100
        start = time.clock()
        allr = [gevent.spawn(self._boss) for i in range(maxsize)]
        gevent.joinall(allr)
        end = time.clock()
        print (Fore.BLUE+"[*]cms reg cost: %f s" % (end - start))



def urlscaner(path):
    try:
        url = "%s%s" % (domain_name, path)
        status_code = requests.head(url, timeout=0.5).status_code
        if status_code == 200:
            print (Fore.LIGHTGREEN_EX + url)
            return "[" + str(status_code) + "]" + url
        elif status_code == 403:
            print (Fore.LIGHTRED_EX + "[403]" + url)
            return "[" + str(status_code) + "]" + url
        elif status_code == 301 or status_code == 302:
            print (Fore.LIGHTWHITE_EX + "[" + str(status_code) + "]" + url)
            return "[" + str(status_code) + "]" + url
        elif status_code == 500:
            print (Fore.LIGHTYELLOW_EX + "[500]" + url)
            return "[" + str(status_code) + "]" + url
        else:
            print (Fore.WHITE + url + "[" + str(status_code) + "]" + url)
    except requests.exceptions.Timeout:
        print (Fore.LIGHTRED_EX+"[-]Timeout")
    except UnicodeDecodeError:
        pass
    except requests.exceptions.ConnectionError:
        print (Fore.LIGHTRED_EX+"[-]ConnectionError")



def pangurl(ip):
    search_ip = 'http://cn.bing.com/search?q=ip:' + ip + '&count=200'
    response = urllib2.urlopen(search_ip)
    content = response.read()
    reg_url = r'<cite>(.*?)</cite>'
    reg_url_res = re.compile(reg_url)
    pangs=[x.split("/")[0][::-1].rstrip(">etic<")[::-1] for x in re.findall(reg_url_res, content)]
    printout=pangs
    for i in printout:
        if i=="p.chinaz.com":
            continue
        elif i == "https:":
            continue
        else:
            print (Fore.LIGHTGREEN_EX + "[+]" + i)
    return pangs



def caddress(ip):
    ciplist=range(256)
    for i in range(256):
        ciplist[i]=".".join(ip.split(".")[0:3])+"."+str(i)
    return ciplist



def caddlist():
    outa = []
    pool = multiprocessing.Pool(processes=20)
    result=[x.get() for x in [pool.map_async(pangurl,caddress(ip))]]
    pool.close()
    pool.join()
    for res in result:
        if res !=[]:
            for _count in res:
                for lis in _count:
                    outa.append(lis)
    print (Fore.LIGHTBLUE_EX+"c address gets done.")
    print (Fore.LIGHTBLUE_EX+"Sub-process(es) done.")
    return outa



if __name__ == "__main__":
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-u", "--url", action='store', dest="url", default=False, help="url")
    parser.add_option("-c", "--CDuan", action="store_true", dest="caddress", default=False, help="c address")
    parser.add_option("-p", "--PangZhan", action="store_true", dest="pzhan", default=False, help="same host")
    parser.add_option("-a", "--auto", action="store_true", dest="auto", default=False, help="auto scan")
    parser.add_option("-d", "--dic", action="store", dest="dir", default=False,help="dic file")
    parser.add_option("-r", "--reg", action="store_true", dest="cms", default=False, help="cms reg")
    (options, args) = parser.parse_args()
    if(options.url):
        urls=[]
        ip = socket.gethostbyname(options.url.strip("https://"))
        if(options.pzhan and options.caddress):
            urls=caddlist()
        elif(options.pzhan):
             pang_out=pangurl(ip)
             for i in pang_out:
                if i == "p.chinaz.com":
                    pang_out.remove("p.chinaz.com")
                elif i == "https:":
                    pang_out.remove("https:")
             if pang_out!=[]:
                for pang_strs in pang_out:
                    print (Fore.LIGHTGREEN_EX + "[+]" + pang_strs)
             else:
                print (Fore.LIGHTWHITE_EX+"[-]The host don't have any other website.")
        elif(options.caddress):
            urls=caddlist()
        if urls!=[]:
            out= {}.fromkeys(urls).keys()
            print (Fore.LIGHTBLUE_EX + "[*]starting remove the same website")
            if "p.chinaz.com" in out:
                out.remove("p.chinaz.com")
            elif "https:" in out:
                out.remove("https:")
            with open('websites.txt', 'w') as f:
                for strs in out:
                    f.write(strs + "\n")
            print (Fore.LIGHTGREEN_EX + "[*]done")
            print (Fore.LIGHTGREEN_EX + "[*]save as websites.txt")
            #print out
        if options.dir:
            start_urlscan = time.clock()
            domain_name = options.url
            lines = open(options.dir, 'r')
            threadpool=ThreadPool(processes=20)
            result_url=[result_url_scan.get() for result_url_scan in [threadpool.map_async(urlscaner,lines)]]
            print (Fore.LIGHTBLUE_EX+"[*]url scan done")
            end_urlscan = time.clock()
            print (Fore.LIGHTBLUE_EX + "=======================result=======================")
            print (Fore.LIGHTBLUE_EX + "=                                                  =")
            print (Fore.LIGHTBLUE_EX + "=              [*]url scan cost: %f s        =" % (end_urlscan - start_urlscan))
            print (Fore.LIGHTBLUE_EX + "=                                                  =")
            print (Fore.LIGHTBLUE_EX + "=======================result=======================")
            with open('urlscan.txt', 'w') as f:
                for strs in result_url[0]:
                    if strs==None:
                        continue
                    else:
                        if strs.split("]")[0]=="[200":
                            print (Fore.LIGHTGREEN_EX+strs)
                        elif strs.split("]")[0]=="[302" or strs.split("]")[0]=="[301":
                            print (Fore.LIGHTWHITE_EX+strs)
                        elif strs.split("]")[0]=="[403":
                            print (Fore.LIGHTRED_EX+strs)
                        elif strs.split("]")[0]=="[500":
                            print (Fore.LIGHTYELLOW_EX+urls)
                        f.write(strs +"\n")
            print (Fore.LIGHTBLUE_EX+"[+]done.")
        if options.cms:
            g = gwhatweb(options.url).whatweb()

    else:
        print "url input error"

