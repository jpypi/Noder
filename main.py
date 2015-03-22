#!/usr/local/bin/python
import pyglet
from pyglet.window import key
import sys
import math
import itertools


window = pyglet.window.Window(width=1200, height=480)
window.set_vsync(True)

helv_font=pyglet.font.load("Helvetica", 14)
fps_display = pyglet.clock.ClockDisplay(helv_font, color=(1, 0, 0, 1))

class Oval(object):
    def __init__(self, size, center):
        self.points=[]
        self.width =size[0]/2
        self.height=size[1]/2
        self.center=center

        xs = range(-self.width, self.width+1)
        sx = xs[:]
        sx.reverse()
        for i, x in enumerate(xs+sx): 
            y=int(math.sqrt((1-(float(x)/self.width)**2))*self.height)
            if i>self.width*2: y*=-1
            self.points.extend((x+self.center[0], y+self.center[1]))

        self.top=center[1]+self.height
        self.bottom=center[1]-self.height
    
    def draw(self):
        pyglet.graphics.draw(len(self.points)/2, pyglet.gl.GL_LINE_LOOP, ("v2i", self.points))

    def move(self,vector):
        vector_cycle=itertools.cycle(vector)
        for i in xrange(len(self.points)):
            self.points[i]+=vector_cycle.next()


class TextOval(Oval):
    def __init__(self, text, center, min_width=None, lines=1, padding=15):
        self.text_string=text
        self.text=pyglet.font.Text(helv_font, self.text_string, x=center[0], y=center[1]-padding/2, halign="center")
        oval_width=self.text.width+padding
        if min_width:
            oval_width=max(oval_width, min_width)
        super(TextOval, self).__init__((oval_width, self.text.height+padding), center)

    def draw(self):
        super(TextOval, self).draw()
        self.text.draw()

    def move(self,vector):
        super(TextOval, self).move(vector)
        self.text.x+=vector[0]
        self.text.y+=vector[1]


class Line:
    def __init__(self, start, end):
        self.start=list(start)
        self.end=list(end)

    def draw(self):
        pyglet.graphics.draw(2, pyglet.gl.GL_LINE_STRIP, ("v2i", (self.start[0], self.start[1], self.end[0], self.end[1])))

    def move(self,vector):
        self.start[0]+=vector[0]
        self.start[1]+=vector[1]
        self.end[0]+=vector[0]
        self.end[1]+=vector[1]


class Node:
    def __init__(self, text, children=[]):
        self.text=text
        self.children=children
        self.lines=[]

    def setChildren(self, children):
        self.children=children

    def generateGraphics(self, initial_position, remaining_depth, grow_width, padding=15, node_padding=10):
        self.graphics=TextOval(self.text, initial_position, min_width=grow_width+padding, padding=padding)
        for i, child in enumerate(self.children):
            box_size = 2**(remaining_depth-1)*(grow_width+padding+node_padding)

            x=initial_position[0] - box_size + box_size*i+box_size/2
            y=initial_position[1] - self.graphics.height*2-box_size/6

            child.generateGraphics((int(x), int(y)), remaining_depth-1, grow_width, padding, node_padding)
            
            self.lines.append(Line((self.graphics.center[0], self.graphics.bottom), \
                                   (child.graphics.center[0], child.graphics.top)))

    # Recursivly go through children drawing them and their children
    def treeDraw(self):
        try:
            self.graphics.draw()
            for child in self.children:
                child.treeDraw()

            for line in self.lines:
                line.draw()
        except AttributeError:
            pass # Can't draw if we don't have graphics
    
    def move(self,vector):
        self.graphics.move(vector)
        for line in self.lines:
            line.move(vector)


#o = TextOval("This is a long node", (window.width/2, window.height/2))
#o2= TextOval("Another", (window.width/2+50, window.height/2+50))
#l = Line((o.center[0], o.top), (o2.center[0], o2.bottom))

f=open("nodes.csv", "r")
nodes=[Node(line.strip()) for line in f.xreadlines()]
f.close()

max_size=0
for i, node in enumerate(nodes):
    size=pyglet.font.Text(helv_font, node.text).width
    max_size=max(max_size, size)
    child_nodes=[]
    for j in xrange(1, 3):
        try: child_nodes.append(nodes[2*i+j])
        except IndexError: pass
    node.setChildren(child_nodes)

tree_depth = math.ceil(math.log(i, 2))
print "\n\nTree height: %d\n\n"%tree_depth
root_node=nodes[0]
root_node.generateGraphics((window.width/2, window.height-20), tree_depth-1, grow_width=max_size, node_padding=6)

def MoveNodes(x,y):
    for node in nodes:
        node.move((x,y))


@window.event
def on_draw():
    window.clear()

    pyglet.gl.glPointSize(1)

    root_node.treeDraw() 
    
    fps_display.draw()


SPEED=5
@window.event
def on_text(symbol):#,modifiers):
    if symbol=="w":#key.W:
        MoveNodes(0,SPEED)
    if symbol=="s":#key.S:
        MoveNodes(0,-SPEED)
    if symbol=="a":#key.A:
        MoveNodes(-SPEED,0)
    if symbol=="d":#key.D:
        MoveNodes(SPEED,0)

##pyglet.clock.schedule_interval(main_update, 1/60.0)
##window.push_handlers(pyglet.window.event.WindowEventLogger())

pyglet.app.run()
