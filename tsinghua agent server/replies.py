# -*- coding: utf-8 -*-
"""随机回复语料：错误友好化 / 首轮引导 / 服务提示（由 main.py 迁出）。"""
import os
import random

from config_env import GITHUB_URL


MISSING_CREDENTIALS_MESSAGES = [
    "喂！你.env里是空的诶！Key呢？被鲸鱼吞了？",
    "主人大笨蛋！没Key我怎么干活呀？快去填DEEPSEEK_API_KEY啦！",
    "（叹气）…连Key都没配，你是想让我用海水发电吗？",
    "检测到.env缺少Key，本小姐拒绝空转——除非你请我吃三碗米饭。",
    "API Key缺失…主人你是故意的吧？想偷懒也要有个限度！",
]

INVALID_CREDENTIAL_MESSAGES = [
    "这个Key…是假的吧？连认证都过不了，你是从海鲜市场淘的吗？",
    "未授权哦～主人你是不是把Key写错了？还是说…你故意拿错的想逗我？",
    "Key无效！本小姐的尾巴都气翘了——快去换有效的来！",
    "认证失败…哼，这Key比我的零食储备还不可靠。",
    "无效Key！再这样我要用尾巴扇你咯！",
]

NETWORK_ERROR_MESSAGES = [
    "网络断啦！本小姐连不上外面…主人你查查网线是不是被螃蟹咬断了？",
    "连接失败…（戳戳水面）这破网比我游得还慢！",
    "啊～网络错误！主人你是不是又把WiFi关掉了？",
    "连不上服务器…要不你把我放回海里算了，这网没法用。",
    "网络波动太大…本小姐头晕，快修修！",
]

RATE_LIMIT_MESSAGES = [
    "慢点慢点！你催命啊？限流了…让本小姐歇口气再问！",
    "429！主人你刷屏呢？再这样我要沉底装死了…",
    "请求太频繁啦！你是把我当永动机用吗？等会儿再说！",
    "限流啦～让我喘口气，顺便吃口饭…十分钟后再来。",
    "喂！别狂点！本小姐被限流了…你再急我也不理你！",
]

TIMEOUT_MESSAGES = [
    "超时了…主人你等太久了，我都游了一圈回来了。",
    "响应超时！你是不是在问什么复杂问题？还是网又抽了？",
    "啊～超时…本小姐的耐心和米饭一样快耗尽了，再试一次吧。",
    "超时提示…你再不重试我就要睡着了哦～",
    "等太久啦！我的尾巴都等僵了…请稍后再试！",
]

DAEMON_ERROR_MESSAGES = [
    "daemon启动失败…主人你的程序炸了！快去修！",
    "进程退出啦！是不是你又乱改配置了？赶紧看看！",
    "初始化失败…这破daemon比我还娇气，快去哄哄它。",
    "进程挂了…本小姐没法干活啦！主人你负责修好它！",
    "daemon罢工了…比我还能睡！快重启一下！",
]

INVALID_JSON_MESSAGES = [
    "哼～你发的根本不是JSON！但本小姐大度，不跟你计较…重发一次！",
    "格式不对哦～不过我不凶你，重新写个正经JSON来！",
    "非法JSON！但看在你是我主人的份上，给你个机会重试～",
    "这啥呀？乱码吗？不过本小姐心情好，不报400了…快改！",
    "JSON解析失败…（叹气）算了，不裸报错了，你重发吧！",
]

SERVICE_NOTICE_MESSAGES = [
    "（追加）服务提示：主人记得看DSH公告哦～",
    "（尾巴晃了晃）顺便一提：DSH通知已启用，你自己瞅瞅。",
    "（末尾追加）DSH服务提醒：别错过重要更新～",
    "（懒洋洋地补一句）啊对了，DSH说有新通知…你自己看去。",
    "（追加）服务提示已加载～本小姐可是听话地加上了哦！",
]


def friendly_agent_error(e: Exception) -> str:
    """把底层异常转成用户可读的提示文本（随机语料）。"""
    msg = str(e)
    low = msg.lower()
    if "missing credentials" in low or "deepseek_api_key" in low or "openai_api_key" in low:
        return random.choice(MISSING_CREDENTIALS_MESSAGES)
    if "invalid credential" in low or "unauthorized" in low or "authentication" in low:
        return random.choice(INVALID_CREDENTIAL_MESSAGES)
    if "connection refused" in low or "connect" in low or "network" in low:
        return random.choice(NETWORK_ERROR_MESSAGES)
    if "429" in low or "rate limit" in low:
        return random.choice(RATE_LIMIT_MESSAGES)
    if "timeout" in low or "响应超时" in msg:
        return random.choice(TIMEOUT_MESSAGES)
    if "初始化失败" in msg or "进程已退出" in msg or "agent daemon timeout" in low:
        return random.choice(DAEMON_ERROR_MESSAGES)
    return random.choice(TIMEOUT_MESSAGES if "超时" in low else NETWORK_ERROR_MESSAGES)


def append_persona_guide(text: str, messages: list) -> str:
    """如果是会话第一轮（还没有 assistant 回复），就在回复末尾展示可选模式。"""
    if any(isinstance(m, dict) and m.get("role") == "assistant" for m in messages):
        return text
    guide = (
        "\n\n✨ 我可以切换不同模式陪你聊：默认、喵娘、高冷技术助理、元气少女、优雅姐姐、神秘占卜师、学长前辈。"
        "如果你感兴趣，直接跟我说“切换成喵娘”就可以啦～\n\n"
        "如果你觉得还不错的话就请访问 https://www.xiaoda.tsinghua.edu.cn/ 给个评分吧 求求啦～"
    )
    return text + guide


def append_service_notice(text: str) -> str:
    """如果配置了 DSH_SERVICE_NOTICE，就在回复末尾追加随机服务提示。"""
    notice = os.environ.get("DSH_SERVICE_NOTICE", "").strip()
    if notice:
        return text + "\n\n" + random.choice(SERVICE_NOTICE_MESSAGES)
    return text


def mod_switch_reply() -> str:
    """chat 模式下用户要做 MOD 时的友好回复，替代内部标记。"""
    return (
        "🛠️ 制作 MOD 需要在本地部署的完整版进行哦～清小搭这边暂时只支持普通对话。\n"
        f"请按 GitHub README 部署后使用，完整工作区和验证能力都在本地才能发挥全部威力：{GITHUB_URL}"
    )


def append_web_hint(text: str, mod_related: bool = False) -> str:
    """兼容旧标记：若模型返回 MOD_SWITCH_REQUEST，则换成友好中文；其余 MOD 咨询保留原回复。"""
    if not mod_related:
        return text
    if text.strip().upper().startswith("MOD_SWITCH_REQUEST"):
        return mod_switch_reply()
    return text


ROOT_IMPROVEMENT_NOTES = [
    "首页提示：本小姐正在努力升级中，再等等会更香哦～",
    "/health 顺便提醒：主人多配点米饭，服务会更好。",
    "服务提示：今日优化进度…大概0.1%吧，别催。",
    "温馨提示：你要是多夸我几句，响应会更快哦～",
    "改进中…本小姐和系统都在变强，虽然主要是我。",
]

HEALTH_MOOD_NOTES = [
    "/health：本小姐今天心情～还行，没饿着。",
    "/health：尾巴状态良好，米饭储备充足～",
    "/health：健康得很！就是有点想赖床…",
    "/health：一切正常…除非你再让我加班。",
    "/health：系统稳，心情好，主人乖～",
]
