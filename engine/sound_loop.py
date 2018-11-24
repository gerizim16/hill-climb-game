import pyglet


class SoundLoop(pyglet.media.Player):
    def __init__(self, sound):
        super().__init__()
        looper = pyglet.media.SourceGroup(sound.audio_format, None)
        looper.loop = True
        looper.queue(sound)
        self.queue(looper)
