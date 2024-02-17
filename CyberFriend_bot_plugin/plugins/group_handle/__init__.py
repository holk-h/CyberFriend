from nonebot import on_request, logger
from nonebot.adapters.onebot.v11 import Bot, GroupRequestEvent, RequestEvent
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="自动同意群邀请",
    description="自动同意特定用户拉入群的邀请。",
    usage="插件无需手动操作，自动运行。"
)

auto_accept_group_invite = on_request()

ALLOWED_USER_IDS = {1599840925}

@auto_accept_group_invite.handle()
async def handle_group_invite(bot: Bot, event: RequestEvent):
    logger.warning(f"收到来自 {event.user_id} 的群邀请")
    # 确保邀请来自特定用户
    if event.user_id in ALLOWED_USER_IDS:
        # 使用正确的bot实例回应请求
        await bot.set_group_add_request(
            flag=event.flag,
            sub_type=event.sub_type,
            approve=True,
            reason=" "
        )
