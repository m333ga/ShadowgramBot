from aiogram import Bot, Dispatcher, types
import asyncio
import json


# ~ load data ~
with open('api_key.json', 'r') as f:
    json_data_api_key = json.load(f)
    API_KEY = json_data_api_key.get('API_KEY')


# ~ set up bot ~
bot = Bot(API_KEY)
dp = Dispatcher(bot=bot)


# ~ commands ~
# start message
@dp.message_handler(commands=['start'])
async def start(message: types.Message) -> None:

    if message.from_user['language_code'] == 'ru':
        await message.answer(f'''💌 *Привет, ~{message.from_user['first_name']}~! Это бот для отправки анонимных сообщений друзьям и знакомым.*
📝 Отправить новое сообщение: /new юзернейм сообщение для отправки
📬 Показать последнее полученное сообщение: /last''', parse_mode='Markdown')

    else:
        await message.answer(f'''💌 *Hi, ~{message.from_user['first_name']}~! This is a bot for sending anonymous messages to your friends.*\n
📝 Send new message: /new @username your message
📬 Show last received message: /last''', parse_mode='Markdown')


# send new message
@dp.message_handler(commands=['new'])
async def new(message: types.Message) -> None:
    try:
        recipient_username = message.text.split()[1].replace('@', '')
        sender_message = message.text.split(' ', maxsplit=2)[2]

        message.text.replace('"', '\"')
        message.text.replace('\'', '\'')
        message.text.replace('\\', '\\')

        # write message to json file
        with open('messages.json', 'r', encoding='utf-8') as f_messages:
            messages = json.load(f_messages)

        # func to write data in json
        def write_to_json(message_text=sender_message, is_showed=False, from_user=message.from_user.username):
            # generate json data
            message_json_data = {
                "message_text": str(message_text),
                "is_showed": is_showed,
                "from_user": str(from_user)
            }
            # messages[recipient_username] = sender_message

            messages[recipient_username] = message_json_data

            with open('messages.json', 'w', encoding='utf-8') as f_messages:
                json.dump(messages, f_messages, ensure_ascii=False, indent=2)

        write_to_json()

        # 'message sent' notification
        if message.from_user['language_code'] == 'ru':
            await message.answer('💌 *Сообщение отправлено!*', parse_mode='Markdown')
        else:
            await message.answer('💌 *Message sent!*', parse_mode='Markdown')

        # read messages dict from json
        with open('messages.json', 'r', encoding='utf-8') as f_messages:
            messages = json.load(f_messages)

        # send message to recipient
        if message.from_user.username in messages and not messages[message.from_user.username]["is_showed"]:
            if message.from_user['language_code'] == 'ru':
                await message.answer(f'💌 *У тебя новое сообщение!:*\n\n{messages[message.from_user.username]["message_text"]}', parse_mode='Markdown')
            else:
                await message.answer(f'💌 *You have a new message!*\n\n{messages[message.from_user.username]["message_text"]}', parse_mode='Markdown')

            # mark message in json as readed
            write_to_json(is_showed=True)

        print(
            f'from {message.from_user.username} to {recipient_username} message "{sender_message}"\n~')

    except IndexError:
        if message.from_user['language_code'] == 'ru':
            await message.answer('''❗️ *Пожалуйста, укажите юзернейм и сообщение.*
\nПример: /new @юзернейм привет''', parse_mode='Markdown')
        else:
            await message.answer('''❗️ *Please enter username and message.*
\nExample: /new @username hello''', parse_mode='Markdown')


# last message
@dp.message_handler(commands=['last'])
async def last(message: types.Message) -> None:
    with open('messages.json', 'r', encoding='utf-8') as f_messages:
        messages = json.load(f_messages)

    if message.from_user['language_code'] == 'ru':
        await message.answer(f'💬 *Последнее полученное сообщение:*\n\n{messages[message.from_user.username]["message_text"]}', parse_mode='Markdown')
    else:
        await message.answer(f'💬 *Last received message:*\n\n{messages[message.from_user.username]["message_text"]}', parse_mode='Markdown')


# ~ run all async functions ~
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
