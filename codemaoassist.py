#import requests as r
#import json
#import sys
#import time


class CaError(BaseException):
    def __init__(self, err, text, the_lines, content, msg):
        """自定义异常类:UnRightUrlError即不正确的网址"""
        """UnCompteteError即不齐全的内容"""
        """IntFloatButStrError即期待整数或小数，却得到字符串的错误"""
        """UnRightContentError即不正确的内容"""
        self.err = err
        self.text = text
        self.msg = msg
        self.the_lines = the_lines
        self.content = content

    def paochu(self):
        print("————————————————————" + self.err + "————————————————————")
        if self.the_lines == "none":
            #没提供源代码行号
            print("源代码出错行号：未提供")
        else:
            #提供了源代码行号
            print("源代码出错行号：" + str(self.the_lines))

        print("出错内容：" + str(self.content))
        print("出错原因：" + self.text)
        print("详细原因：" + self.msg)
        exit()




class Ca():
    def __init__(self):
        """初始化“Ca对象”"""
        pass

    def one(self, content={}):
        """最简单的方式：刷一次浏览"""

        start_time = time.time()

        #先格式化数据
        try:
            #源代码行号
            lines = str(content["lines"])
        except KeyError:
            lines = "none"

        try:
            #是否有提示
            prompt = content["prompt"]
        except KeyError:
            prompt = False

        try:
            try:
                #必须参数：目标网址和目标类型
                url = int(content["url"])
                if url < 0:
                    raise CaError("UnRightContentError", "目标的信息内容错误！", lines, content, "目标ID不可小于0！")

                t = content["t"]
                if t != "novel":
                    if t != "wiki":
                        raise CaError("UnRightContentError", "目标的信息内容错误！", lines, content, "目标类型必须为novel或wiki！")
            except KeyError:
                raise CaError("UnCompleteError", "目标的信息基本格式错误！", lines, content, "目标缺少ID或类型！")
            except ValueError:
                raise CaError("IntFloatButStrError","目标的信息类型错误！", lines, content, "目标的ID必须为或能转换成int类型！")
        except CaError as e:
            e.paochu()  # 抛出异常

        try:
            try:
                #超时时间
                timeout = float(content["timeout"])
            except ValueError:
                raise CaError("IntFloatButStrError","目标的信息类型错误！", lines, content, "目标的超时时间必须为或能转换成float类型！")
            except KeyError:
                timeout = 2#默认超时时间为2
        except CaError as e:
            e.paochu()

        try:
            try:
                #间隔时间
                interval = float(content["interval"])
            except ValueError:
                raise CaError("IntFloatButStrError", "目标的信息类型错误！", lines, content, "目标的间隔时间必须为或能转换成float类型！")
            except KeyError:
                interval = 1  # 默认间隔时间为1
        except CaError as e:
            e.paochu()

        try:
            try:
                #次数
                times = int(content["times"])
            except ValueError:
                raise CaError("IntFloatButStrError", "目标的信息类型错误！", lines, content, "目标的次数必须为或能转换成int类型！")
            except KeyError:
                times = 1  # 默认次数为1
        except CaError as e:
            e.paochu()

        try:
            #头部
            headers = content["headers"]
        except KeyError:
            headers = "none"

        #检查格式
        if t == "novel":
            realurl = "https://shequ.codemao.cn/wiki/novel/cover/" + str(url)
            url = "https://api.codemao.cn/api/fanfic/" + str(url)
        else:
            realurl = "https://shequ.codemao.cn/community/" + str(url)
            url = "https://api.codemao.cn/web/forums/posts/" + str(url) + "/details"    

        try:
            if interval < 0 or timeout < 0 or times < 1:
                raise CaError("UnRightContentError", "目标的信息内容错误！", lines, content, "目标的间隔必须大于等于0，或超时时间必须大于等于0，或次数必须大于等于1！")
        except CaError as e:
            e.paochu()


        #开始迭代get
        i = 0
        failed = 0
        many = []
        name = "404NotFound"
        while i < times:
            try:
                if headers == "none":
                    web = r.get(url, timeout=timeout)
                else:
                    web = r.get(url, timeout=timeout, headers = headers)
                html = web.json()

                try:
                    if web.status_code == 200:
                        try:
                            if html["code"] == 404:
                                #小说的空页面不会返回404，而是返回一个json数组，其中"code"键的值为"404"
                                raise CaError("404NotFoundError", "目标不存在！", lines, "返回数据中“code”键的值为404！")
                        except KeyError:
                            pass
                    elif web.status_code == 404:
                        #帖子的空页面则会返回404
                        raise CaError("404NotFoundError", "目标不存在！", lines, content, "目标页面返回404！")
                except CaError as e:
                    e.paochu()

                if t == "wiki":
                    #帖子的json，浏览量为["n_views"],标题为["title"]
                    many.append(html["n_views"])
                    name = "“" + html["title"] + "”"
                #elif self.var == 2:
                    #作品的json，浏览量为["view_times"],标题为["work_name"]
                #    self.many.append(html["view_times"])
                #    self.name = html["work_name"]
                else:
                    #小说的json，浏览量为["view_times"],标题为["title"]
                    many.append(html["data"]["fanficInfo"]["view_times"])
                    name = "《" + html["data"]["fanficInfo"]["title"] + "》"

            except r.exceptions.RequestException as e:
                if prompt:
                    print("————————————————————r.exceptions.RequestException————————————————————")
                failed += 1

            

            i = i+1
            time.sleep(interval)

        self.url = str(realurl)
        self.name = str(name)
        self.times = str(times)
        self.failed = str(failed)
        self.start = str(many[0])
        self.end = str(many[-1])
        self.timeout = str(timeout)
        self.interval = str(interval)
        self.spend = str(time.time() - start_time)

        if prompt:
            print("————————————————————OK!————————————————————")
            print("目标地址：" + realurl)
            print("目标名称：" + name)
            print("浏览次数：" + str(times))
            print("超时次数：" + str(failed))
            print("开始浏览：" + str(many[0]))
            print("结束浏览：" + str(many[-1]))
            print("超时上限：" + str(timeout))
            print("间隔时间：" + str(interval))
            print("所用时间：" + str(time.time() - start_time))