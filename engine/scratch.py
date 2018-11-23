import pyglet


engine_sfx = pyglet.media.load('./resources/engine_sfx.wav', streaming=False)
looper = pyglet.media.SourceGroup(engine_sfx.audio_format, None)
looper.loop = True
looper.queue(engine_sfx)
player = pyglet.media.Player()
player.queue(looper)
player.play()

def update(dt):
    global player
    player.pitch = (player.pitch+0.01)%4
    # player.pitch = 0
    
    pass
    # print('hi')

pyglet.clock.schedule_interval(update, 1/60.0)
pyglet.app.run()