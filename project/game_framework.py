from pico2d import *
import time

running = True
state = None

def run(start_state):
    global running, state
    state = start_state
    running = True
    state.enter()
    last = time.time()
    while running:
        now = time.time()
        dt = now - last
        last = now
        events = get_events()
        state.handle_events(events)
        state.update(dt)
        state.draw()
        delay(0.001)
    state.exit()

def change_state(next_state):
    global state
    state.exit()
    state = next_state
    state.enter()

def quit():
    global running
    running = False
