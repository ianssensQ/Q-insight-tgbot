from app.services.rabbit.utils.parser_init import client
from datetime import datetime, timedelta
import pytz


async def fetch_messages(channel_username, limit=150, days=1):
    async with client:
        channel = await client.get_entity(channel_username)
        messages = []
        timezone = pytz.utc
        end_date = datetime.now(timezone).replace(tzinfo=None)
        start_date = (end_date - timedelta(days=days)).replace(tzinfo=None)

        async for message in client.iter_messages(channel, limit=limit, offset_date=start_date, reverse=True):
            message_date = message.date.replace(tzinfo=None)
            if message_date > end_date:
                break
            message_data = {
                'post_date': message.date,
                'post_text': message.text,
                'post_url': f'{channel_username}/{message.id}'
            }
            messages.append(message_data)
        return messages

