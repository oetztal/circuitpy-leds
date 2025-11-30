import asyncio


class Control:

    def __init__(self):
        self.current_show = None

    async def execute(self, pixels, index):
        if self.current_show:
            await self.current_show.execute(pixels, index)
        else:
            pixels.fill((0, 0, 0))
            pixels.show()
            await asyncio.sleep(0.1)
