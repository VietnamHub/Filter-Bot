import html
from typing import Optional, List

from telegram import Message, Update, Bot, User
from telegram import ParseMode, MAX_MESSAGE_LENGTH
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import escape_markdown

import bot.modules.sql.userinfo_sql as sql
from bot import dispatcher, OWNER_ID, LOGGER, DEV_USERS
from bot.modules.helper_funcs.extraction import extract_user


@run_async
def about_me(bot: Bot, update: Update, args: List[str]):
    message = update.effective_message  # type: Optional[Message]
    user_id = extract_user(message, args)

    if user_id:
        user = bot.get_chat(user_id)
    else:
        user = message.from_user

    info = sql.get_user_me_info(user.id)

    if info:
        update.effective_message.reply_text("*{}*:\n{}".format(user.first_name, escape_markdown(info)),
                                            parse_mode=ParseMode.MARKDOWN)
    elif message.reply_to_message:
        username = message.reply_to_message.from_user.first_name
        update.effective_message.reply_text(username + "Thông tin về anh ấy hiện không có !")
    else:
        update.effective_message.reply_text("Bạn chưa thêm bất kỳ thông tin nào về bản thân!")


@run_async
def set_about_me(bot: Bot, update: Update):
    message = update.effective_message  # type: Optional[Message]
    user_id = message.from_user.id
    text = message.text
    info = text.split(None, 1)  # use python's maxsplit to only remove the cmd, hence keeping newlines.
    if len(info) == 2:
        if len(info[1]) < MAX_MESSAGE_LENGTH // 4:
            sql.set_user_me_info(user_id, info[1])
            message.reply_text("Your information has been recorded successfully")
        else:
            message.reply_text(
                " About You{} To be confined to letters ".format(MAX_MESSAGE_LENGTH // 4, len(info[1])))


@run_async
def about_bio(bot: Bot, update: Update, args: List[str]):
    message = update.effective_message  # type: Optional[Message]

    user_id = extract_user(message, args)
    if user_id:
        user = bot.get_chat(user_id)
    else:
        user = message.from_user

    info = sql.get_user_bio(user.id)

    if info:
        update.effective_message.reply_text("*{}*:\n{}".format(user.first_name, escape_markdown(info)),
                                            parse_mode=ParseMode.MARKDOWN)
    elif message.reply_to_message:
        username = user.first_name
        update.effective_message.reply_text("{} chưa được xác minh !".format(username))
    else:
        update.effective_message.reply_text(" Thông tin của bạn về bạn đã được thêm vào !")


@run_async
def set_about_bio(bot: Bot, update: Update):
    message = update.effective_message  # type: Optional[Message]
    sender = update.effective_user  # type: Optional[User]
    if message.reply_to_message:
        repl_message = message.reply_to_message
        user_id = repl_message.from_user.id
        if user_id == message.from_user.id:
            message.reply_text("Bạn đang muốn thay đổi chính mình ... ?? Đó là nó.")
            return
        elif user_id and sender.id not in OWNER_ID:
            message.reply_text(" Chỉ CHỦ GROUP mới có thể thay đổi thông tin của tôi ... ??.")
            return
        elif user_id == bot.id and sender.id not in OWNER_ID:
            message.reply_text(" Chỉ CHỦ GROUP mới có thể thay đổi thông tin của tôi ... ??")
            return

        text = message.text
        bio = text.split(None, 1)  # use python's maxsplit to only remove the cmd, hence keeping newlines.
        if len(bio) == 2:
            if len(bio[1]) < MAX_MESSAGE_LENGTH // 4:
                sql.set_user_bio(user_id, bio[1])
                message.reply_text("Thông tin về {} đã được thu thập thành công !".format(repl_message.from_user.first_name))
            else:
                message.reply_text(
                    "About you {} phải bám vào chữ cái! Số ký tự bạn vừa thử {} hm .".format(
                        MAX_MESSAGE_LENGTH // 4, len(bio[1])))
    else:
        message.reply_text(" Tôi không biết phải xác minh ai?")


def __user_info__(user_id):
    bio = html.escape(sql.get_user_bio(user_id) or "")
    me = html.escape(sql.get_user_me_info(user_id) or "")
    if bio and me:
        return "<b>Thông tin xác minh:</b>\n{bio}".format(me=me, bio=bio)
    elif bio:
        return "<b>Thông tin xác minh:</b>\n{bio}\n".format(me=me, bio=bio)
    elif me:
        return "<b>About user:</b>\n{me}""".format(me=me, bio=bio)
    else:
        return ""


__help__ = """
 - /xacminh <text>: xác minh người khác
 - /thongtin: xem thông tin được xác minh
"""

__mod_name__ = "Xác minh ⚠"

SET_BIO_HANDLER = DisableAbleCommandHandler("xacminh", set_about_bio)
GET_BIO_HANDLER = DisableAbleCommandHandler("thongtin", about_bio, pass_args=True)

SET_ABOUT_HANDLER = DisableAbleCommandHandler("xacminh1", set_about_me)
GET_ABOUT_HANDLER = DisableAbleCommandHandler("thongtin1", about_me, pass_args=True)

dispatcher.add_handler(SET_BIO_HANDLER)
dispatcher.add_handler(GET_BIO_HANDLER)
dispatcher.add_handler(SET_ABOUT_HANDLER)
dispatcher.add_handler(GET_ABOUT_HANDLER)
