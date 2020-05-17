#!/usr/bin/env python
# -*- coding: utf-8 -*-
from aip import AipFace
from picamera import PiCamera
import urllib.request
import RPi.GPIO as GPIO
import base64
import time
import Main

#百度智能云人脸识别id、key
APP_ID = '*****'
API_KEY = '**********'
SECRET_KEY ='**********'
client = AipFace(APP_ID, API_KEY, SECRET_KEY)#创建一个客户端用以访问百度云
#图像编码方式
IMAGE_TYPE='BASE64'
camera = PiCamera()#定义一个摄像头对象
#用户组
GROUP = 'usr1'
 
#照相函数
# def getimage():
#     camera.resolution = (1024,768)#摄像界面为1024*768
#     camera.start_preview()#开始摄像
#     time.sleep(1)
#     camera.capture('faceimage.jpg')#拍照并保存
#     time.sleep(1)
#     camera.close()

# 对图片的格式进行转换
def transimage():
    f = open('faceimage.jpg','rb')
    img = base64.b64encode(f.read())
    return img


#上传到百度api进行人脸检测
def go_api(image):
    result = client.search(str(image, 'utf-8'), IMAGE_TYPE, GROUP);#在百度云人脸库中寻找有没有匹配的人脸
    if result['error_msg'] == 'SUCCESS':#如果成功了
        name = result['result']['user_list'][0]['user_id']#获取名字
        score = result['result']['user_list'][0]['score']#获取相似度
        if score < 80:#如果相似度大于80
            print("对不起，我不认识你！")
            name = 'Unknow'
            return 0
        curren_time = time.asctime(time.localtime(time.time()))#获取当前时间
 
        #将人员出入的记录保存到Log.txt中
        f = open('Log.txt','a')
        f.write("Person: " + name + "     " + "Time:" + str(curren_time)+'\n')
        f.close()
        return 1
    if result['error_msg'] == 'pic not has face':
        # print('检测不到人脸')
        time.sleep(2)
        return 1
    else:
        print(result['error_code']+' ' + result['error_code'])
        return 0
#主函数
if __name__ == '__main__':
    print('准备')
    # getimage()#拍照
    img = transimage()#转换照片格式
    res = go_api(img)#将转换了格式的图片上传到百度云
    if res == 1:#是人脸库中的人
        print("正常")
    else:
        print("出现陌生人")
    print('等40s进入下一轮')
    time.sleep(1)

