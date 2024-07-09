from pkg.plugin.events import *
from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
from pkg.command.operator import CommandOperator, operator_class
from plugins.Comfyui_qbot.pkg import cascade, sd3 
from mirai import Image, Plain
import os
import yaml

backend_mapping = {
    "cascade": cascade.generate,
    "sd3": sd3.generate,
}
process: callable = None

# 增加指令
#@operator_class(name="comfyui", help="comfyui random/status/switch", privilege=1)
#class SwitchVoicePlugin(CommandOperator):
#
#    # 控制语音合成的开关
#    async def execute(self, context: entities.ExecuteContext) -> typing.AsyncGenerator[entities.CommandReturn, None]:
#        global ifVoice
#        global language
#
#        if context.crt_params[0] == "on":
#            self.ap.logger.info("启动语音合成")
#            ifVoice = True
#            yield entities.CommandReturn(text="启动语音合成")
#
#        elif context.crt_params[0] == "off":
#            self.ap.logger.info("关闭语音合成")
#            ifVoice = False
#            yield entities.CommandReturn(text="关闭语音合成")
#
#        elif context.crt_params[0] == "status":
#            if ifVoice:
#                yield entities.CommandReturn(text="语音合成状态:已开启" + f"，当前语言为{language}")
#            else:
#                yield entities.CommandReturn(text="语音合成状态:已关闭")
#
#        elif context.crt_params[0] == "language":
#
#            reply = "语言列表：\n 中文  英文    日文"
#                    
#
#            yield entities.CommandReturn(text=reply.strip())
#
#        elif context.crt_params[0] == "switch":
#           
#           language = context.crt_params[1]
#           self.ap.logger.info(f"切换语音合成语言为{language}")
#           yield entities.CommandReturn(text=f"切换语音合成语言为{language}")
#
#        elif context.crt_params[0] == "帮助":
#            yield entities.CommandReturn(text="vits插件支持的指令有：\n"
#                                              "!vits on\n"
#                                              "!vits off\n"
#                                              "!vits status\n"
#                                              "!vits language\n"
#                                              "!vits switch\n"
#                                              "!vits help\n")
#
#        else:
#            yield entities.CommandReturn(error="无效指令，请输入\"!vits help\"查看帮助")


# 注册插件
@register(name="comfyui", description="调用comfyui api进行绘画", version="0.0", author="logos")
class ComfyuiPlugin(BasePlugin):


    # 插件加载时触发
    # plugin_host (pkg.plugin.host.PluginHost) 提供了与主程序交互的一些方法，详细请查看其源码
    def __init__(self, plugin_host: APIHost):
        global process
        
        with open(os.path.join(os.path.dirname(__file__), 'config.yml'), 'r', encoding='utf-8') as f:
            self.cfg = yaml.safe_load(f)
        process = backend_mapping[self.cfg["backend"]]


    # 当收到消息时触发
    @handler(PersonNormalMessageReceived)
    @handler(GroupNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):
        msg = ctx.event.text_message  # 这里的 event 即为 PersonNormalMessageReceived 的对象
        if msg.startswith('paint'):
            # 输出调试信息
            self.ap.logger.debug("paint {}".format(ctx.event.sender_id))

            msg = msg.replace('paint', '').strip()
            # 回复消息 "generating"
            #ctx.add_return("reply", ["Please wait, generating……"])

            if msg != "":
                image_path = process(msg)
            else:
                image_path = process()
            #img_obj = [Image(base64=i.replace('\n', '')) for i in images]
            ctx.add_return("reply", [Image(path = str(image_path))])
            # 阻止该事件默认行为（向接口获取回复）
            ctx.prevent_default()
        
    # 插件卸载时触发
    def __del__(self):
        pass
