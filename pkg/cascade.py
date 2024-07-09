# 导入所需库
import websocket # NOTE: 需要安装websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
import json
import urllib.request
import urllib.parse
import random
import os
from PIL import Image
import io
 
# 设置服务器地址和客户端ID
server_address = "127.0.0.1:8188"
#server_address = "4pxpnwu8asdjz5h7-8188.container.x-gpu.com"
client_id = str(uuid.uuid4())
output_dir = r'plugins/Comfyui_qbot/output_images'  # 输出文件夹路径
os.makedirs(output_dir, exist_ok=True)  # 如果文件夹不存在，则创建
 
# 定义向服务器发送提示的函数
def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())
 
# 定义从服务器下载图像数据的函数
def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
        return response.read()
 
# 定义获取历史记录的函数
def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())
 
# 定义通过WebSocket接收消息并下载图像的函数
def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):    
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break # 执行完成
        else:
            continue # 预览是二进制数据
 
    history = get_history(prompt_id)[prompt_id]
    #print(history['outputs'])
    for node_id in history['outputs']:
        #print(node_id)
        node_output = history['outputs'][node_id]
        #print(node_output,'\n\n', node_id)
        if 'images' in node_output:
            images_output = []
            for image in node_output['images']:
                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                images_output.append(image_data)
            output_images[node_id] = images_output
 
    return output_images
 
def change_prompt(prompt):  #更改prompt
    #prompt["6"]["inputs"]["text"] = "masterpiece best quality man"
    prompt["3"]["inputs"]["seed"] = random.randint(0, 2147483647)
    prompt["33"]["inputs"]["seed"] = random.randint(0, 2147483647)
    #prompt["4"]["inputs"]["ckpt_name"] = "darkSushiMixMix_225D.safetensors"
    #prompt["11"]["inputs"]["lora_name"] = "2.5D美少女_绚丽时尚Gorgeous fashion _v1.0.safetensors"
    #prompt["14"]["inputs"]["contro_net_name"] = "control_v11p_sd15_openpose.pth"
    #prompt["6"]["inputs"]["text"] ="(best quality, masterpiece),1girl,animate,niji" #positive prompt
    #prompt["7"]["inputs"]["text"] ="nsfw,simplified, abstract, unrealistic, impressionistic, low resolution, face paint, face tattoo," #negative prompt
    prompt["34"]["inputs"]["batch_size"] = "1"
    #prompt["17"]["inputs"]["image"] = r"1.png"
    
    
    return
 
def generate(msg = "(best quality, masterpiece),1girl,animate,niji"):
     
 
    # 示例JSON字符串，表示要使用的提示
    with open(os.path.join(os.path.dirname(__file__), 'cascade.json'), encoding='utf-8') as prompt_text:
    
        # 将示例JSON字符串解析为Python字典，并根据需要修改其中的文本提示和种子值
        prompt = json.load(prompt_text)

    change_prompt(prompt)
    prompt["6"]["inputs"]["text"] = msg #positive prompt
    # 创建一个WebSocket连接到服务器
    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    
    # 调用get_images()函数来获取图像
    images = get_images(ws, prompt)
    
    # 显示输出图像（这部分已注释掉）
    #Commented out code to display the output images:
    
    for node_id in images:
         for idx, image_data in enumerate(images[node_id]):
            image = Image.open(io.BytesIO(image_data))
            file_path = os.path.join(output_dir, f"{client_id}_{idx}.png")
            absolute_path = os.path.abspath(file_path)
            image.save(file_path)  # 保存图像到文件
            print(f"Saved image to {absolute_path}")

            image.show()
            return absolute_path
             
    

if __name__ == "__main__":
    print(generate())