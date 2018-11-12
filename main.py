import class_logger
import class_config
import class_MongoDB
import requests
import re
from lxml import etree
import time
import json
import random
import string


def getProxy():
    return class_config.getProxy()


# 初始化logger:Crawl
logger = class_logger
logger.init()
main_logger = logger.getLogger('Spider')
phone_pool = class_config.Phone()
phone_pool.next()


# 初始化dbc
dbc = class_MongoDB.MongoClient(class_config.Mongo_uri, logger.getLogger('PYMG-DB'), 'pymh')
dbc.setUnique('info', 'url')
dbc.setUnique('sent', 'clone_url')
dbc.setUnique('ignore', 'url')
dbc.setUnique('published', 'url')

while 1:
    HaveNext = True
    i = 1
    # 当前日期
    now_date = time.strftime("%m-%d", time.localtime())

    hrefList = []
    # 是否需要爬下一页
    while HaveNext == True:
        # 构造URL
        url = "http://www.pymh.com/House/HouseSell.aspx?flag=&page=%i" % (i)
        # 发送请求, proxies = getProxy()
        retry = 0
        while retry < 3:
            try:
                response = requests.get(url=url).text
                time.sleep(1)
                break
            except:
                retry += 1
               ###0000

        # 用etree解析
        selector = etree.HTML(response)
        try:
            links = selector.xpath('//div[@class="list"]/div[2]')
        except Exception as e:
            print(e)

        for link in links:
            # 定位
            href = link.xpath('ul/li[1]/a/@href')[0]
            date = link.xpath('ol/text()')[0]
            date = re.findall(r'(\d+-\d+)', date)[0]
            # 是否采集完成今日的
            # if now_date != date:
            #     HaveNext = False
            #     break

            # 这里设置爬取的页数
            if i == class_config.yeshu:
                HaveNext = False
                break
            # 判断这篇消息是不是自己发的
            if dbc.isexisted('ignore', {'url': href}) == False:
                if dbc.isexisted('info', {'url': href}) == False:
                    if dbc.isexisted('sent', {'clone_url': href}) == False:
                        main_logger.info('获取到任务链接 -> ' + href)
                        hrefList.append(href)
                    else:
                        main_logger.info('数据库中已存在 -> ' + href)
                        break
                else:
                    main_logger.info('数据库中已存在 -> ' + href)
                    break
        # HaveNext = False
        i += 1
        time.sleep(1)
    main_logger.info("获取到 %i 条信息" % len(hrefList))


    # 爬取每间房子的信息
    nownum = 0
    for s in range(len(hrefList)):
        nownum += 1

        i = hrefList[len(hrefList) - 1 - s]
        url = 'http://www.pymh.com' + i
        retry = 0
        while retry < 3:
            try:
                response = requests.get(url=url, proxies=getProxy())
                time.sleep(1)
                break
            except:
                retry += 1

        # 处理编码
        response.encoding = 'utf-8'
        response = response.text
        # 解析网页
        selector = etree.HTML(response)
        ig = False
        for p in class_config.phone_arr:
            if str(p) in response:
                ig = True

        if ig == False:
            try:
                title = selector.xpath('//div[@class="showTitle"]/text()')
                if title != []:
                    title = re.sub(r'\s+', '', title[0])
                else:
                    title = ''

                fullinfo = {
                    'url': i,
                    'title': title,
                    # 'imgs': [],
                    'date':now_date,

                 }

                infos = selector.xpath('/html/body/div[6]/div[1]/div[2]/ul/li/span/text()')
                # print(infos)
                # 拼接 处理数据
                if len(infos) > 0:
                    fullinfo['小区'] = infos[0]
                if len(infos) > 1:
                    fullinfo['地址'] = infos[1]
                if len(infos) > 2:
                    fullinfo['身份'] = infos[2]
                if len(infos) > 3:
                    fullinfo['面积'] = infos[3]
                if len(infos) > 4:
                    # 正则处理 金额数据
                    pay = re.findall(r'(\d+)', infos[4])
                    if len(pay) > 0:
                        fullinfo['价格'] = pay[0]
                    else:
                        fullinfo['价格'] = '0'
                if len(infos) > 5:
                    fullinfo['装修'] = infos[5]
                if len(infos) > 6:
                    fullinfo['户型'] = infos[6]
                if len(infos) > 7:
                    fullinfo['类型'] = infos[7]
                if len(infos) > 8:
                    fullinfo['楼层'] = infos[8]
                else:
                    fullinfo['楼层'] =''
                pt = selector.xpath('/html/body/div[6]/div[1]/div[5]/div[2]/text()')
                if len(pt) > 0:
                    fullinfo['配套设施'] = pt[0]
                else:
                    fullinfo['配套设施'] = ''
                #其他描述的内容替换手机号为''
                try:
                    pt = selector.xpath('//div[@class="showCon"]/text()')
                    if pt == []:
                        fullinfo['其他描述'] = ' 加微信<span style="color:#E53333;"><strong>15265136678</strong></span>'
                    else:
                        pt = re.sub(r"1\d{10}", '', pt[0])
                        fullinfo['其他描述'] = pt + ' 加微信<span style="color:#E53333;"><strong>15265136678</strong></span>'
                except Exception as e:
                    print(e)
                    print(pt)


                # imgs = selector.xpath('//img/@src')
                #
                # # 提取图片
                # for img in imgs:
                #     if 'UploadFiles' in img:
                #         fullinfo['imgs'].append(img)
                main_logger.info('-----------------------------------------------------------------')
                main_logger.info('标题    ' + fullinfo.get('title'))
                main_logger.info('面积    ' + fullinfo.get('面积'))
                main_logger.info('小区    ' + fullinfo.get('小区'))
                main_logger.info('价格    ' + fullinfo.get('价格'))
                main_logger.info('楼层    ' + fullinfo.get('楼层'))
                if len(pt) > 0:
                    main_logger.info('描述    ' + pt)
                main_logger.info('-----------------------------------------------------------------')
                # dbc.insert_one('info', fullinfo)
            except Exception as e:
                main_logger.warn('198行错误')
                print(title,url)
            # 开始提交发布信息 #########################################################################

            # 获取请求数据源
            s = requests.session()
            s.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
                # 'Content-Type': 'multipart/form-data;',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Referer': 'http://www.pymh.com/Member/PubInfo/House.aspx',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.8',
                'Origin': 'http://www.pymh.com',
                'Upgrade-Insecure-Requests': '1'
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
                # 'Content-Type': 'multipart/form-data;',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Referer': 'http://www.pymh.com/Member/PubInfo/House.aspx'
            }
            # headers = {'User-Agent': ' Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
            s.proxies = getProxy()
            err_num = 0
            while 1:


                url = 'http://www.pymh.com/Member/PubInfo/House.aspx'
                retry = 0
                while retry < 3:
                    try:
                        response = s.get(url=url, proxies=getProxy())
                        time.sleep(1)
                        break
                    except:
                        main_logger.info('227行错误')
                        retry += 1

                # 处理编码
                try:
                    if type(response) != 'str':
                        response.encoding = 'utf-8'
                except Exception as e:
                    print(e)
                try:
                    response = response.text
                except AttributeError as e:
                    response = str(response)
                    # print('不是对象是str'+e)
                # 解析网页
                selector = etree.HTML(response)
                try:
                    __VIEWSTATE = selector.xpath('//*[@id="__VIEWSTATE"]/@value')[0]
                    __VIEWSTATEGENERATOR = selector.xpath('//*[@id="__VIEWSTATEGENERATOR"]/@value')[0]
                    normal_s = "ctl00$ContentPlaceHolder1$"
                    yzm = selector.xpath('//*[@id="ctl00_ContentPlaceHolder1_AuthCode"]')[0]
                    # print(yzm.xpath('img/@src'))
                    #图片验证码 对照表
                    if yzm.xpath('img/@src') != []:
                        # imgcode = rk.RClient(rk_username, rk_password).rk_create(s.get('http://www.pymh.com' + yzm.xpath('img/@src')[0]).content, 5000)['Result']
                        key = yzm.xpath('img/@src')[0]
                        # print(imgcode)
                        yzm = class_config.capth[key]
                        break
                    #文字验证码
                    if len(yzm.xpath('text()')) > 0:
                        text = yzm.xpath('text()')[0]
                        if '-' in text or '+' in text:
                            text = text.replace('=', '')
                            yzm = str(eval(text))
                        else:
                            yzm = text
                        # print(yzm)
                        break
                except:
                    main_logger.info('响应出错except等待5分钟后尝试')

                    print('出错信息为: ' + response)
                    time.sleep(10*60)

            # 切割户型
            if '户型' in fullinfo.keys():
                arr = re.findall(r'(\d+)', fullinfo['户型'])
            else:
                arr = ''
            # 处理楼层
            if '楼层' in fullinfo.keys():
                floor = fullinfo['楼层']
            else:
                floor = ''
            # main_logger.info('开始拼接数据')
            Files = [
                (None, 'application/x-zip-compressed'),
                (None, 'application/x-zip-compressed'),
                (None, 'application/x-zip-compressed')
            ]

            # i = 0

            # for img in fullinfo['imgs']:
            #     try:
            #         Files[i] = (str(i) + '.jpg', requests.get(url=img).content, 'imeg/jpeg')
            #     except:
            #         Files[i] = (None, 'application/x-zip-compressed')
            #     i += 1
            # 随机码

            try:
                salt = ''.join(random.sample(string.ascii_letters, 1))
                # 判断随机字符串的开与关 开关在class_config里
                dic = ["    ", "!", "...", "-", "。"]
                # name = ['男房东', '房多多', '卖房子', '房子多', '加微信', '好房子']
                if class_config.random_Control:
                    t_phone = phone_pool.get() + salt
                else:
                    t_phone = phone_pool.get()


                fullinfo['phone'] = t_phone
                data = {
                    '__VIEWSTATE': __VIEWSTATE,
                    '__VIEWSTATEGENERATOR': __VIEWSTATEGENERATOR,
                    'ctl00$ContentPlaceHolder1$HouseClass': '出售',
                    'ctl00$ContentPlaceHolder1$HouseTitle': fullinfo.get('title') + random.choice(dic),
                    'ctl00$ContentPlaceHolder1$ZhongJie': '是',
                    'ctl00$ContentPlaceHolder1$XiaoQu':fullinfo.get('小区','key不存在,可能没填小区') ,
                    'ctl00$ContentPlaceHolder1$HouseAddr': '平邑',
                    'ctl00$ContentPlaceHolder1$Shi': '',
                    'ctl00$ContentPlaceHolder1$Ting': '',
                    'ctl00$ContentPlaceHolder1$Wei': '',
                    'ctl00$ContentPlaceHolder1$Yang': '',
                    'ctl00$ContentPlaceHolder1$ZhuangXiu': '',
                    'ctl00$ContentPlaceHolder1$HouseLeixing': '',
                    'ctl00$ContentPlaceHolder1$LouCeng': floor,
                    'ctl00$ContentPlaceHolder1$LouCeng2': floor,
                    'ctl00$ContentPlaceHolder1$MianJi': re.findall(r'(\d+)', fullinfo.get('面积','key错误，可能没填面积')),
                    'ctl00$ContentPlaceHolder1$JiaGe': fullinfo.get('价格'),
                    'file': '',
                    'ctl00$ContentPlaceHolder1$contents': fullinfo.get('其他描述') + random.choice(dic),
                    'ctl00$ContentPlaceHolder1$Person': random.choice(class_config.name),
                    'ctl00$ContentPlaceHolder1$Tel': t_phone,
                    'ctl00$ContentPlaceHolder1$QQ': '',
                    'ctl00$ContentPlaceHolder1$Email': '',
                    'ctl00$ContentPlaceHolder1$DelPwd': '666666',
                    'ctl00$ContentPlaceHolder1$YZM': yzm,
                    'ctl00$ContentPlaceHolder1$PubBT.x': '57',
                    'ctl00$ContentPlaceHolder1$PubBT.y': '29',
                    'Hidden1': '',
                }
                # print(data)
                # main_logger.info('数据拼接完成,开始提交')
#----------------------------------------------------------发帖----------------------------------------------------------
                url = 'http://www.pymh.com/Member/PubInfo/House.aspx'
                response = s.post(url, data=data, headers=headers)
                response.encoding = 'utf-8'
                selector = etree.HTML(response.text)
                # arr_re = ''
                # try:
                #
                #     pub_info = selector.xpath('//div[@class="pubOk_str"]/text()')
                #     if pub_info != []:
                #         pub_info = pub_info[0]
                #     else:
                #         pub_info = ''
                #     main_logger.info(pub_info)
                #     dbc.insert_one('published', fullinfo)

                # except:
                arr_re = re.findall("alert\('(.*?)'\)", response.text)
                # print(arr_re)
                if arr_re != []:
                    main_logger.info(arr_re[0])
                    if arr_re[0] == '您今天发布的信息已超过最系统设定最大值，请明天再来吧！':
                        phone_pool.next()
                        nownum -= 1
                    elif arr_re[0] == '请不要重复发布信息！明天再来吧。':
                        continue
                else:
                    pub_info = selector.xpath('//div[@class="pubOk_str"]/text()')
                    print(pub_info)
                    dbc.insert_one('published', fullinfo)

                select_num = dbc.select_num(t_phone,now_date)
                select_num_all = dbc.select_num(None,now_date)

                # 保存记录
                upload = {}
                upload['clone_url'] = fullinfo['url']
                upload['clone_url'] = fullinfo['url']
                upload['time'] = time.time()
                upload['salt'] = salt
                # upload['msg'] = arr_re
                dbc.insert_one('sent', upload)
                # main_logger.info(upload)
            except Exception as e:
                main_logger.info()
                print(e)
            yc = random.randint(58,70)
            main_logger.info(
                '==========%s==【%s】====== 【 %i/%i 】 ' % ((t_phone),select_num, nownum, select_num_all) + "============%s秒继续..." % yc)
            time.sleep(yc)

        else:
            main_logger.info('发现自己发的帖子')
            dbc.insert_one('ignore', {'url': i, 'type': 'spider'})

