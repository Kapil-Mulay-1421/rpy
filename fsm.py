import time
from enum import Enum


# ---------------- STATES ----------------
class State(Enum):
    IDLE = 1
    STATE_A = 2
    STATE_B = 3
    ERROR = 4


current_state = State.IDLE


# ---------------- STATE FUNCTIONS ----------------
def handle_idle():
    global current_state

    print("In IDLE")

    # condition/event
    if event_a():
        current_state = State.STATE_A


def handle_state_a():
    global current_state

    print("In STATE_A")

    if event_b():
        current_state = State.STATE_B

    elif error_detected():
        current_state = State.ERROR


def handle_state_b():
    global current_state

    print("In STATE_B")

    if task_complete():
        current_state = State.IDLE


def handle_error():
    global current_state

    print("In ERROR")

    if reset_event():
        current_state = State.IDLE


# ---------------- EVENTS ----------------
def event_a():
    return False


def event_b():
    return False


def error_detected():
    return False


def task_complete():
    return False


def reset_event():
    return False


# ---------------- MAIN LOOP ----------------
while True:

    if current_state == State.IDLE:
        handle_idle()

    elif current_state == State.STATE_A:
        handle_state_a()

    elif current_state == State.STATE_B:
        handle_state_b()

    elif current_state == State.ERROR:
        handle_error()

    time.sleep(0.05)