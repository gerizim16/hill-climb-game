import pyglet

from .resources import engine_sfx


class EngineSound(pyglet.media.Player):
    def __init__(self):
        super().__init__()
        looper = pyglet.media.SourceGroup(engine_sfx.audio_format, None)
        looper.loop = True
        looper.queue(engine_sfx)
        self.queue(looper)
