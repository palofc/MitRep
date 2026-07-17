from curses import wrapper,echo,noecho,KEY_BACKSPACE,A_BOLD,A_UNDERLINE,KEY_UP,KEY_DOWN,curs_set,KEY_RESIZE,resize_term
from queue import Queue
import threading,socket,os
from json import dumps,loads

messages = Queue()
ip = input("Enter IP: ")
port = int(input("Enter port: "))

idx = 0
text = ""
word = ""
history = []
refreshed = False

def setup(stdscr):
    os.write(1, b"\x1b[2J")
    noecho()
    curs_set(0)
    stdscr.keypad(True)
    stdscr.timeout(20)
    stdscr.refresh()


def newmessage(stdscr,message):
    stdscr.clear()
    global history
    stdscr.nodelay(True)    
    
    if message != "":
        history.append(message)     # Adds json message to a list containing all messages that can fit in the window
        height, width = stdscr.getmaxyx()

        visible = height - 2
        start = max(0, len(history) - visible - idx)
        end = start + visible

        if len(history) > visible:
            bounded = history[start:end] 

        else:
            bounded = history

        for text in range(len(bounded)):    # Traverses through history where text is its index
            
            msg_dict = loads(bounded[text])     # Loads all data from json to respective variables

            if msg_dict["type"] == "announcement":
                   stdscr.addstr(text,0,msg_dict["msg"],A_BOLD)

            else:
                 username = msg_dict["username"]
                 msg = msg_dict["msg"]
                 stdscr.addstr(text,0,username + ": ",A_BOLD)    # Draws username as bold        
                 stdscr.addstr(msg)   #Draws the message

        stdscr.move(height-1,14)


def draw_messages(stdscr):
    global refreshed
    refreshed = True
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    visible = height - 2
    start = max(0, len(history) - visible - idx)
    end = start + visible

    if len(history) > visible:
        bounded = history[start:end] 

    else:
        bounded = history

    for text in range(len(bounded)):    # Traverses through history where text is its index
        
        msg_dict = loads(bounded[text])     # Loads all data from json to respective variables

        if msg_dict["type"] == "announcement":
            stdscr.addstr(text,0,msg_dict["msg"],A_BOLD)

        else:
            username = msg_dict["username"]
            msg = msg_dict["msg"]
            stdscr.addstr(text,0,username + ": ",A_BOLD)    # Draws username as bold        
            stdscr.addstr(msg)   #Draws the message

    stdscr.move(height-1,0)
    stdscr.clrtoeol()
    stdscr.addstr(height-1,0,"Type message: ",A_BOLD) 
    stdscr.addstr(word)

def getinput(stdscr):
    global word,history,idx
    key = stdscr.getch()
    height, width = stdscr.getmaxyx()

    if key in (127,8,KEY_BACKSPACE):    #Checks if key is backspace
        word = word[:-1]

    elif key in (10,13):    #Checks if key is enter
        if word == "!clear":
            history = []
            idx = 0
            stdscr.clear()
                        
        else:
            message: dict = {}      #Prepares to load word into a json to send to server
            message["msg"] = word.strip()
            message["type"] = "text"

            if message["msg"].startswith("!"):
                message["type"] = "command"

            json_string = dumps(message)
            s.sendall(json_string.encode())  #Dumps message into a json and sends the json
        
        word = ""

    elif 32 <= key <= 126:  #Checks if key is in printable range
        word += chr(key)

    if key in (259,KEY_UP):
        idx += 1
        if idx >= len(history):
            idx = len(history)

    if key in (258,KEY_DOWN):
        idx -= 1
        if idx < 0:
            idx = 0

    max_scroll = max(0, len(history) - (height - 2))
    idx = min(idx, max_scroll)

    if key == KEY_RESIZE:
        draw_messages(stdscr)

    

def recieve_message():
    while True:
        text = s.recv(1024).decode()
        messages.put(text)


def main(stdscr):
    setup(stdscr)

    while True:
        refreshed = False
        while not messages.empty():
            newmessage(stdscr,messages.get())
        getinput(stdscr)
        if not refreshed:
            draw_messages(stdscr)
        stdscr.refresh()


s = socket.socket()
s.connect((ip,port))


input_thread = threading.Thread(target=recieve_message, daemon = True)
input_thread.start()

wrapper(main)
