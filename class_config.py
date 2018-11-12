# encoding=utf-8
import random

'''
配置文件
'''
Mongo_uri = 'mongodb://127.0.0.1:27017'
Logger_file = 'spider.log'
name = ['男房东','卖房子','加微信','看朋友圈','钱','微信联系','李','周','微信说','郑','王','微信聊','房东']
#爬去页数 1页10条信息
yeshu = 12
phone_arr = [


    13002794560,#360手机卡2
    15969737356,#360手机卡1 流量卡
    18315678345,#诺基亚小手机
    15866969887,#华为
    15265136678,#华为
    # 13157039456,#华为手机虚拟号
    # 13059722456,#虚拟号
    # 15054636979, #秋姐

]
#验证码映射表
capth = {
    '/UserFiles/image/authCode/yzm3.gif': '2539',
    '/UserFiles/image/authCode/yzm2.gif': '7410',
    '/UserFiles/image/authCode/yzm1.gif': '5079',
    '/UserFiles/image/authCode/WEg5.gif': 'dveb',
    '/UserFiles/image/authCode/V1fw6epp.jpg': 'pxfxy',
    '/UserFiles/image/authCode/RlE8qOWXMFcZyrI0tO1.jpg': '2edfwa',
    '/UserFiles/image/authCode/image_validate_code.png': '2t9w',
    '/UserFiles/image/authCode/gQXrO1222RZ6D.jpg': '35ntd',
    '/UserFiles/image/authCode/eqwg5t.gif': '运但',
    '/UserFiles/image/authCode/e1.gif': 'axyr',
    '/UserFiles/image/authCode/76ht.gif': '政过',
    '/UserFiles/image/authCode/13.bmp': 'hxqc',
    '/UserFiles/image/authCode/12.bmp': '37fy',
    '/UserFiles/image/authCode/10.bmp': '100',
    '/UserFiles/image/authCode/8.bmp': '9',
    '/UserFiles/image/authCode/6.bmp': '105',
    '/UserFiles/image/authCode/5.bmp': '25',
    '/UserFiles/image/authCode/4.bmp': '68',
    '/UserFiles/image/authCode/3.bmp': '68',
    '/UserFiles/image/authCode/2dR.gif': 'bywk',
    '/UserFiles/image/authCode/2.bmp': '110',
    '/UserFiles/image/authCode/1u04.gif': '清它',
    '/UserFiles/image/authCode/1.bmp': '11',
    '/UploadFiles/AuthCode/17155253.jpg': 'ja88',
    '/UploadFiles/AuthCode/17155032.jpg': 'frdv',
    '/UploadFiles/AuthCode/1715510.jpg': 'spel'
}
random_Control = False


def getProxy():
    return None

    # Example
    # """
    # return {
    #    'http': 'http://HOW031537AC7GX8D:96798EA82DD43C41@http-dyn.abuyun.com:9020',
    #    'https': 'http://HCM5DK0600NB102D:66EDD0692F673188@http-dyn.abuyun.com:9020'
    # }    # """


class Phone:
    phone = ''
    now = 0

    def __init__(self):
        pass

    def get(self):
        return self.phone

    def next(self):
        if self.now < len(phone_arr):
            self.phone = str(phone_arr[self.now])
            self.now += 1
        else:

            print('手机号已用完')
            exit()
        return self.phone
