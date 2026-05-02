
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Expedition


class ExpeditionConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        user = self.scope["user"]

        if user.is_anonymous:
            await self.close()
            return

        self.user = user
        self.groups = []

        expeditions = await self.get_user_expeditions()

        for expedition_id in expeditions:
            group_name = f"expedition_{expedition_id}"
            await self.channel_layer.group_add(group_name, self.channel_name)
            self.groups.append(group_name)

        await self.accept()

    async def disconnect(self, close_code):
        for group in self.groups:
            await self.channel_layer.group_discard(group, self.channel_name)

    @database_sync_to_async
    def get_user_expeditions(self):
        return list(
            Expedition.objects.filter(
                chief=self.user
            ).values_list("id", flat=True)
        ) + list(
            Expedition.objects.filter(
                members__user=self.user
            ).values_list("id", flat=True)
        )

    async def expedition_event(self, event):
        await self.send_json(event["data"])
