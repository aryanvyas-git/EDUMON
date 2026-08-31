from channels.generic.websocket import AsyncWebsocketConsumer

# Full implementation added in Phase 5 (real-time chat, R1g).


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.close()
