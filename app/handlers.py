from aiogram import Router,F,Bot
from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup,Message,CallbackQuery
from aiogram.filters import CommandStart,Command

import csv
from DatabaseBot.config import ADMIN_ID,TOKEN
import os
from DatabaseBot.database import SessionLocal, User, BroadCast
from datetime import datetime

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from aiogram.types import CallbackQuery, Message, PreCheckoutQuery, LabeledPrice, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


bot = Bot(token=TOKEN)

router = Router()
Currency = 'XTR'

headers = {
    "Referer": "https://www.google.com/"
               "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
}


class Find(StatesGroup):
    telephone = State()


class BroadcastState(StatesGroup):
    wait_text = State()
def main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔎 Поиск',callback_data='search'),InlineKeyboardButton(text='👤 Профиль',callback_data='profile')],
        [InlineKeyboardButton(text='💰 Пополнить',callback_data='premium')]
    ])
    return keyboard

payment = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Оплатить ⭐', pay=True)]
])


def search_by_phone(phone_number, filename="database-telephone"):

    search_digits = ''.join(c for c in str(phone_number) if c.isdigit())

    # Проверяем существование файла (с .csv и без)
    actual_filename = filename
    if not os.path.exists(actual_filename):
        if not actual_filename.endswith('.csv'):
            actual_filename = actual_filename + '.csv'
        if not os.path.exists(actual_filename):
            return "❌ Файл '{}' или '{}' не найден!".format(filename, actual_filename)

    found_records = []

    try:
        with open(actual_filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                row_phone = row.get('phone_number')

                if row_phone is not None and str(row_phone).strip():
                    row_phone_str = str(row_phone)
                    row_digits = ''.join(c for c in row_phone_str if c.isdigit())

                    if row_digits == search_digits:
                        found_records.append(row)

        if not found_records:
            return "🔍 По номеру {} ничего не найдено".format(phone_number)

        # Формируем строку с результатами
        result_lines = []
        result_lines.append("\n📱 Найдено записей: {}".format(len(found_records)))
        result_lines.append("=" * 50)

        for i, record in enumerate(found_records, 1):
            result_lines.append("\n✨ Запись #{}".format(i))
            result_lines.append("-" * 40)

            # Основная информация
            result_lines.append("🆔 ID: {}".format(record.get('id', '❓ Нет данных')))
            result_lines.append("👤 Имя: {}".format(record.get('first_name', '❓ Нет данных')))

            full_name = record.get('full_name')
            if full_name and str(full_name).strip():
                result_lines.append("🏷️ Полное имя: {}".format(full_name))

            email = record.get('email')
            if email and str(email).strip():
                result_lines.append("📧 Email: {}".format(email))

            result_lines.append("📞 Телефон: {}".format(record.get('phone_number', '❓ Нет данных')))

            # Адрес
            result_lines.append("\n🏢 Адрес:")
            result_lines.append("   🏙️  Город: {}".format(record.get('address_city', '❓ Нет данных')))
            result_lines.append("   🛣️  Улица: {}".format(record.get('address_street', '❓ Нет данных')))
            result_lines.append("   🏠 Дом: {}".format(record.get('address_house', '❓ Нет данных')))

            entrance = record.get('address_entrance')
            if entrance and str(entrance).strip():
                result_lines.append("   🚪 Подъезд: {}".format(entrance))

            floor = record.get('address_floor')
            if floor and str(floor).strip():
                result_lines.append("   🏢 Этаж: {}".format(floor))

            office = record.get('address_office')
            if office and str(office).strip():
                result_lines.append("   📌 Квартира/офис: {}".format(office))

            doorcode = record.get('address_doorcode')
            if doorcode and str(doorcode).strip():
                result_lines.append("   🔑 Код домофона: {}".format(doorcode))

            comment = record.get('address_comment')
            if comment and str(comment).strip():
                result_lines.append("   💬 Комментарий: {}".format(comment))

            # Координаты
            lat = record.get('location_latitude')
            lon = record.get('location_longitude')
            if lat and lon and str(lat).strip() and str(lon).strip():
                result_lines.append("\n🗺️  Координаты: {}, {}".format(lat, lon))

            # Финансы
            amount = record.get('amount_charged')
            if amount is not None and str(amount).strip():
                result_lines.append("💰 Сумма: {} ₽".format(amount))

            # Техническая информация
            user_id = record.get('user_id')
            if user_id is not None and str(user_id).strip():
                result_lines.append("\n🆔 User ID: {}".format(user_id))

            user_agent = record.get('user_agent')
            if user_agent and str(user_agent).strip():
                agent = str(user_agent)
                agent_preview = agent[:50] + "..." if len(agent) > 50 else agent
                result_lines.append("📱 User Agent: {}".format(agent_preview))

            created_at = record.get('created_at')
            if created_at and str(created_at).strip():
                result_lines.append("📅 Дата: {}".format(created_at))

        return '\n'.join(result_lines)

    except Exception as e:
        return "❌ Ошибка при чтении файла: {}".format(e)


def admin_main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊‍ Статистика", callback_data='stats')],
        [InlineKeyboardButton(text='✉️ Рассылка', callback_data='broadcast')],
        [InlineKeyboardButton(text='⚙️ Доп настройки', callback_data='settings')]
    ])
    return keyboard


def back_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Back', callback_data='back')],
    ])
    return keyboard




@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id == ADMIN_ID :
        await message.answer("Добро пожаловать в админ панель бота 🌍❤️!", reply_markup=admin_main_menu())
        return
    else:
        await message.answer('❌ У вас нет доступа к этой команде.')
        return



@router.callback_query(F.data == 'back')
async def back_menu(callback: CallbackQuery):
    await callback.message.answer("", reply_markup=admin_main_menu())
    await callback.answer('')


@router.callback_query(F.data == 'stats')
async def stats_process(callback: CallbackQuery):
    db = SessionLocal()
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.active == True).count()
    db.close()
    text = f'<b>Статистика:</b>\n<b>Всего пользователей 🕵️: {total_users}</b>\n<b>Активных пользователей 🎮: {active_users}</b>'
    await callback.message.answer(f'{text}',parse_mode="HTML")
    await callback.answer('')


@router.callback_query(F.data == 'broadcast')
async def broadcast_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите текст для рассылки ✉️")
    await state.set_state(BroadcastState.wait_text)
    await callback.answer('')


@router.callback_query(F.data == 'settings')
async def settings(callback: CallbackQuery):
    await callback.message.answer("Здесь ничего нет ")
    await callback.answer('')
@router.message(BroadcastState.wait_text)
async def broadcast_mess(message: Message, state: FSMContext, bot: Bot):
    broadcast_text = message.text
    db = SessionLocal()
    users_list = db.query(User).filter(User.active == True).all()
    count = 0
    for user in users_list:
        try:
            await bot.send_message(user.telegram_id, broadcast_text)
            count += 1
        except Exception as e:
            print(f'Failed to send to {user.telegram_id}:{e}')
    new_broadcast = BroadCast(message=broadcast_text)
    db.add(new_broadcast)
    db.commit()
    db.close()
    await message.answer(f"Рассылка завершена ✉️ ! Сообщение отправлено {count} пользователям 🕵️.",
                         )
    await state.clear()





@router.message(CommandStart())
async def start(message: Message):
    db = SessionLocal()
    exiting = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    if not exiting:
        new_user = User(telegram_id=message.from_user.id, name=message.from_user.full_name,
                        register_at=datetime.now().isoformat())
        db.add(new_user)
        db.commit()
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    if message.from_user.id == ADMIN_ID:
        user.premium = True
        db.commit()

    register_at = user.register_at
    premium = user.premium
    db.close()
    if premium is True:
        premium = '✅'
    else:
        premium = '❌'

    await message.reply(
        f'ℹ️ Вся необходимая информация о вашем профиле\n\n🏷️ <b>Имя:</b> <a href="tg://copy?text=ddddd">{message.from_user.full_name}</a>\n🆔 <b>Мой ID:</b> <a href="tg://copy?text=ddddddd">{message.from_user.id}</a>\n\n📆 <b>Регистрация:</b> <a href="tg://copy?text=fdddd">{register_at}</a>\n🔃 <b>TG Премиум:</b> {message.from_user.is_premium}\n\n🔑 <b>Подписка:</b> {premium}\n🗣️ \n💰 Твой баланс: <a href="tg://copy?text=0.00">0.00 RUB</a>\n',
        reply_markup=main_menu(), parse_mode="HTML")


@router.callback_query(F.data == 'premium')
async def premium_get(callback:CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔑 Подписка ', callback_data='subscribe')],
        [InlineKeyboardButton(text='🤝 Поддержка бота', callback_data='support_bot')]
    ])
    await callback.answer('')
    await callback.message.answer('🔃 Выберите вариант:', reply_markup=keyboard)

@router.callback_query(F.data == 'subscribe')
async def premium_getting(callback: CallbackQuery):
    prices = [LabeledPrice(label="XTR", amount=250)]

    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == str(callback.from_user.id)).first()

    if user and user.premium:
        await callback.answer('❌ У вас уже есть подписка!', show_alert=True)
        db.close()
        return

    db.close()
    await callback.answer('')

    await callback.message.answer_invoice(
        title='🔑 Premium подписка',
        description='• Доступ к расширенному поиску\n• Приоритетная поддержка',
        prices=prices,
        provider_token='',
        payload='premium_subscription',
        currency='XTR',
        reply_markup=payment
    )


@router.callback_query(F.data == 'support_bot')
async def support_to_bot(callback: CallbackQuery):
    prices = [LabeledPrice(label="XTR", amount=20)]
    await callback.answer('')

    await callback.message.answer_invoice(
        title='🤝 Поддержка бота',
        description='Поддержите разработку бота звездами ⭐',
        prices=prices,
        provider_token='',
        payload='bot_support',
        currency='XTR',
        reply_markup=payment,
    )


@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    payment_system = message.successful_payment
    payload = payment.invoice_payload  # Получаем payload
    user_id = str(message.from_user.id)

    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == user_id).first()

    if not user:

        user = User(telegram_id=user_id, name=message.from_user.full_name)
        db.add(user)
        db.commit()

    # Обрабатываем разные типы платежей
    if payload == 'premium_subscription':
        # Покупка подписки
        user.premium = True

        db.commit()

        await message.answer(
            f"✅ **Premium 🔑Подписка активирована!**\n\n"
            f"⭐ Получено: {payment.total_amount} звёзд\n"
            f"Спасибо за покупку! 🎉",
             message_effect_id="5104841245755180586"


        )

    elif payload == 'bot_support':

        await message.answer(
            f"🎉 **Спасибо за поддержку!** 🎉\n\n"
            f"⭐ Получено: {payment.total_amount} звёзд\n"
            f"👤 От: {message.from_user.full_name}\n\n"
            f"💝 Ваша поддержка помогает боту развиваться!",
            message_effect_id="5104841245755180586"
        )

    db.close()

@router.callback_query(F.data == 'search')
async def search_first_step(callback:CallbackQuery,state:FSMContext):
    await callback.answer('')
    await callback.message.answer('📱Введите номер телефона который вы хотите найти')
    await state.set_state(Find.telephone)

@router.message(Find.telephone)
async def search_phoned(message:Message,state:FSMContext):
    telephone = message.text.strip().replace('+','').replace(' ','').replace('-','')
    if len(telephone) < 10:
        await message.answer('📱 Телефона не корректен')
        await state.clear()
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🟢 WhatsApp', url=f'https://wa.me/+{telephone}'),
         InlineKeyboardButton(text='🟣 Viber', url=f'https://viber.click/+{telephone}')],
        [InlineKeyboardButton(text='🔵 Telegram', url=f'https://t.me/+{telephone}'),
         InlineKeyboardButton(text='🔴 Сайт', url='https://tg-user.id/from/username/')]
    ])
    getting_phone = search_by_phone(telephone, "voronezh-79000144022-79999995432.csv")
    get_piter_phone = search_by_phone(telephone, "petersburg-79817904189-79999999897.csv")
    rostov_phone = search_by_phone(telephone, "database-telephone.csv")
    await message.answer(f"{getting_phone}\n{get_piter_phone}\n{rostov_phone}", parse_mode='HTML',
                         reply_markup=keyboard)
    await state.clear()

@router.callback_query(F.data == 'profile')
async def profile_answer(callback:CallbackQuery):
    db = SessionLocal()

    user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()

    register_at = user.register_at
    premium = user.premium
    if premium is True:
        premium = '✅'
    else:
        premium = '❌'

    await callback.answer('')

    db.close()
    await callback.message.reply(
        f'ℹ️ Вся необходимая информация о вашем профиле\n\n🏷️ <b>Имя:</b> <a href="tg://copy?text=ddddd">{callback.from_user.full_name}</a>\n🔗<b>Username:</b> @{callback.from_user.username}\n\n🆔 <b>Мой ID:</b> <a href="tg://copy?text=ddddddd">{callback.message.from_user.id}</a>\n📆 <b>Регистрация:</b> <a href="tg://copy?text=fdddd">{register_at}</a>\n🔃 <b>TG Премиум:</b> {callback.message.from_user.is_premium}\n\n🔑 <b>Подписка:</b> {premium}\n🗣️ <b>Язык:</b> <b>{callback.message.from_user.language_code}</b>\n\n💰 Твой баланс: <a href="tg://copy?text=0.00">0.00 RUB</a>\n',
         parse_mode="HTML",reply_markup=main_menu())

