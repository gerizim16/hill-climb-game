import pyglet


class TextInput(object):
    def __init__(self, batch, position, width, font_size=14):
        x, y = position
        self.document = pyglet.text.document.UnformattedDocument('')
        self.document.set_style(0, len(self.document.text), dict(
            # font_name='Times New Roman',
            font_size=font_size,
            color=(0, 0, 0, 255),
        ))
        font = self.document.get_font()
        height = font.ascent - font.descent

        self.layout = pyglet.text.layout.IncrementalTextLayout(
            self.document, width, height, multiline=False, batch=batch)
        self.layout.x = x
        self.layout.y = y

        self.caret = pyglet.text.caret.Caret(self.layout)

        pad = 5
        self.background = batch.add_indexed(
            4, pyglet.gl.GL_TRIANGLES, None,
            [0, 1, 3, 1, 2, 3],
            ('v2f', (x-pad, y-pad, 
                     x-pad, y+height+pad, 
                     x+width+pad, y+height+pad,
                     x+width+pad, y-pad)),
            ('c3B', (255, 255, 255)*4)
        )
