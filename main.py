import os
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext, CallbackQueryHandler

async def set_reminder(update: Update, context: CallbackContext):
    context.user_data['task'] = {}
    context.user_data['task']['answered'] = False
    context.user_data['task']['message_id'] = None

    # ID чата
    chat_id = update.message.chat_id

    # Получаем данные о задании и сотруднике из Google Sheets или откуда-нибудь ещё
    employee_id = os.getenv('EMPLOYEE_ID')
    test_task = 'Тестовое задание'
    test_date = '2023-07-16'
    test_time = '12:00'
    answer_time = 3  # Время на ответ в секундах
    text = f'Просьба выполнить задачу:\nЗадание: {test_task}\nДата: {test_date}\nВремя: {test_time}\nВремя на ответ: {answer_time} сек.'

    keyboard = [
        [InlineKeyboardButton('Выполнено', callback_data='done')],
        [InlineKeyboardButton('Не сделано', callback_data='not_done')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = await context.bot.send_message(chat_id=employee_id, text=text, reply_markup=reply_markup)
    context.user_data['task']['message_id'] = message.message_id

    context.job_queue.run_once(check_response, answer_time, user_id=employee_id, data=context.user_data)


async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    context.user_data['task']['answered'] = True

    button_data = query.data

    manager_id = os.getenv('MANAGER_ID')
    await context.bot.send_message(chat_id=manager_id, text=f'Сотрудник нажал кнопку: {button_data}')


async def check_response(context: CallbackContext):
    employee_id = context.job.user_id

    if not context.job.data['task']['answered']:
        manager_id = os.getenv('MANAGER_ID')
        await context.bot.send_message(chat_id=manager_id, text=f'Сотрудник {employee_id} проигнорировал напоминание')


def main():
    load_dotenv()
    app = ApplicationBuilder().token(token=os.getenv('TG_TOKEN')).build()

    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CommandHandler('set_reminder', set_reminder))

    app.run_polling()


if __name__ == '__main__':
    main()