
import asyncio
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Инициализируем бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())



# --- 1. ОПРЕДЕЛЕНИЕ СОСТОЯНИЙ FSM ---
class SecretaryState(StatesGroup):
    WaitingForQuestion = State()  # Ожидание выбора вопроса или кастомного текста
    WaitingForCustomBrief = State()  # Ожидание отправки брифа/ТЗ


# --- КЛАВИАТУРЫ ---
def get_main_keyboard():
    """Главная клавиатура (Вне FSM)"""
    buttons = [
        [types.KeyboardButton(text="👤 О разработчике")],
        [types.KeyboardButton(text="❓ Задать вопрос")],
    ]
    return types.ReplyKeyboardMarkup(
        keyboard=buttons, resize_keyboard=True, one_time_keyboard=False
    )


def get_questions_keyboard():
    """Клавиатура с 4 вопросами внутри состояния WaitingForQuestion"""
    buttons = [
        [
            types.KeyboardButton(
                text="Какие боты вы делаете и сколько это стоит?"
            )
        ],
        [
            types.KeyboardButton(
                text="Как происходит передача и запуск проекта?"
            )
        ],
        [types.KeyboardButton(text="Всё ли официально? Выдаете ли вы чеки?")],
        [types.KeyboardButton(text="🚀 Мне нужен кастомный бот под мои задачи")],
    ]
    return types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


# --- ХЕНДЛЕРЫ ---


# 1. Команда /start (Свободное состояние)
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()  # Сбрасываем любые состояния на старте
    await message.answer(
        f"Привет, {message.from_user.full_name}! 👋\n\n"
        f"Я — автоматический бот-секретарь студии **Domination Squad**.\n"
        f"Помогу ответить на частые вопросы или передам твою задачу разработчику напрямую 24/7.",
        reply_markup=get_main_keyboard(),
    )


# 2. Кнопка "О разработчике" (Свободное состояние)
@dp.message(F.text == "👤 О разработчике")
async def about_developer(message: types.Message):
    await message.answer(
        "⚡️ **Студия разработки Domination Squad**\n\n"
        "• Специализация: Асинхронные Telegram-боты на aiogram 3.x (лид-магниты, авто-продажи, бизнес-визитки, воронки).\n"
        "• Локация: Воронеж, РФ.\n"
        "• Наш GitHub: [Ссылка на твой оформленный GitHub]\n\n"
        "Для прямой связи с разработчиком пишите: @domination_squad",
        parse_mode="Markdown",
    )


# 3. Кнопка "Задать вопрос" -> Переход в первое состояние FSM
@dp.message(F.text == "❓ Задать вопрос")
async def start_questions(message: types.Message, state: FSMContext):
    await state.set_state(SecretaryState.WaitingForQuestion)
    await message.answer(
        "Выберите интересующий вас вопрос на клавиатуре ниже 👇\n"
        "Если вашего вопроса нет, нажмите кнопку кастомного бота.",
        reply_markup=get_questions_keyboard(),
    )


# --- СОСТОЯНИЕ: WaitingForQuestion ---


# Хендлер Вопроса 1
@dp.message(
    SecretaryState.WaitingForQuestion,
    F.text == "Какие боты вы делаете и сколько это стоит?",
)
async def q1_answer(message: types.Message):
    await message.answer(
        "💰 **Цены и решения:**\n\n"
        "Мы создаем профессиональные лид-магнит боты, визитки и автоворонки. "
        "Базовая стоимость запуска — **3 000 ₽** (включает разработку и привязку к вашему каналу).\n\n"
        "Последующая поддержка и удержание бота на нашем скоростном сервере — **1 500 ₽/мес** через Kwork.",
        parse_mode="Markdown",
    )


# Хендлер Вопроса 2
@dp.message(
    SecretaryState.WaitingForQuestion,
    F.text == "Как происходит передача и запуск проекта?",
)
async def q2_answer(message: types.Message):
    await message.answer(
        "🔄 **Процесс запуска проекта:**\n\n"
        "1. Вы создаете бота в @BotFather и делаете его администратором вашего Telegram-канала.\n"
        "2. Передаете нам токен бота.\n"
        "3. Мы заливаем и настраиваем проект на нашем сервере (RuVDS, Москва).\n"
        "4. Вы проводите финальное тестирование, и бот начинает работать на вас 24/7!",
        parse_mode="Markdown",
    )


# Хендлер Вопроса 3
@dp.message(
    SecretaryState.WaitingForQuestion,
    F.text == "Всё ли официально? Выдаете ли вы чеки?",
)
async def q3_answer(message: types.Message):
    await message.answer(
        "🛡 **Полная официальность и безопасность:**\n\n"
        "Да! Мы работаем абсолютно легально через официальный статус **самозанятого в РФ**.\n"
        "После проведения оплаты через платформу Kwork или напрямую, вам мгновенно "
        "формируется и отправляется чек из официального приложения ФНС «Мой налог». Всё строго по закону.",
        parse_mode="Markdown",
    )


# Переход ко второму состоянию FSM (Сбор кастомного брифа)
@dp.message(
    SecretaryState.WaitingForQuestion,
    F.text == "🚀 Мне нужен кастомный бот под мои задачи",
)
async def custom_brief_start(message: types.Message, state: FSMContext):
    await state.set_state(SecretaryState.WaitingForCustomBrief)
    await message.answer(
        "📝 **Опишите вашу задачу одним сообщением.**\n\n"
        "Вы можете отправить текст, прикрепить файл с ТЗ, скриншоты или даже надиктовать голосовое сообщение. "
        "Бот скопирует его и мгновенно передаст разработчику.",
        reply_markup=types.ReplyKeyboardRemove(),  # Убираем кнопки, чтобы не мешали писать
    )


# 🔥 УМНАЯ ЗАГЛУШКА (Вариант Б): Перехватывает любой другой левый ввод в состоянии выбора вопроса
@dp.message(SecretaryState.WaitingForQuestion)
async def waiting_for_question_garbage_filter(message: types.Message):
    await message.answer(
        "⚠️ Пожалуйста, выберите один из готовых вопросов на кнопках клавиатуры.\n\n"
        "Если вы хотите описать свою индивидуальную задачу, нажмите кнопку "
        "«🚀 Мне нужен кастомный бот под мои задачи».",
        reply_markup=get_questions_keyboard(),
    )


# --- СОСТОЯНИЕ: WaitingForCustomBrief ---


# Принимает СОВЕРШЕННО ЛЮБОЙ тип контента (текст, фото, гс, файлы), отправляет админу и сбрасывает FSM
@dp.message(SecretaryState.WaitingForCustomBrief)
async def collect_and_send_brief(message: types.Message, state: FSMContext):
    # Уведомляем админа о новом бриф-заявке с кликабельным юзернеймом клиента
    user_info = (
        f"🔔 **НОВЫЙ ЗАКАЗ/ВОПРОС В БОТЕ!**\n"
        f"От: {message.from_user.full_name} (@{message.from_user.username})\n"
        f"ID пользователя: `{message.from_user.id}`\n"
        f"Ниже прикреплено сообщение клиента:\n"
        f"----------------------------------------"
    )

    try:
        # Отправляем инфо-карточку админу
        await bot.send_message(
            chat_id=ADMIN_ID, text=user_info, parse_mode="Markdown"
        )
        # Отправляем точную копию контента пользователя (текст, гс, медиа, доки) админу
        await message.send_copy(chat_id=ADMIN_ID)

        # Отвечаем пользователю и возвращаем его на главную
        await message.answer(
            "✅ **Бриф успешно отправлен разработчику!**\n\n"
            "Команда Domination Squad уже изучает вашу задачу. Мы свяжемся с вами в ближайшее время.",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown",
        )
        # СБРОС СОСТОЯНИЯ FSM
        await state.clear()

    except Exception as e:
        # На случай, если ADMIN_ID указан неверно или бот не запущен у админа
        await message.answer(
            "Произошла ошибка при отправке данных. Пожалуйста, напишите напрямую: @domination_squad"
        )
        print(f"Ошибка пересылки: {e}")


# --- ЗАПУСК БОТА (POLLING) ---
async def main():
    print("🚀 Бот-секретарь Domination Squad успешно запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
