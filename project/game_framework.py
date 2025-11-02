from pico2d import *
import time

stack = []
running = False

def run(start_state):
    global running, stack
    running = True
    stack = [start_state]
    start_state.enter()
    while running and stack:
        state = stack[-1]
        state.handle_events()
        state.update()
        state.draw()
        delay(0.001)
        if hasattr(state, 'get_running') and not state.get_running():
            quit()
    while stack:
        stack.pop().exit()

def change_state(state):
    if stack:
        stack[-1].exit()
        stack.pop()
    stack.append(state)
    state.enter()

def push_state(state):
    if stack:
        if hasattr(stack[-1], 'pause'):
            stack[-1].pause()
    stack.append(state)
    state.enter()

def pop_state():
    if stack:
        stack[-1].exit()
        stack.pop()
    if stack:
        if hasattr(stack[-1], 'resume'):
            stack[-1].resume()
    else:
        quit()

def quit():
    global running
    running = False
