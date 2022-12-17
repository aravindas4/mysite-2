import asyncio
from channels.layers import get_channel_layer


def send_messages_to_room(room_name, message):

    channel_layer = get_channel_layer()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop=loop)

    loop.run_until_complete(
        channel_layer.group_send(
            room_name,
            {
                "type": "chat_message",
                "message": message
            }
        )
    )