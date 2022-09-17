class EventHandler():
    def __init__(self, q):
        self._queue = q


    async def get_item(self):
        item = await self._queue.get()
        return item

    async def listen_for_events(self):  
        '''
        Asynchronously check the event queue for new incoming events
        '''
        while True:
            await self.get_item()