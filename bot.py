import asyncio
import logging
import math
import os
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime, timedelta

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CopyTextButton,
)
from telegram.error import BadRequest, Forbidden, RetryAfter
from telegram.ext import (
    Application,
    ApplicationHandlerStop,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =====================================================
# BOT SETTINGS
# =====================================================

TOKEN = os.environ.get("BOT_TOKEN", "").strip()
ADMIN_IDS = {8485299821}

CHANNELS = (
    ("@X_Ankitsopurts", "https://t.me/X_Ankitsopurts"),
    ("@yutabothub", "https://t.me/yutabothub"),
)

DB_NAME = "bot_users.db"
HISTORY_LIMIT = 10
FAVORITES_LIMIT = 10
PAGE_SIZE = 10
JOIN_CACHE_SECONDS = 120

# Colored buttons (Telegram button "style"). If Telegram rejects them,
# the bot switches them off automatically and keeps working.
COLORS = {"on": True}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


# =====================================================
# DESIGN TEMPLATES
# {name}     -> name as typed
# {name_dec} -> every letter followed by a small decoration mark
# =====================================================

DESIGNS = {
    "premium": [
        "🝐꯭𐏓꯭꯭ ⃪🤍𝄄𝄀꯭𝄄꯭ ‌⃪{name} 𝅥‌꯭𝆬‌🍫 𝅥‌꯭𝆬‌ ⃪𝄄𝄀꯭𝄄꯭⎯‌꯭⟶⋆",
        "⎯᪵⎯꯭‌❃⃪꯭‌{name}꯭᪵𝆺꯭𝅥᪵⎯꯭‌⎯꯭💎",
        "𝆺꯭𝅥◄❥‌‌⃟⃝🥀⛦⃕‌ {name}⛦⃕‌❍𝆭𝐏─𝄄꯭꯭𝄄꯭꯭ 𝅥‌꯭𝆬‌🪷",
        "⎯꯭꯭֯‌ ⃪꯭⃛𝂍⃨⃜{name}꯭ ꯭⃜🚬⃪⃜𝅃꯭᳚༎‌꯭꯭➛",
        "𝁘 ໍ {name} 🤍⤹ 𓆪𓂃𔘓",
        "𓆩꯭〬ᬊ꯭{name}𝄢꯭‌‌⃪➤⃝꯭🍷꯭𔘓꯭⃭𝘅꯭𝗗꯭𓆪꯭ꪾ",
        "⎯᪵𓆩〭〬{name}𓆪ᮀ⎯꯭‌ꭗ‌‌➛",
        "⎯꯭‌𓆩꯭{name}𓆪꯭〝‌ ˈˈ‌🌜‌",
        "🦋✨{name}✨🦋",
        "💓{name}:)",
        "𓂃 ࣪˖ ִֶָ {name} 🎀",
        "⌁{name}༎‌꯭",
        "•𝁘ໍ𓈒𝀚‌🦚⃝⃪{name}𓆪ꪾˎ𓂃ֶꪳ",
        "⏤‌‌‌‌{name}‌Ꭼ𝚴Ѻ™🐉",
        # ---- new premium designs ----
        "𐏓𐏓꯭꯭ ⃪꯭꯭꯭꯭꯭🇲꯭꯭꯭꯭꯭꯭꯭꯭꯭꯭ɢ֟፝]꯭꯭꯭꯭〠꯭꯭꯭꯭꯭᭄꯭꯭꯭꯭{name_dec}𝅃꯭᳚𝆺꯭𝅥",
        "𐏓𐏓꯭꯭ ⃪꯭꯭꯭꯭꯭🇲꯭꯭꯭꯭꯭꯭꯭꯭꯭꯭ɢ֟፝]꯭꯭꯭꯭〠꯭꯭꯭꯭꯭᭄꯭꯭꯭꯭{name_dec}᪳̄᪻᪱𝅃꯭᳚𝆺꯭𝅥",
        "𝄀𝅛᷼𝄀𓋈𝆭𖡡꯭𖧹꯭⃔𖤓꯭𝆭{name_dec}⃜⃛𖤓꯭⃕𖧹꯭𝆭𖡡𓋈𝄀᷼𝅛𝄀",
        "⎯꯭꯭᪵⎯꯭꯭̽🍂꯭꯭͎᪳ ⃪꯭꯭{name_dec}𝅃꯭꯭𝆺꯭꯭𝅥⎯꯭꯭⟶꯭꯭͇̽",
        "⊹₊𓏲{name}𝆊 🐩ᩚ᮫",
        ".𝁘ໍ {name} ~| 𓂃•",
        "ᯓ𓆰꧊᱂ {name} ꧊᱂ 🤍",
        ".𝁘ໍ {name} ~ ♡ ™| 𓂃•",
        "⏤꯭꯭͟͟͞🦅⃝⃪꯭꯭꯭꯭⌯꯭꯭‖꯭꯭ට{name_dec}‖꯭꯭ ꯭꯭ ꯭꯭⤹꯭꯭🤍𓍯꯭꯭𓂃꯭꯭",
        "⋆꯭꯭⎯꯭꯭𝅃꯭꯭᳚𝆺꯭꯭𝅥༎꯭꯭ࠫ{name_dec}༎꯭꯭ࠫ٭⃪꯭꯭⃜🔥꯭꯭𝆺꯭꯭𝅥𔘓꯭꯭𖥫꯭꯭",
        "⃪🇲ʀ֟፝ {name}𝅃᳚𝆺𝅥",
        "𐏓𐏓 ⃪🇲ʀ֟፝]〠᭄{name}𝅃᳚𝆺𝅥",
        "⟶͇̽ꭘ꯭͓̽ꗝ༎꯭꯭ࠫ{name_dec}𝆺꯭𝅥🐰꯭༎꯭ࠫ⛧꯭ٖٖٖٖٖٖٜٖٖٖٖ",
        "🝐꯭𐏓꯭꯭➺꯭𝅯𝅯ͥͥͥͥͥͥ⃟꯭ⷨⷨⷨⷨ𓆩꯭〭⃛〬𓆩꯭{name_dec}𝆺𝅥⸼̶꯭͠♥️꯭།͢ ꯭𝄄꯭꯭꯭꯭𝄄⃪꯭꯭꯭𝅯",
        "⋆⎯꯭̽𝅃꯭᳚𝆺𝅥༎ࠫ𝆺꯭𝅥{name_dec}༎ࠫ٭⃪꯭꯭꯭⃜🫀꯭𝆺꯭𝅥𔘓•꯭◡̈",
        "𓄂꯭꯭‌≛⃝꯭꯭꯭‌꯭𒉓꯭꯭‌꯭{name_dec}˝꯭꯭꯭😈꯭𐎭꯭❥꯭┼",
        "ᯓ꯭𓆰𝅃꯭᳚ ⃪♔꯭͢༎꯭𓄂️꯭{name_dec}🔥|ا꯭🜲꯭ ꯭༏༏",
        "🝐꯭𐏓꯭꯭𝄄꯭꯭꯭꯭𝄄꯭꯭꯭❚🧿꯭{name}‌ا۬͢𝆺𝅥⃝❤️‍🩹𝄄꯭꯭𝄄꯭꯭꯭",
        "⏤֯🍫᭥{name}⎯᪳ꭙ",
        "⟶͇̽ꭘ꯭͓̽ꗝ༎꯭꯭ࠫ{name_dec}𝆺꯭𝅥🤳༎꯭ࠫ⛧꯭ٖٖٖٖٖٖٜٖٖٖٖ",
        "●꯭꯭⏤꯭꯭͟͟͞͞🕊️꯬꯭꯭𓆩꯭꯭{name_dec}𓆪꯭꯭̥ ꯭꯭𝅥‌꯭꯭𝆬‌꯭꯭°꯭꯭🪼꯭꯭᪳⎯꯭꯭ͯ⟶꯭꯭⋆꯭꯭",
    ],

    "aesthetic": [
        "⎯꯭‌🤍⃝〭𝆭〬{name} -꯭᪵ᥫ꯭᭡𓂃꯭ ,",
        "ꞋꞌꞋ{name} 🎀 𓄹",
        "𝀚𝆭‌ꪳ{name}🦋𝅯‌𓂃",
        "⎯᪵⎯𐎓⃝꯭꯭🌷꯭ ⃪꯭{name}𝄄꯭𝆺꯭꯭𝆭💗",
        "⤹⌯ {name}⤹°𝅯⃮𖹭᷎᷉",
        "⎯⎯‌꯭꯭{name} ꯭🌷",
        "꯭𝆭𝆭‌‌{name}𝆭 ⃝꯭𝆹𝅥‌‌☜꯭",
        "🌷꧍{name}𔘓‌𝆟🫧𓂃ꪸ𝆔.",
        "✧⃝꯭✨𓆩{name}𓆪✨⃝꯭✧ °🦋°",
        "ㅤㅤ⏤ {name} 🤍",
        "••ᯓ❥ {name} ‹‹/𝟑",
        "🌙꯭𓆩꯭{name}𓆪꯭🌙 °👼🏻°",
        "🪷𐬹𓍼 {name} 𓍢ִ໋🪷",
        "🦅👑꯭{name}꯭👑🦅 𝂈✨",
        "🌸⃝〬𓆩 {name} 𓆪⃝〬🌸 𝂈🤍",
    ],

    "fancy": [
        "𝐍𝐀𝐌𝐄 𝐌𝐀𝐊𝐄𝐑 𝐁𝐎𝐓 ♥🥀:\n{name}",
        "⎯᪵⎯⎯᪶᳚𓆩᪶𝆅{name}𖾓ᷱ᪳𑩖𝂨",
        "⋆⎯⃪{name}𖾓ᷱ᪳𝁛",
        "𝂃{name}𝞃",
        "𝀚᧘{name}𝁛゙˳ ໋",
        "⎯ٜ𝅃⃪᳚🎨ꤦꤦꤦٜ ⃪⃝{name}•⃪ꤦꤦٜ᭡ᰪ𓂃",
        "⎯ ⃪💝⃪{name}⃪𝆅",
        "⋆𝁘ໍ🍥ꠦꠋ{name}𔓎᪳𔓗๋𓂃",
        "𝁘〬᧘{name}𝁜๎",
        "|𝆺𝅥𝆭⋆{name}𝆺𝅥.🫀",
        "⎯𝅃᳚♥️ ⃪⃝{name}•᭡𝆭ᥫ᭡゙𓂃",
        "🤍⃝⃪᪲🩷⃖{name}🌸᪵᪳᪳𝆺𝅥𝆬⎯⟶᯦",
        "⎯࣮ໍ𝁘゙ฺ𝆆{name}👒⃪𝁛ࣰ໋",
        "⎯ࣲ⎯ꪷ꯬៱{name}⎯𐚁𝆆𝁛𝆥",
        "𝁑𝁠{name}𝇄𝆆🦩𝁜",
        "𓆩⃪〭〬🍭⃪⃕⃔ໍ{name}💕𝆭⎯⎯𝁤",
        "𓆩֪ۤ{name}᭧",
        "⃪⃛ ៱{name}𓂃𝆊᪽🐼",
        "•{name}🖤",
        "⟶‌‌𓆩〭〬༲🥃{name} ༎ࠫ🖤",
        "🌸⃝⃘⃜{name}♡︎〭〬𓆪⟶",
        "🎬-★𓆩⃝{name}𓆪★-🛍",
        "⟶‌‌𓆩〭〬༲🥃 {name} ༎ࠫ🖤⟵‌",
        "𝁎🕷⃟⃪ {name} 🕸️˵𝁛",
        "𝁘𝂅⬎‌‌{name}🤍⬎‌",
        "🐼꯭🧋⃝⃨⃜ {name} 🧋꯭⃝⃨⃜🐼",
    ],
}

CATEGORY_NAMES = {
    "premium": "👑 Premium Design",
    "aesthetic": "🌷 Aesthetic Design",
    "fancy": "✨ Fancy Design",
}


# =====================================================
# BIO LISTS
# =====================================================

BIO_ATTITUDE = [
    "👑 Born To Rule, Not To Follow",
    "😎 Silent But Dangerous",
    "🔥 My Life My Rules",
    "👑 Royal Blood Never Fades",
    "⚡ No Attitude, Just Personality",
    "🖤 Alone But Happy",
    "🚀 Dream Big, Stay Silent",
    "😈 I Am My Own Hero",
    "👑 King Of My Own World",
    "🔥 Haters Are My Motivation",
    "💯 Believe In Yourself",
    "🦁 Lion Never Follows Sheep",
    "⚡ Different From Others",
    "😎 Not Perfect, Just Original",
    "👑 मेरा अंदाज़ ही अलग है",
    "🔥 औकात नहीं, पहचान बनाओ",
    "🖤 दिल साफ, अंदाज़ नवाबी",
    "😈 हम बदलते नहीं, निखरते हैं",
    "👑 नाम छोटा, पहचान बड़ी",
    "⚡ वक्त आने दो",
    "🦅 उड़ान अपनी अलग है",
    "🔥 खुद की दुनिया का बादशाह",
    "💯 जो हूँ, वही दिखता हूँ",
    "😎 Copy नहीं, Original हूँ",
    "👑 Respect Is Everything",
    "🖤 No Fake Friends",
    "⚡ Attitude In My DNA",
    "🔥 Make History",
    "🦁 Fearless Soul",
    "👑 Royal Mindset",
    "😈 My Silence Is My Power",
    "💎 Rare By Nature",
    "🚀 Focus On Success",
    "🔥 Never Give Up",
    "🖤 खुद से मुकाबला है",
    "👑 अपनी पहचान खुद बनानी है",
    "⚡ हम अपनी मर्जी के मालिक",
    "😎 Simple But Classy",
    "🦅 Sky Is Not The Limit",
    "💯 मेहनत मेरी पहचान",
    "👑 राजा बनने का शौक नहीं",
    "🔥 Level अलग है",
    "🖤 No Comparison",
    "😈 Born Unique",
    "⚡ Mindset Matters",
    "👑 मेरा समय भी आएगा",
    "💎 Quality Over Quantity",
    "🦁 Stay Strong",
    "🔥 Self Made",
    "😎 Just Be Real",
]

BIO_STYLISH = [
    "꧁༺ 𝑹𝒐𝒚𝒂𝒍 𝑩𝒐𝒚 ༻꧂",
    "★彡[𝑺𝒊𝒎𝒑𝒍𝒆 𝑳𝒊𝒇𝒆]彡★",
    "『𝑺𝒕𝒚𝒍𝒊𝒔𝒉 𝑺𝒐𝒖𝒍』",
    "♛ 𝑲𝒊𝒏𝒈 𝑽𝒊𝒃𝒆𝒔 ♛",
    "𓆩♡𓆪 𝑪𝒖𝒕𝒆 𝑯𝒆𝒂𝒓𝒕",
    "𝑩𝒐𝒓𝒏 𝑻𝒐 𝑺𝒉𝒊𝒏𝒆 ✨",
    "꧁ঔৣ☬ 𝑳𝒆𝒈𝒆𝒏𝒅 ☬ঔৣ꧂",
    "『𝑵𝒐 𝑳𝒊𝒎𝒊𝒕𝒔』",
    "𝑺𝒕𝒂𝒚 𝑼𝒏𝒊𝒒𝒖𝒆 💎",
    "♡ 𝑯𝒂𝒑𝒑𝒚 𝑺𝒐𝒖𝒍 ♡",
    "꧁༒☬𝑩𝒐𝒔𝒔☬༒꧂",
    "𝓛𝓲𝓿𝓮 𝓕𝓻𝓮𝓮 🦋",
    "𝑴𝒚 𝑾𝒐𝒓𝒍𝒅 🌍",
    "★ 𝑩𝒆 𝑷𝒐𝒔𝒊𝒕𝒊𝒗𝒆 ★",
    "𝕯𝖗𝖊𝖆𝖒 𝕮𝖍𝖆𝖘𝖊𝖗",
    "『𝑺𝒐𝒍𝒐 𝑷𝒍𝒂𝒚𝒆𝒓』",
    "𓆩👑𓆪 𝑹𝒐𝒚𝒂𝒍 𝑴𝒊𝒏𝒅",
    "𝑵𝒆𝒗𝒆𝒓 𝑺𝒆𝒕𝒕𝒍𝒆 🔥",
    "꧁ 𝑺𝒘𝒂𝒈 𝑩𝒐𝒚 ꧂",
    "𝑺𝒎𝒊𝒍𝒆 𝑴𝒐𝒓𝒆 😊",
    "『𝑳𝒐𝒗𝒆 𝑴𝒚𝒔𝒆𝒍𝒇』",
    "𝓓𝓻𝓮𝓪𝓶 𝓑𝓲𝓰",
    "⚡ 𝑬𝒍𝒆𝒄𝒕𝒓𝒊𝒄 𝑽𝒊𝒃𝒆",
    "♛ 𝑺𝒕𝒂𝒚 𝑹𝒐𝒚𝒂𝒍",
    "𝑭𝒓𝒆𝒆 𝑺𝒑𝒊𝒓𝒊𝒕 🕊️",
    "꧁ 𝑪𝒍𝒂𝒔𝒔𝒚 𝑳𝒊𝒇𝒆 ꧂",
    "𝑩𝒆 𝑩𝒐𝒍𝒅 💥",
    "𝑺𝒕𝒂𝒚 𝑪𝒂𝒍𝒎 🖤",
    "★ 𝑮𝒐𝒐𝒅 𝑽𝒊𝒃𝒆𝒔 ★",
    "『𝑩𝒆𝒔𝒕 𝑽𝒆𝒓𝒔𝒊𝒐𝒏』",
    "𝑺𝒊𝒎𝒑𝒍𝒆 𝑩𝒖𝒕 𝑹𝒂𝒓𝒆",
    "𓆩⚡𓆪 𝑺𝒑𝒆𝒆𝒅 𝑴𝒐𝒅𝒆",
    "𝑳𝒊𝒗𝒆 𝑳𝒐𝒖𝒅",
    "꧁ 𝑷𝒖𝒓𝒆 𝑺𝒐𝒖𝒍 ꧂",
    "『𝑺𝒕𝒂𝒓 𝑩𝒐𝒚』",
    "𝑺𝒖𝒏𝒔𝒉𝒊𝒏𝒆 ☀️",
    "♡ 𝑪𝒖𝒕𝒆 𝑽𝒊𝒃𝒆𝒔",
    "𝑨𝒍𝒘𝒂𝒚𝒔 𝑺𝒎𝒊𝒍𝒊𝒏𝒈",
    "★ 𝑴𝒂𝒌𝒆 𝑰𝒕 𝑯𝒂𝒑𝒑𝒆𝒏",
    "꧁ 𝑼𝒏𝒊𝒒𝒖𝒆 𝑴𝒊𝒏𝒅 ꧂",
    "𝑺𝒕𝒚𝒍𝒆 𝑰𝒔 𝑬𝒗𝒆𝒓𝒚𝒕𝒉𝒊𝒏𝒈",
    "『𝑪𝒉𝒊𝒍𝒍 𝑴𝒐𝒅𝒆』",
    "𓆩💎𓆪 𝑹𝒂𝒓𝒆 𝑮𝒆𝒎",
    "𝑩𝒆 𝒀𝒐𝒖",
    "♛ 𝑷𝒓𝒊𝒏𝒄𝒆 𝑽𝒊𝒃𝒆𝒔",
    "꧁ 𝑺𝒕𝒂𝒚 𝑯𝒖𝒎𝒃𝒍𝒆 ꧂",
    "𝑴𝒐𝒐𝒏 𝑳𝒐𝒗𝒆𝒓 🌙",
    "★ 𝑨𝒓𝒕 𝑶𝒇 𝑳𝒊𝒗𝒊𝒏𝒈",
    "𝑺𝒎𝒂𝒓𝒕 𝑴𝒊𝒏𝒅",
    "𓆩👑𓆪 𝑴𝒚 𝑰𝒅𝒆𝒏𝒕𝒊𝒕𝒚",
]

BIO_LOVE = [
    "❤️ You Are My Happiness",
    "🥰 Made Of Love",
    "💕 Love Is Beautiful",
    "🌹 Forever Yours",
    "🦋 You Make Me Smile",
    "💗 दिल में सिर्फ तुम",
    "❤️ मोहब्बत मेरी पहचान",
    "🌙 तुम ही सुकून हो",
    "💞 प्यार सबसे खूबसूरत एहसास",
    "🥀 दिल से जुड़े हैं",
    "💘 One Heart One Dream",
    "🫶 Love Beyond Words",
    "🌸 Cute But Romantic",
    "💖 My Heart Is Pure",
    "❤️ प्यार में सादगी",
    "🥰 Smile Is My Love Language",
    "💕 Together Forever",
    "🌹 A Heart Full Of Dreams",
    "💗 तुमसे ही मुस्कान है",
    "🦋 Love Makes Life Beautiful",
    "💞 दिल की दुनिया तुम",
    "❤️ True Love Never Fades",
    "🌷 Sweet Soul",
    "💘 मेरा दिल, मेरी दुनिया",
    "🫶 प्यार में कोई शर्त नहीं",
    "💖 Happiness Is Love",
    "🌙 Moonlight And Love",
    "💕 A Little Romantic",
    "❤️ Just One Special Person",
    "🌹 मोहब्बत लाजवाब है",
    "🥰 Dreaming Of Love",
    "💗 Love Is My Vibe",
    "💞 दिल से दिल तक",
    "🦋 Pure Feelings",
    "❤️ Love Is Not A Game",
    "🌸 दिल में एक खास जगह",
    "💘 Forever In My Heart",
    "🫶 प्यार और भरोसा",
    "💖 Sweet Memories",
    "🌹 मेरा सुकून, मेरी खुशी",
    "💕 Romantic Soul",
    "🌙 तुम हो तो सब है",
    "❤️ Feelings Never Lie",
    "🥰 Love With Respect",
    "💗 दिल की आवाज़",
    "💞 One Soul Many Dreams",
    "🌷 प्यार ही प्यार",
    "💘 My Favorite Feeling",
    "🦋 Love And Peace",
    "❤️ दिल से सिर्फ तुम्हारे लिए",
]

BIO_SAD = [
    "🥀 Silent Feelings",
    "🖤 Lost In Thoughts",
    "🌙 अकेले रहना पसंद है",
    "💔 Broken Expectations",
    "🥀 कुछ बातें अधूरी हैं",
    "🖤 Smiling Outside",
    "🌧️ Rain And Memories",
    "💭 खोया हुआ सा हूँ",
    "🥀 Silence Speaks",
    "🌙 रातें और खामोशी",
    "🖤 No More Expectations",
    "💔 अधूरी कहानी",
    "🌧️ Tears Of Memories",
    "🥀 अकेलापन भी एक एहसास है",
    "💭 Lost In My World",
    "🖤 Feelings Are Private",
    "🌙 खामोश लफ्ज़",
    "🥀 Memories Never Fade",
    "💔 Trust Is Precious",
    "🌧️ बारिश और यादें",
    "🖤 Behind Every Smile",
    "💭 दिल की अनकही बातें",
    "🌙 Silent Nights",
    "🥀 Some Stories Stay Unfinished",
    "🖤 कम बोलता हूँ",
    "🌧️ A Cloudy Mind",
    "💔 उम्मीदें कम रखो",
    "🥀 खामोशी मेरी आदत",
    "💭 Thoughts Everywhere",
    "🌙 अकेली रातें",
    "🖤 Private Emotions",
    "🥀 वक्त सब सिखा देता है",
    "🌧️ Missing Old Days",
    "💭 Memories In My Mind",
    "🖤 शांत दिल, गहरी सोच",
    "🌙 Lost In Memories",
    "🥀 हर मुस्कान के पीछे कहानी",
    "💔 Feelings Unspoken",
    "🌧️ बादलों जैसा मन",
    "🖤 No Words Needed",
    "💭 अधूरे ख्वाब",
    "🌙 Deep Thoughts",
    "🥀 कुछ यादें खास होती हैं",
    "🖤 Silent Personality",
    "🌧️ Peace In Silence",
    "💭 बीते कल की यादें",
    "🥀 Not Every Story Is Perfect",
    "🌙 खुद के साथ खुश",
    "🖤 Mood: Offline",
    "✨ Better Days Ahead",
]

BIOS = {
    "att": ("👑 Attitude Bio", BIO_ATTITUDE),
    "sty": ("✨ Stylish Bio", BIO_STYLISH),
    "lov": ("❤️ Love Bio", BIO_LOVE),
    "sad": ("🥀 Sad Bio", BIO_SAD),
}

LOADING_FRAMES = [
    "🌸 Creating your styles...\n▰▱▱▱▱ 20%",
    "🌸 Creating your styles...\n▰▰▱▱▱ 40%",
    "🌸 Creating your styles...\n▰▰▰▱▱ 60%",
    "🌸 Creating your styles...\n▰▰▰▰▱ 80%",
    "🌸 Creating your styles...\n▰▰▰▰▰ 100%",
]

OWNER_USERNAME = "@ankit_x_x_1"


def welcome_text(first_name=""):
    greeting = f"👋 Hello {first_name}!\n\n" if first_name else ""

    return (
        "✨ Welcome To Name Stylish Bot ✨\n\n"
        f"{greeting}"
        "🌟 Features:\n"
        "✨ Make your name stylish\n"
        "💎 Tons of unique designs\n"
        "🦋 Cool fonts & symbols\n"
        "📝 Ready-made bios (Attitude, Stylish, Love, Sad)\n"
        "⚡ Easy copy & paste\n"
        "🌙 Simple, fun & easy to use\n\n"
        "👇 Choose what you want to create:\n\n"
        f"💫 Powered by {OWNER_USERNAME}"
    )


# =====================================================
# DATABASE
# =====================================================

@contextmanager
def db():
    conn = sqlite3.connect(DB_NAME, timeout=15)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                joined_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        columns = [row[1] for row in conn.execute("PRAGMA table_info(users)")]
        if "user_name" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN user_name TEXT")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                design TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, design)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                design TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_user(uid):
    with db() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users(user_id) VALUES (?)",
            (uid,),
        )


def set_user_name(uid, name):
    save_user(uid)
    with db() as conn:
        conn.execute(
            "UPDATE users SET user_name = ? WHERE user_id = ?",
            (name, uid),
        )


def get_user_name_db(uid):
    with db() as conn:
        row = conn.execute(
            "SELECT user_name FROM users WHERE user_id = ?",
            (uid,),
        ).fetchone()
    return row[0] if row and row[0] else ""


def get_users():
    with db() as conn:
        return [
            row[0]
            for row in conn.execute("SELECT user_id FROM users").fetchall()
        ]


def remove_user(uid):
    with db() as conn:
        conn.execute("DELETE FROM users WHERE user_id = ?", (uid,))


def save_favorite(uid, design):
    with db() as conn:
        cursor = conn.execute(
            "INSERT OR IGNORE INTO favorites(user_id, design) VALUES (?, ?)",
            (uid, design),
        )
        return cursor.rowcount > 0


def get_favorites(uid):
    with db() as conn:
        return conn.execute(
            "SELECT id, design FROM favorites "
            "WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (uid, FAVORITES_LIMIT),
        ).fetchall()


def delete_favorite(uid, fav_id):
    with db() as conn:
        conn.execute(
            "DELETE FROM favorites WHERE user_id = ? AND id = ?",
            (uid, fav_id),
        )


def save_history(uid, name, category):
    with db() as conn:
        conn.execute(
            "INSERT INTO history(user_id, name, category, design) "
            "VALUES (?, ?, ?, '')",
            (uid, name, category),
        )


def get_history(uid):
    with db() as conn:
        return conn.execute(
            "SELECT id, name, category, created_at FROM history "
            "WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (uid, HISTORY_LIMIT),
        ).fetchall()


def get_history_item(uid, item_id):
    with db() as conn:
        return conn.execute(
            "SELECT name, category FROM history WHERE user_id = ? AND id = ?",
            (uid, item_id),
        ).fetchone()


def get_stats():
    with db() as conn:
        return tuple(
            conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in ("users", "favorites", "history")
        )


def to_ist(created_at):
    try:
        utc = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        return (utc + timedelta(hours=5, minutes=30)).strftime("%d %b, %I:%M %p")
    except Exception:
        return created_at


# =====================================================
# BUTTON AND MESSAGE HELPERS
# =====================================================

def btn(text, callback_data=None, url=None, copy_text=None, style=None):
    kwargs = {}
    if style and COLORS["on"]:
        kwargs["api_kwargs"] = {"style": style}

    return InlineKeyboardButton(
        text,
        callback_data=callback_data,
        url=url,
        copy_text=copy_text,
        **kwargs,
    )


async def safe_edit(message, build):
    """build() -> (text, markup). Retries without colors if rejected."""
    for attempt in range(2):
        text, markup = build()
        try:
            await message.edit_text(text, reply_markup=markup)
            return
        except BadRequest as exc:
            if "not modified" in str(exc).lower():
                return
            if attempt == 0 and COLORS["on"]:
                logger.warning("Button colors rejected, turning them off: %s", exc)
                COLORS["on"] = False
                continue
            raise


async def safe_reply(message, build):
    for attempt in range(2):
        text, markup = build()
        try:
            return await message.reply_text(text, reply_markup=markup)
        except BadRequest as exc:
            if attempt == 0 and COLORS["on"]:
                logger.warning("Button colors rejected, turning them off: %s", exc)
                COLORS["on"] = False
                continue
            raise


# =====================================================
# CHANNEL MEMBERSHIP
# =====================================================

async def is_joined(uid, context):
    cache = context.bot_data.setdefault("join_cache", {})
    if cache.get(uid, 0) > time.time():
        return True

    try:
        # Both channels are mandatory. Verify each one before allowing access.
        for channel_id, _channel_url in CHANNELS:
            member = await context.bot.get_chat_member(channel_id, uid)
            joined = (
                member.status in ("member", "administrator", "creator")
                or (
                    member.status == "restricted"
                    and getattr(member, "is_member", False)
                )
            )
            if not joined:
                return False

        cache[uid] = time.time() + JOIN_CACHE_SECONDS
        return True

    except Exception:
        logger.exception("Membership check failed")
        return False


def join_keyboard():
    return InlineKeyboardMarkup([
        [btn("📢 Join Channel 1", url=CHANNELS[0][1])],
        [btn("📢 Join Channel 2", url=CHANNELS[1][1])],
        [btn("✅ I've Joined Both", callback_data="check_join", style="success")],
    ])


async def ask_to_join(message):
    await message.reply_text(
        "🔒 Please join both channels first, then tap "
        "\"I've Joined Both\" to continue.",
        reply_markup=join_keyboard(),
    )


async def require_membership(update, context):
    user = update.effective_user

    if user and await is_joined(user.id, context):
        return True

    if update.effective_message:
        await ask_to_join(update.effective_message)

    return False


# =====================================================
# MENUS
# =====================================================

def main_menu_markup():
    return InlineKeyboardMarkup([
        [btn("✨ Name Styles", callback_data="namemenu", style="primary")],
        [btn("📝 Bio Collection", callback_data="bio", style="success")],
        [
            btn("⭐ Favorites", callback_data="show:favorites"),
            btn("🕘 History", callback_data="show:history"),
        ],
    ])


def build_main_menu(name=""):
    return (
        "🏠 Main Menu\n\nWhat would you like to create?",
        main_menu_markup(),
    )


def build_name_menu(name):
    return (
        "✨ Name Styles\n\n"
        f"📝 Current name: {name}\n\n"
        "Choose a design category:",
        InlineKeyboardMarkup([
            [btn("👑 Premium Design", callback_data="cat:premium")],
            [btn("🌷 Aesthetic Design", callback_data="cat:aesthetic")],
            [btn("✨ Fancy Design", callback_data="cat:fancy")],
            [
                btn("✏️ Change Name", callback_data="newname"),
                btn("🏠 Main Menu", callback_data="menu", style="danger"),
            ],
        ]),
    )


def build_bio_menu():
    return (
        "📝 Bio Collection\n\nChoose a bio type (50 bios each):",
        InlineKeyboardMarkup([
            [btn(BIOS["att"][0], callback_data="bc:att:0")],
            [btn(BIOS["sty"][0], callback_data="bc:sty:0")],
            [btn(BIOS["lov"][0], callback_data="bc:lov:0")],
            [btn(BIOS["sad"][0], callback_data="bc:sad:0")],
            [btn("🏠 Main Menu", callback_data="menu", style="danger")],
        ]),
    )


def admin_menu():
    return InlineKeyboardMarkup([
        [btn("📊 Statistics", callback_data="admin:stats")],
        [btn("📢 Broadcast", callback_data="admin:broadcast")],
        [btn("❌ Close", callback_data="admin:close")],
    ])


# =====================================================
# NAME CONVERSION
# =====================================================

def decorate(name):
    return "".join(ch if ch.isspace() else ch + "꯭" for ch in name)


def make_design(template, name):
    result = template.replace("{name_dec}", decorate(name)).replace("{name}", name)

    # CopyTextButton allows at most 256 characters.
    if len(result) > 256:
        result = template.replace("{name_dec}", name).replace("{name}", name)

    return result[:256]


# =====================================================
# PAGE BUILDERS
# =====================================================

def nav_row(prefix, page, total, extra=""):
    row = []

    if page > 0:
        row.append(btn("⬅️ Prev", callback_data=f"{prefix}:{page - 1}{extra}", style="primary"))

    row.append(btn(f"📄 {page + 1}/{total}", callback_data="noop"))

    if page < total - 1:
        row.append(btn("Next ➡️", callback_data=f"{prefix}:{page + 1}{extra}", style="primary"))

    return row


def build_design_page(category, name, page, mode):
    designs = [make_design(t, name) for t in DESIGNS[category]]
    total = max(1, math.ceil(len(designs) / PAGE_SIZE))
    page = max(0, min(page, total - 1))

    start = page * PAGE_SIZE
    chunk = designs[start:start + PAGE_SIZE]

    rows = []
    for index, design in enumerate(chunk, start=start):
        label = f"{index + 1}. {design}".replace("\n", " ")

        if mode == "s":
            button = btn(label, callback_data=f"sv:{category}:{index}")
        else:
            button = btn(label, copy_text=CopyTextButton(text=design))

        rows.append([button])

    rows.append(nav_row(f"pg:{category}", page, total, extra=f":{mode}"))

    if mode == "s":
        rows.append([btn("📋 Switch To Copy Mode", callback_data=f"pg:{category}:{page}:c", style="success")])
        hint = "⭐ Save mode: tap a style to add it to Favorites"
    else:
        rows.append([btn("⭐ Switch To Save Mode", callback_data=f"pg:{category}:{page}:s", style="success")])
        hint = "👇 Tap any style to copy it"

    rows.append([
        btn("✏️ New Name", callback_data="newname"),
        btn("🏠 Main Menu", callback_data="menu", style="danger"),
    ])

    text = (
        f"{CATEGORY_NAMES[category]}\n\n"
        f"📝 Name: {name}\n"
        f"📄 Page: {page + 1}/{total}\n"
        f"🎨 Total styles: {len(designs)}\n\n"
        f"{hint}"
    )

    return text, InlineKeyboardMarkup(rows)


def build_bio_page(key, page):
    title, items = BIOS[key]
    total = max(1, math.ceil(len(items) / PAGE_SIZE))
    page = max(0, min(page, total - 1))

    start = page * PAGE_SIZE
    chunk = items[start:start + PAGE_SIZE]

    rows = []
    for index, bio in enumerate(chunk, start=start):
        rows.append([
            btn(f"{index + 1}. {bio}", copy_text=CopyTextButton(text=bio))
        ])

    rows.append(nav_row(f"bc:{key}", page, total))
    rows.append([
        btn("📝 Bio Types", callback_data="bio"),
        btn("🏠 Main Menu", callback_data="menu", style="danger"),
    ])

    text = (
        f"{title}\n\n"
        f"📄 Page: {page + 1}/{total}\n"
        f"💬 Total bios: {len(items)}\n\n"
        "👇 Tap any bio to copy it"
    )

    return text, InlineKeyboardMarkup(rows)


# =====================================================
# NAME HELPERS
# =====================================================

def get_name(uid, context):
    name = context.user_data.get("user_name")

    if not name:
        name = get_user_name_db(uid)
        if name:
            context.user_data["user_name"] = name

    return name or ""


async def ask_for_name(message, context):
    context.user_data["waiting_for_name"] = True
    await message.reply_text("✏️ Please send the name you want to style.")


async def open_category(message, uid, category, name):
    """Plays the loading animation, then shows page 1 of the category."""
    for frame in LOADING_FRAMES:
        try:
            await message.edit_text(frame)
        except BadRequest:
            pass
        await asyncio.sleep(0.3)

    save_history(uid, name, category)

    await safe_edit(message, lambda: build_design_page(category, name, 0, "c"))


# =====================================================
# START AND NAME INPUT
# =====================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_membership(update, context):
        return

    save_user(update.effective_user.id)
    context.user_data["waiting_for_name"] = False

    await update.effective_message.reply_text(
        welcome_text(update.effective_user.first_name or ""),
        reply_markup=main_menu_markup(),
    )


async def receive_name(update, context):
    user = update.effective_user
    message = update.effective_message

    if not user or not message or not message.text:
        return

    if context.user_data.get("waiting_for_broadcast"):
        return

    if not await require_membership(update, context):
        return

    # Text is only treated as a name after the user chose "Name Styles".
    if not context.user_data.get("waiting_for_name"):
        await safe_reply(message, build_main_menu)
        return

    name = message.text.strip()

    if not name:
        await message.reply_text("Please send a valid name.")
        return

    if len(name) > 50:
        await message.reply_text(
            "Please send a name with 50 characters or fewer."
        )
        return

    context.user_data["user_name"] = name
    context.user_data["waiting_for_name"] = False
    set_user_name(user.id, name)

    await safe_reply(message, lambda: build_name_menu(name))


async def menu_command(update, context):
    if not await require_membership(update, context):
        return

    name = get_name(update.effective_user.id, context)
    await safe_reply(update.effective_message, lambda: build_main_menu(name))


async def bio_command(update, context):
    if not await require_membership(update, context):
        return

    await safe_reply(update.effective_message, build_bio_menu)


async def help_command(update, context):
    if not await require_membership(update, context):
        return

    lines = [
        "/start - Start the bot",
        "/menu - Open the main menu",
        "/bio - Open the bio collection",
        "/favorites - View saved designs",
        "/history - View recent activity",
    ]

    if is_admin(update.effective_user.id):
        lines.append("/admin - Open the admin panel")

    await update.effective_message.reply_text("\n".join(lines))


# =====================================================
# MENU AND CATEGORY CALLBACKS
# =====================================================

async def noop_callback(update, context):
    await update.callback_query.answer()


async def menu_callback(update, context):
    query = update.callback_query
    await query.answer()

    if not await is_joined(query.from_user.id, context):
        await ask_to_join(query.message)
        return

    name = get_name(query.from_user.id, context)
    await safe_edit(query.message, lambda: build_main_menu(name))


async def new_name_callback(update, context):
    query = update.callback_query
    await query.answer()

    if not await is_joined(query.from_user.id, context):
        await ask_to_join(query.message)
        return

    await ask_for_name(query.message, context)


async def name_menu_callback(update, context):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id

    if not await is_joined(uid, context):
        await ask_to_join(query.message)
        return

    name = get_name(uid, context)

    if not name:
        await ask_for_name(query.message, context)
        return

    await safe_edit(query.message, lambda: build_name_menu(name))


async def category_callback(update, context):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id

    if not await is_joined(uid, context):
        await ask_to_join(query.message)
        return

    category = query.data.split(":", 1)[1]

    if category not in DESIGNS:
        await query.message.reply_text("Invalid category.")
        return

    name = get_name(uid, context)

    if not name:
        await ask_for_name(query.message, context)
        return

    save_user(uid)
    await open_category(query.message, uid, category, name)


async def page_callback(update, context):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id

    if not await is_joined(uid, context):
        await ask_to_join(query.message)
        return

    try:
        _, category, page, mode = query.data.split(":")
        page = int(page)
    except ValueError:
        return

    if category not in DESIGNS or mode not in ("c", "s"):
        return

    name = get_name(uid, context)

    if not name:
        await ask_for_name(query.message, context)
        return

    await safe_edit(
        query.message,
        lambda: build_design_page(category, name, page, mode),
    )


async def save_style_callback(update, context):
    query = update.callback_query
    uid = query.from_user.id

    if not await is_joined(uid, context):
        await query.answer()
        await ask_to_join(query.message)
        return

    try:
        _, category, index = query.data.split(":")
        template = DESIGNS[category][int(index)]
    except (ValueError, KeyError, IndexError):
        await query.answer("Invalid style.", show_alert=True)
        return

    name = get_name(uid, context)

    if not name:
        await query.answer("Please send your name first.", show_alert=True)
        return

    added = save_favorite(uid, make_design(template, name))
    await query.answer("⭐ Saved!" if added else "Already saved.")


# =====================================================
# BIO CALLBACKS
# =====================================================

async def bio_menu_callback(update, context):
    query = update.callback_query
    await query.answer()

    if not await is_joined(query.from_user.id, context):
        await ask_to_join(query.message)
        return

    await safe_edit(query.message, build_bio_menu)


async def bio_page_callback(update, context):
    query = update.callback_query
    await query.answer()

    if not await is_joined(query.from_user.id, context):
        await ask_to_join(query.message)
        return

    try:
        _, key, page = query.data.split(":")
        page = int(page)
    except ValueError:
        return

    if key not in BIOS:
        return

    await safe_edit(query.message, lambda: build_bio_page(key, page))


# =====================================================
# FAVORITES
# =====================================================

async def show_favorites_message(message, uid):
    favorites = get_favorites(uid)

    if not favorites:
        await message.reply_text(
            "⭐ No saved favorites yet.\n\n"
            "Open any design page and switch to Save Mode."
        )
        return

    for fav_id, design in favorites:
        keyboard = InlineKeyboardMarkup([[
            btn("📋 Copy", copy_text=CopyTextButton(text=design)),
            btn("🗑 Remove", callback_data=f"favlist:remove:{fav_id}", style="danger"),
        ]])

        await message.reply_text(design, reply_markup=keyboard)
        await asyncio.sleep(0.05)


async def favorite_list_callback(update, context):
    query = update.callback_query

    if not await is_joined(query.from_user.id, context):
        await query.answer()
        await ask_to_join(query.message)
        return

    try:
        fav_id = int(query.data.split(":")[2])
    except (ValueError, IndexError):
        await query.answer("Please reopen your favorites list.", show_alert=True)
        return

    delete_favorite(query.from_user.id, fav_id)
    await query.answer("Removed.")

    try:
        await query.message.edit_text("🗑 Favorite removed.")
    except BadRequest:
        pass


async def favorites_command(update, context):
    if not await require_membership(update, context):
        return

    await show_favorites_message(
        update.effective_message,
        update.effective_user.id,
    )


# =====================================================
# HISTORY
# =====================================================

async def send_history(message, uid):
    rows = get_history(uid)

    if not rows:
        await message.reply_text("🕘 Your history is empty.")
        return

    keyboard = [
        [
            btn(
                f"{name} • {CATEGORY_NAMES.get(category, category)} • {to_ist(created_at)}",
                callback_data=f"hist:{item_id}",
            )
        ]
        for item_id, name, category, created_at in rows
    ]

    await message.reply_text(
        "🕘 Recent activity (tap to open again):",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def history_command(update, context):
    if not await require_membership(update, context):
        return

    await send_history(
        update.effective_message,
        update.effective_user.id,
    )


async def history_item_callback(update, context):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id

    if not await is_joined(uid, context):
        await ask_to_join(query.message)
        return

    try:
        item_id = int(query.data.split(":")[1])
    except (ValueError, IndexError):
        return

    item = get_history_item(uid, item_id)

    if not item or item[1] not in DESIGNS:
        await query.message.reply_text("This history item is no longer available.")
        return

    name, category = item
    context.user_data["user_name"] = name
    set_user_name(uid, name)

    sent = await query.message.reply_text(LOADING_FRAMES[0])
    await open_category(sent, uid, category, name)


async def show_callback(update, context):
    query = update.callback_query
    await query.answer()

    if not await is_joined(query.from_user.id, context):
        await ask_to_join(query.message)
        return

    kind = query.data.split(":", 1)[1]

    if kind == "favorites":
        await show_favorites_message(query.message, query.from_user.id)
    elif kind == "history":
        await send_history(query.message, query.from_user.id)


# =====================================================
# ADMIN
# =====================================================

def is_admin(uid):
    return uid in ADMIN_IDS


async def admin_command(update, context):
    if not is_admin(update.effective_user.id):
        await update.effective_message.reply_text("⛔ Admin only.")
        return

    await update.effective_message.reply_text(
        "🛠 Admin Panel",
        reply_markup=admin_menu(),
    )


async def admin_callback(update, context):
    query = update.callback_query

    if not is_admin(query.from_user.id):
        await query.answer("Admin only.", show_alert=True)
        return

    await query.answer()
    action = query.data.split(":", 1)[1]

    if action == "stats":
        users, favorites, history = get_stats()
        await query.message.reply_text(
            "📊 Statistics\n\n"
            f"Users: {users}\n"
            f"Favorites: {favorites}\n"
            f"History: {history}"
        )

    elif action == "broadcast":
        context.user_data["waiting_for_broadcast"] = True
        await query.message.reply_text(
            "Send the broadcast message. Cancel: /cancelbroadcast"
        )

    elif action == "close":
        await query.edit_message_text("Admin panel closed.")


# =====================================================
# BROADCAST
# =====================================================

async def broadcast_command(update, context):
    if not is_admin(update.effective_user.id):
        await update.effective_message.reply_text("⛔ Admin only.")
        return

    context.user_data["waiting_for_broadcast"] = True
    await update.effective_message.reply_text(
        "Send the broadcast message. Cancel: /cancelbroadcast"
    )


async def cancel_broadcast(update, context):
    if not is_admin(update.effective_user.id):
        return

    context.user_data["waiting_for_broadcast"] = False
    await update.effective_message.reply_text("❌ Broadcast cancelled.")


async def broadcast_message(update, context):
    user = update.effective_user
    message = update.effective_message

    if not user or not is_admin(user.id):
        return

    if not context.user_data.get("waiting_for_broadcast"):
        return

    if not message or (
        message.text and message.text.startswith("/")
    ):
        return

    context.user_data["waiting_for_broadcast"] = False
    users = get_users()

    success = 0
    failed = 0
    removed = 0

    status = await message.reply_text(
        f"⏳ Broadcast started: {len(users)} users"
    )

    for uid in users:
        try:
            await message.copy(chat_id=uid)
            success += 1
            await asyncio.sleep(0.05)

        except RetryAfter as exc:
            delay = exc.retry_after
            if hasattr(delay, "total_seconds"):
                delay = delay.total_seconds()

            await asyncio.sleep(float(delay) + 1)

            try:
                await message.copy(chat_id=uid)
                success += 1
            except Forbidden:
                failed += 1
                removed += 1
                remove_user(uid)
            except Exception:
                failed += 1
                logger.exception("Broadcast retry failed")

        except Forbidden:
            failed += 1
            removed += 1
            remove_user(uid)

        except Exception:
            failed += 1
            logger.exception("Broadcast failed")

    await status.edit_text(
        "✅ Broadcast complete\n\n"
        f"Total: {len(users)}\n"
        f"Success: {success}\n"
        f"Failed: {failed}\n"
        f"Removed: {removed}"
    )

    raise ApplicationHandlerStop


# =====================================================
# CHANNEL JOIN VERIFICATION
# =====================================================

async def check_join_callback(update, context):
    query = update.callback_query
    await query.answer()

    if not await is_joined(query.from_user.id, context):
        await ask_to_join(query.message)
        return

    save_user(query.from_user.id)
    context.user_data["waiting_for_name"] = False

    await query.message.reply_text(
        "✅ Membership verified!\n\n"
        + welcome_text(query.from_user.first_name or ""),
        reply_markup=main_menu_markup(),
    )


# =====================================================
# RUN BOT
# =====================================================

def main():
    if not TOKEN:
        print("ERROR: Set BOT_TOKEN in the hosting environment.")
        return

    init_db()

    app = Application.builder().token(TOKEN).build()

    # Broadcast handlers run before regular text handlers.
    app.add_handler(CommandHandler("broadcast", broadcast_command), group=-1)
    app.add_handler(CommandHandler("cancelbroadcast", cancel_broadcast), group=-1)
    app.add_handler(
        MessageHandler(filters.ALL & ~filters.COMMAND, broadcast_message),
        group=-1,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("bio", bio_command))
    app.add_handler(CommandHandler("favorites", favorites_command))
    app.add_handler(CommandHandler("history", history_command))
    app.add_handler(CommandHandler("admin", admin_command))

    callbacks = [
        (check_join_callback, r"^check_join$"),
        (noop_callback, r"^noop$"),
        (menu_callback, r"^menu$"),
        (new_name_callback, r"^newname$"),
        (name_menu_callback, r"^namemenu$"),
        (category_callback, r"^cat:"),
        (page_callback, r"^pg:"),
        (save_style_callback, r"^sv:"),
        (bio_menu_callback, r"^bio$"),
        (bio_page_callback, r"^bc:"),
        (favorite_list_callback, r"^favlist:"),
        (history_item_callback, r"^hist:"),
        (show_callback, r"^show:"),
        (admin_callback, r"^admin:"),
    ]

    for handler, pattern in callbacks:
        app.add_handler(CallbackQueryHandler(handler, pattern=pattern))

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)
    )

    print("Stylish Name Maker Bot started!")
    app.run_polling()


if __name__ == "__main__":
    main()
