import requests
import base64

# 下载图像并转为base64
def encode_image_from_url(image_url):
    # 下载图像
    response = requests.get(image_url)
    if response.status_code == 200:
        # 将图像内容转为base64
        return "data:image/jpeg;base64," + base64.b64encode(response.content).decode('utf-8')
    else:
        return None