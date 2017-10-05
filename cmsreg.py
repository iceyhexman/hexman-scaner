from gevent.queue import Queue
import requests,json, hashlib,gevent,time

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

    def whatweb(self, maxsize=1000):
        start = time.clock()
        allr = [gevent.spawn(self._boss) for i in range(maxsize)]
        gevent.joinall(allr)
        end = time.clock()
        print (Fore.BLUE+"[*]cms reg cost: %f s" % (end - start))
