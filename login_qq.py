#coding=utf-8
import urllib2
import re
import random
import cookielib
import json
import threading
from encryption import QQmd5
import datetime
import verifyImg as verifyImg
import time
import sys

DEBUG = True

'''
self.user       : 用户QQ名,可以为邮件地址
self.cookie     : 没有opener之前用来保存cookie的,给跪了....
self.pwd        : 用户密码
self.friend     : 好友列表信息
self.group      : 群组列表信息
self.categories : 好友分组
self.msg_queue  : 收到的消息队列
self.gid        : 群ID->群名字
self.gname      : 群名字->群ID
self.uin        : 用户ID->用户名字
self.markname   : 用户备注->用户ID
self.nick       : 用户昵称->用户ID
self.cat        : 用户ID->分组
self.gcode      : 群ID->群信息
self.clientid   : 随机生成的客户端ID
'''

import urllib
class webqq(threading.Thread):
    def __init__(self, user, pwd, msg_queue):
        threading.Thread.__init__(self)
        #self.cookies = cookielib.CookieJar()
        self.cookies = cookielib.MozillaCookieJar()
        try:
            self.cookies.load('res/loginGet.cookie')
            self.cookies.load('res/loginPost.cookie')
            self.cookies.load('res/getGroupList.cookie')
            self.cookies.load('res/getFriend.cookie')
            print '成功读取cookie并加载'
            print self.cookies
        except Exception as e:
            print '读取cookie失败', str(e)
        self.opener = urllib2.build_opener(
                urllib2.HTTPHandler(),
                urllib2.HTTPSHandler(),
                urllib2.HTTPCookieProcessor(self.cookies),
                )
        urllib2.install_opener(self.opener)
        self.user = user
        self.pwd = pwd
        self.mycookie = ";"
        #self.clientid = "21485768"
        #self.clientid = "34592990"
        self.clientid = str(random.randint(10000000, 99999999))
        self.friend = None
        self.group = None
        self.categories = None
        self.msg_queue = msg_queue
        self.success_login = False
        self.login_cnt = 0
        self.login_fail = False

    def getSafeCode(self):
        url = (
                'https://ssl.ptlogin2.qq.com/check?uin='  +
                str(self.user) + '&appid=1003903&js_ver=10017&js_type=0'
                '&login_sig=0ihp3t5ghfoonssle-98x9hy4uaqmpvu*8*odgl5vyerelcb8fk-y3ts6c3*7e8-'
                '&u1=http%3A%2F%2Fweb2.qq.com%2Floginproxy.html&r=' + str(random.random())
                )
        req = urllib2.Request(url)
        #self.mycookie += "confirmuin=" + self.user + ";"
        #req.add_header('Cookie', self.mycookie)
        req  = urllib2.urlopen(req)
        #cs = ['%s=%s' %  (c.name, c.value) for c in self.cookies]
        #self.mycookie += ";".join(cs)
        verifycode = re.search(r"'(\d)','(.+)','(.+)'", req.read())
        self.check = verifycode.group(1)
        self.verifycode1 = verifycode.group(2)
        self.verifycode2 = verifycode.group(3)
        if self.check == "1" or self.login_fail:
            url = 'https://ssl.captcha.qq.com/getimage?&uin='+str(self.user)+'&aid=1002101&0.45644426648505' + str(random.randint(10,99))
            req = urllib2.Request(url)
            req = urllib2.urlopen(req)
            self.fi = open("res/verifyImg.jpg", "wb")
            while 1:
                c = req.read()
                if not c:
                    break
                else :self.fi.write(c)
            self.fi.close()
            #verifyImg.main('res/verifyImg.jpg')
            self.verifycode1 = raw_input("verifer:")
        if DEBUG:print self.check, self.verifycode1, self.verifycode2

    def loginGet(self):
        #cs = ['%s=%s' %  (c.name, c.value) for c in self.cookies]
        #self.mycookie += ";" "; ".join(cs)

        login_url = (
                'https://ssl.ptlogin2.qq.com/login?u='+self.user
                + '&p=' + str(QQmd5().md5_2(self.pwd, self.verifycode1, self.verifycode2))
                + '&verifycode=' + self.verifycode1
                + '&webqq_type=10'
                '&remember_uin=1'
                '&login2qq=1'
                '&aid=1003903'
                #'&u1=http%3A%2F%2Fweb.qq.com%2Floginproxy.html%3Flogin2qq%3D1%26webqq_type%3D10'
                '&u1=' + str(urllib.quote('http://web2.qq.com/loginproxy.html?login2qq=1&webqq_type=10')).replace('/', '%2f')
                +'&h=1'
                '&ptredirect=0'
                '&ptlang=2052'
                '&daid=164'  # atupal
                '&from_ui=1'
                '&pttype=1'
                '&dumy='
                '&fp=loginerroralert'
                #'&action=2-14-32487'
                '&action=2-34-20120'
                '&mibao_css=m_webqq'
                '&t=1'
                '&g=1'
                '&js_type=0'
                #'&js_ver=10015'
                '&js_ver=10041'
                #'&login_sig=0ihp3t5ghfoonssle-98x9hy4uaqmpvu*8*odgl5vyerelcb8fk-y3ts6c3*7e8-'
                '&login_sig=HW-HptrIEOpShz9pkt4s2aip*VmRQHSV28tVMb9tndUp1liWqE56eAsNYlk0IwAB'
                )

        req = urllib2.Request(login_url)
        req.add_header("Referer", (
                'https://ui.ptlogin2.qq.com/cgi-bin/login?'
                'target=self'
                '&style=5'
                '&mibao_css=m_webqq'
                '&appid=1003903'
                '&enable_qlogin=0'
                '&no_verifyimg=1'
                '&s_url=http%3A%2F%2Fweb.qq.com%2Floginproxy.html'
                '&f_url=loginerroralert&strong_login=1'
                '&login_state=10'
                '&t=20121029001'
            ))

        #req.add_header("Cookie", self.mycookie)
        #self.opener.addheaders.append(("Cookie", self.mycookie))

        req = urllib2.urlopen(req)

        def ptuiCB(*args):
          return args[2]

        if DEBUG or 1:  # TODO(atupal)
            content = req.read()
            print content
            check_sig_url = eval(content.strip().strip('\r\n').strip('\n').strip(';'), {"__builtins__": None}, {'ptuiCB': ptuiCB})
            urllib2.urlopen(check_sig_url)

        try:
            for cookie in self.cookies:
                if DEBUG:
                    print cookie.name, ":",  cookie.value
                if cookie.name == 'ptwebqq':
                    self.ptwebqq = cookie.value
                elif cookie.name == 'uin':
                    self.uin_user = cookie.value
        except Exception as e:
            print e
            self.loginGet()

        if DEBUG:
            print urllib2.urlopen('http://web2.qq.com/web2/get_msg_tip?uin=&tp=1&id=0&retype=1&rc=0&lv=3&t=1358252543124').read()
        #cs = ['%s=%s' %  (c.name, c.value) for c in self.cookies]
        #self.mycookie += ";" "; ".join(cs)
        try:self.cookies.save('res/loginGet.cookie')
        except IOError:pass

    def loginPost(self):
        try:

            url = 'http://d.web2.qq.com/channel/login2'
            data = (
                    'r=%7B%22status%22%3A%22online%22%2C%22ptwebqq%22%3A%22' + self.ptwebqq
                    + '%22%2C%22passwd_sig%22%3A%22%22%2C%22clientid%22%3A%22'
                    +self.clientid+'%22%2C%22psessionid%22%3Anull%7D&clientid='
                    +self.clientid+'&psessionid=null')

            req = urllib2.Request(url, data)
            #req.add_header('Cookie', self.mycookie)
            req.add_header('Referer', 'http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=2')
            req = urllib2.urlopen(req)
            self.result = json.load(req)
            if self.result['retcode'] != 0:
                print self.result['retcode']
                return False
            if DEBUG:
                print '*************************************************'
                print 'vfwebqq, psessionid:', self.result['result']['vfwebqq'], self.result['result']['psessionid']
            try:self.cookies.save('res/loginPost.cookie')
            except IOError:pass
        except Exception as e:
            self.login_cnt += 1
            if self.login_cnt > 10:
                print '登录太频繁, 等待5秒'
                time.sleep(5)
            print e
            self.getSafeCode()
            self.loginGet()
            self.loginPost()

    def getGroupList(self):
        url = 'http://s.web2.qq.com/api/get_group_name_list_mask2'
        data = 'r=%7B%22vfwebqq%22%3A%22'+self.result['result']['vfwebqq'] +'%22%7D'
        req = urllib2.Request(url, data)
        req.add_header('Referer', 'http://s.web2.qq.com/proxy.html?v=20110412001&callback=1&id=1')
        req = urllib2.urlopen(req)
        self.group = json.load(req)['result']
        self.gid = dict()
        self.gname = dict()
        try:
            for g in self.group['gnamelist']:
                self.gid[g['gid']] = g['name']
                self.gname[g['name']] = g['gid']
                pass
        except:
            print '部分群信息拉取失败'
            pass

        print '[INFO] Groups catched.'
        try:self.cookies.save('res/getGroupList.cookie')
        except IOError: pass


    def getFriend(self):
        try:
            url = 'http://s.web2.qq.com/api/get_user_friends2'
            import getFriend2_hash
            cnt = 1
            while self.uin_user[cnt] == '0':
                cnt += 1
            ptwebqq_hash = getFriend2_hash.getFriend_hash(self.uin_user[cnt:], self.ptwebqq)
            #data = 'r=%7B%22vfwebqq%22%3A%22'+self.result['result']['vfwebqq'] +'%22%7D'
            data = ('r=%7B%22h%22%3A%22hello%22%2C%22hash%22%3A%22'
                    +ptwebqq_hash+'%22%2C%22vfwebqq%22%3A%22'
                    +self.result['result']['vfwebqq']+'%22%7D')

            req = urllib2.Request(url, data)
            req.add_header('Referer', 'http://s.web2.qq.com/proxy.html?v=20110412001&callback=1&id=1')
            print 'ptwebqq=' + self.ptwebqq
            print data
            req = urllib2.urlopen(req)
            self.friend_ret = json.load(req)
            self.uin = dict()
            self.markname = dict()
            self.nick = dict()
            self.cat = dict()
            self.friend = self.friend_ret['result']['friends']
            self.categories = self.friend_ret['result']['categories']
            for fri in self.friend:
                self.cat[fri['uin']] = fri['categories']
            for info in self.friend_ret['result']['info']:
                self.nick[info['nick']] = info['uin']
                self.uin[info['uin']] = info['nick']
            for mark in self.friend_ret['result']['marknames']:
                self.markname[mark['markname']] = mark['uin']
                self.uin[mark['uin']] = mark['markname']

            print '好友信息拉取成功!'
            self.success_login = True
            #with open('res/login_cookie', 'w') as f:
            #    f.write(str(self.cookies))
            self.cookies.save('res/getFriend.cookie')
        except Exception as e:
            pass
            '''
            cnt = 1
            while self.uin_user[cnt] == '0':
                cnt += 1
            import getFriend2_hash
            ptwebqq_hash = getFriend2_hash.getFriend2_hash2(self.uin_user[cnt:], self.ptwebqq)
            data = ('r=%7B%22h%22%3A%22hello%22%2C%22hash%22%3A%22'
                    +ptwebqq_hash+'%22%2C%22vfwebqq%22%3A%22'
                    +self.result['result']['vfwebqq']+'%22%7D')
            print 'ptwebqq=' + self.ptwebqq
            print data
            print '获取列表失败,重试中...'

            #print self.friend_ret
            print e
            while not self.getFriend_2():
                self.getFriend_2()
            '''
        else:
            pass

    def getFriend_2(self):
        cnt = 1
        while self.uin_user[cnt] == '0':
            cnt += 1
        import requests
        url = 'http://s.web2.qq.com/api/get_user_friends2'
        headers = {'Referer': 'http://s.web2.qq.com/proxy.html?v=20110412001&callback=1&id=1'}
        import getFriend2_hash
        ptwebqq_hash = getFriend2_hash.getFriend2_hash2(self.uin_user[cnt:], self.ptwebqq)

        data = ('r=%7B%22h%22%3A%22hello%22%2C%22hash%22%3A%22'
                +ptwebqq_hash+'%22%2C%22vfwebqq%22%3A%22'
                +self.result['result']['vfwebqq']+'%22%7D')

        cookies = dict(ptwebqq=str(self.ptwebqq))
        req = requests.post(url, cookies = cookies, data = data, headers = headers)
        #req = requests.post(url,data = data, headers = headers)

        self.friend_ret = json.loads(req.content)
        print '[RESULT]',req.content
        self.uin = dict()
        self.markname = dict()
        self.nick = dict()
        self.cat = dict()
        self.friend = self.friend_ret['result']['friends']
        self.categories = self.friend_ret['result']['categories']
        for fri in self.friend:
            self.cat[fri['uin']] = fri['categories']
        for info in self.friend_ret['result']['info']:
            self.nick[info['nick']] = info['uin']
            self.uin[info['uin']] = info['nick']
        for mark in self.friend_ret['result']['marknames']:
            self.markname[mark['markname']] = mark['uin']
            self.uin[mark['uin']] = mark['markname']

        print '好友信息拉取成功!'
        self.success_login = True
        return True
        #with open('res/login_cookie', 'w') as f:
        #    f.write(str(self.cookies))

    def getMeg(self):
        if DEBUG:
            print urllib2.urlopen('http://web2.qq.com/web2/get_msg_tip?uin=&tp=1&id=0&retype=1&rc=0&lv=3&t=1358252543124').read()
        pass

    def poll2(self):
        try:
            url = 'http://d.web2.qq.com/channel/poll2'
            data =(
                    'r=%7B%22clientid%22%3A%22'+self.clientid
                    +'%22%2C%22psessionid%22%3A%22'
                    +self.result['result']['psessionid']
                    +'%22%2C%22key%22%3A0%2C%22ids%22%3A%5B%5D%7D&clientid='
                    +self.clientid+'&psessionid='
                    +self.result['result']['psessionid']
                    )

            req = urllib2.Request(url, data)
            #req.add_header('Cookie', self.mycookie)
            req.add_header('Referer', 'http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=3')
            result = json.load(urllib2.urlopen(req))
            print result
            #正常返回
            if int(result['retcode']) == 0:
                for res in result['result']:
                    try:
                        content = ''
                        for i in res['value']['content'][1:]:
                            content += str(i)
                        

                        if res['poll_type'] == 'message':
                            #print self.uin[res['value']['from_uin']] \
                             #       ,': ', res['value']['content'][1]
                            print '[MESSAGE]',content.decode().encode('gbk'), res['value']['from_uin']

                            self.msg_queue.put( (self.uin[res['value']['from_uin']]\
                                    + ' ' +  str(datetime.datetime.now()) + '\n' , content, res['value']['from_uin'], 1 ))



                        elif res['poll_type'] == 'group_message':
                            #print self.gid[res['value']['from_uin']] \
                             #       ,': ', res['value']['content'][1]
                             try:
                                 self.msg_queue.put( ( self.gid[res['value']['from_uin']] +'#'+self.uin[res['value']['send_uin']]\
                                         + ' ' +str(datetime.datetime.now()) + '\n', content,
                                    res['value']['from_uin'] , 2))
                             except:
                                 self.msg_queue.put((self.gid[res['value']['from_uin']] +'#'+str(res['value']['send_uin'])\
                                         + ' ' +str(datetime.datetime.now()) + '\n' , content,
                                    res['value']['from_uin'], 2  ))
                        else:
                            #print res
                            pass
                    except:
                        if content != '':
                            pass
                        print content
                        #print res
                        pass
            #新的ptwebqq值
            elif int(result['retcode']) == 116:
                self.ptwebqq = result['p']
            #掉线重连
            elif int(result['retcode']) == 121:
                self.qq = webqq(self.user, self.pwd, self.msg_queue)
                self.qq.getSafeCode()
                self.qq.loginGet()
                self.qq.loginPost()
                self.qq.getGroupList()
                self.qq.getFriend()
            else:
                '''
                buddy status change:
                    0: ol -> off
                    102: off -> ol
                '''
                '''
                self.login_cnt += 1
                if self.login_cnt > 10:
                    print '频繁登录,请等待10s'
                    time.sleep(10)
                self.getSafeCode()
                self.loginGet()
                self.loginPost()
                self.getGroupList()
                self.getFriend()
                '''
                pass
            return
        except Exception as e:
            print e

    def run(self):
        while True:
            self.poll2()


    def sendMsg(self, uin, msg, face=None):
        try:
            uin = str(uin)
            url = 'http://d.web2.qq.com/channel/send_buddy_msg2'
            if face is None:
                data = ('r=%7B%22to%22%3A'+uin+'%2C%22face%22%3A237%2C%22content'
                +urllib.quote(r'":"[\"'+msg
                +r'\",\"\\n【提示：此用户正在使用shift webQq】\",'
                +r'[\"font\",{\"name\":\"宋体\",\"size\":\"10\",\"style\":[0,0,0],\"color\":\"000000\"}]]","')
                +'msg_id%22%3A13190001%2C%22clientid%22%3A%22'
                +self.clientid+'%22%2C%22psessionid%22%3A%22'
                +self.result['result']['psessionid']+'%22%7D&clientid='
                +self.clientid+'&psessionid='
                +self.result['result']['psessionid']
                )
            else:
                data = 'r=%7B%22to%22%3A'+uin+'%2C%22face%22%3A237%2C%22content'+urllib.quote(r'":"[\"'+msg+r'\",\"\\n【提示：此用户正在使用shift webQq】\", [\"face\",'+str(face)+r'],[\"font\",{\"name\":\"宋体\",\"size\":\"10\",\"style\":[0,0,0],\"color\":\"000000\"}]]","')+'msg_id%22%3A13190001%2C%22clientid%22%3A%22'+self.clientid+'%22%2C%22psessionid%22%3A%22'+self.result['result']['psessionid']+'%22%7D&clientid='+self.clientid+'&psessionid='+self.result['result']['psessionid']
                '''
                data = 'r=%7B%22to%22%3A'+uin
                +'%2C%22face%22%3A237%2C%22content'
                +urllib.quote(r'":"[\"'
                +msg+r'\",\"\\n【提示：此用户正在使用shift webQq】\", [\"face\",'
                +str(face)+r'],[\"font\",{\"name\":\"宋体\",\"size\":\"10\",\"style\":[0,0,0],\"color\":\"000000\"}]]","')
                +'msg_id%22%3A13190001%2C%22clientid%22%3A%22'
                +self.clientid+'%22%2C%22psessionid%22%3A%22'
                +self.result['result']['psessionid']+'%22%7D&clientid='
                +self.clientid+'&psessionid='
                +self.result['result']['psessionid']
                '''
            req = urllib2.Request(url, data)
            #req.add_header('Cookie', self.mycookie)
            req.add_header('Referer', 'http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=2')
            if DEBUG: urllib2.urlopen(req).read()
        except Exception as e:
            print e

    def sendQunMsg(self, uin, msg, face = None):
        try:
            uin = str(uin)
            url = 'http://d.web2.qq.com/channel/send_qun_msg2'
            if face is None:
                data = 'r=%7B%22group_uin%22%3A'+uin+'%2C%22face%22%3A237%2C%22content'+urllib.quote(r'":"[\"'+msg+r'\",\"\\n【提示：此用户正在使用shift webQq】\",[\"font\",{\"name\":\"宋体\",\"size\":\"10\",\"style\":[0,0,0],\"color\":\"000000\"}]]","')+'msg_id%22%3A13190001%2C%22clientid%22%3A%22'+self.clientid+'%22%2C%22psessionid%22%3A%22'+self.result['result']['psessionid']+'%22%7D&clientid='+self.clientid+'&psessionid='+self.result['result']['psessionid']
                '''
                data = 'r=%7B%22group_uin%22%3A'+uin
                +'%2C%22face%22%3A237%2C%22content'
                +urllib.quote(r'":"[\"'
                        +msg+r'\",\"\\n【提示：此用户正在使用shift webQq】\",'
                        +r'[\"font\",{\"name\":\"宋体\",\"size\":\"10\",\"style\":[0,0,0],\"color\":\"000000\"}]]","')
                +'msg_id%22%3A13190001%2C%22clientid%22%3A%22'
                +self.clientid+'%22%2C%22psessionid%22%3A%22'
                +self.result['result']['psessionid']
                +'%22%7D&clientid='+self.clientid
                +'&psessionid='+self.result['result']['psessionid']
                '''
            else:
                data = 'r=%7B%22group_uin%22%3A'+uin+'%2C%22face%22%3A237%2C%22content'+urllib.quote(r'":"[\"'+msg+r'\",\"\\n【提示：此用户正在使用shift webQq】\", [\"face\",'+str(face)+r'], [\"font\",{\"name\":\"宋体\",\"size\":\"10\",\"style\":[0,0,0],\"color\":\"000000\"}]]","')+'msg_id%22%3A13190001%2C%22clientid%22%3A%22'+self.clientid+'%22%2C%22psessionid%22%3A%22'+self.result['result']['psessionid']+'%22%7D&clientid='+self.clientid+'&psessionid='+self.result['result']['psessionid']
                '''
                data = 'r=%7B%22group_uin%22%3A'+uin
                +'%2C%22face%22%3A237%2C%22content'
                +urllib.quote(r'":"[\"'
                        +msg+r'\",\"\\n【提示：此用户正在使用shift webQq】\", [\"face\",'
                        +str(face)+r'], [\"font\",{\"name\":\"宋体\",\"size\":\"10\",\"style\":[0,0,0],\"color\":\"000000\"}]]","')
                +'msg_id%22%3A13190001%2C%22clientid%22%3A%22'
                +self.clientid+'%22%2C%22psessionid%22%3A%22'
                +self.result['result']['psessionid']
                +'%22%7D&clientid='+self.clientid
                +'&psessionid='+self.result['result']['psessionid']
                '''
            req = urllib2.Request(url, data)
            req.add_header('Referer', 'http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=2')
            if DEBUG:print urllib2.urlopen(req).read()
        except Exception as e:
            print e

    def request(self, url, methods = ['GET', 'POST'], data = None, referer = None, user_agent = None, origin = None, host = None):
            req = urllib2.Request(url)
            if data       : req.add_data(data)
            if referer    : req.add_header('Referer', referer)
            if user_agent : req.add_header('User-Agent', user_agent)
            if origin     : req.add_header('Origin', origin)
            if host       : req.add_header('Host', host)
            req = urllib2.urlopen(req)
            return req.read()

    def getCookie(self, name):
        for c in self.cookies:
            if c.name == name:
                return c.value
        return None

def run():
    #user = raw_input('QQ:')
    #pwd = getpass.getpass('password: ')
    import os
    try:
        user = os.environ['QQ']
        pwd = os.environ['QQ_PASSWD']
    except:
        import getpass
        user = raw_input('QQ:')
        pwd = raw_input('password:')
    queue = Queue.Queue()
    qq = webqq(user, pwd, queue)
    qq.getSafeCode()
    qq.loginGet()
    qq.loginPost()
    qq.getGroupList()
    qq.getFriend()
    print 'DEAMON'
    while 1:
        qq.poll2()
        continue
    for i in range(100):
        if DEBUG:print 'to', qq.friend['info'][0]['uin']
        if DEBUG:print 'to', qq.group['gnamelist'][10]
        #qq.sendMsg(str(qq.friend['result']['info'][0]['uin']), 'clientjsfzhiyong')
        ms = ''
        for _ in xrange(i):
            ms += '。'
        qq.sendQunMsg(str(qq.group['gnamelist'][10]['gid']), ms)
        #qq.sendMsg('2236071402', 'geisf')


import Queue

if __name__ == "__main__":
    run()
