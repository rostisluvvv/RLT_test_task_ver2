import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import Config, load_config
from user_handlers import register_user_handlers

logger = logging.getLogger(__name__)


def register_all_handlers(dp: Dispatcher) -> None:
    register_user_handlers(dp)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s '
               u'[%(asctime)s] - %(name)s - %(message)s')

    logger.info('Starting bot')

    config: Config = load_config('.env')

    bot: Bot = Bot(token=config.tg_bot.token, parse_mode='HTML')

    dp: Dispatcher = Dispatcher(bot)
    register_all_handlers(dp)
    try:
        await dp.start_polling()
    finally:
        await bot.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except(SystemExit):
        logger.error("Bot stopped!")
