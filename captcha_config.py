from aiogram.types import ChatPermissions


# Настройки капчи
#  ╱| 、
# (˚ˎ 。7
#  | 、˜〵
#  じしˍ, )ノ


# С исключением похожих символов (0 и О, 7 и 1)
captcha_symbols = ['2', '3', '4', '5', '6', '8', '9', 'A',
                   'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
                   'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R',
                   'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
captcha_len = 3
image_captcha_width = 130
image_captcha_height = 100

muted_permissions = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_polls=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False,
    can_invite_users=False,
    can_pin_messages=False)
