import asyncio


class Control:

    def __init__(self, pixels):
        self.current_show = None
        self.pixels = pixels

    async def execute(self, index):
        if self.current_show:
            await self.current_show.execute(index)
        else:
            self.pixels.fill((0, 0, 0))
            self.pixels.show()
            await asyncio.sleep(0.1)
