import pyglet


class ScrollingText(pyglet.text.layout.ScrollableTextLayout):
    def __init__(self, batch, position, width, height, text='', 
                 align='left', timeout=60*3, font_size=20, scroll_speed=1,
                 group=None):
        document = pyglet.text.document.UnformattedDocument(text)
        document.set_style(0, len(document.text), dict(
            font_size=font_size,
            color=(0, 0, 0, 255),
            align=align
        ))
        super().__init__(document, width, height, multiline=True, 
                         batch=batch, group=group)
        self.x, self.y = position
        self.view_y = 0
        self.time = 0
        self.scroll_speed = scroll_speed
        self.timeout = timeout

        pad = 5
        self.background = batch.add_indexed(
            4, pyglet.gl.GL_TRIANGLES, group,
            [0, 1, 3, 1, 2, 3],
            ('v2f', (self.x-pad, self.y-pad, 
                     self.x-pad, self.y+height+pad, 
                     self.x+width+pad, self.y+height+pad,
                     self.x+width+pad, self.y-pad)),
            ('c3B', (255, 255, 255)*4)
        )
        
    def update_text(self, text):
        self.document.text = text

    def update(self):
        if self.time < self.timeout:
            self.time += 1
        elif self.view_y == self.height-self.content_height:
            if self.time < self.timeout*2:
                self.time += 1
            else:
                self.time = 0
                self.view_y = 0
        else:
            self.view_y = self.view_y - self.scroll_speed
