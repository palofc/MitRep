from curses import wrapper,echo,noecho,KEY_BACKSPACE,A_BOLD
from queue import Queue
import threading,socket,os
from json import dumps,loads

messages = Queue()
ip = input("Enter IP: ")
port = int(input("Enter port: "))

text = ""
word = ""
history = []

def setup(stdscr):
    os.write(1, b"\x1b[2J")
    noecho()
    stdscr.keypad(True)
    stdscr.timeout(20)
    stdscr.refresh()




def newmessage(stdscr,message):
    stdscr.clear()      #clears the terminal to redraw all the messages
    stdscr.nodelay(True)

    if message != "":
        history.append(message)     # Adds json message to a list containing all messages that can fit in the window
        height, width = stdscr.getmaxyx()

        while len(history) > height - 2:        #removes data from history until all of them can fit in the terminal
            history.remove(history[0])

        for text in range(len(history)):    #Traverses through history where text is its index
            msg_dict = loads(history[text])     #Loads all data from json to respective variables

            if msg_dict["type"] == "announcement":
                stdscr.addstr(text,0,msg_dict["msg"])

            else:
                username = msg_dict["username"]
                msg = msg_dict["msg"]

                stdscr.addstr(text,0,username + ": ",A_BOLD)    #Draws username as bold        
                stdscr.addstr(msg)   #Draws the message

        stdscr.move(height-1,14)


def getinput(stdscr):
    global word,history
    key = stdscr.getch()

    if key in (127,8,KEY_BACKSPACE):    #Checks if key is backspace
        word = word[:-1]

    elif key in (10,13):    #Checks if key is enter
        if word == "!clear":
            history = []
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

    height, width = stdscr.getmaxyx()
    stdscr.move(height-1,0)
    stdscr.clrtoeol()
    stdscr.addstr(height-1,0,"Type message: " + word)


def recieve_message():
    while True:
        text = s.recv(1024).decode()
        messages.put(text)

def main(stdscr):
    setup(stdscr)

    while True:
        while not messages.empty():
            newmessage(stdscr,messages.get())
        getinput(stdscr)
        stdscr.refresh()


s = socket.socket()
s.connect((ip,port))


input_thread = threading.Thread(target=recieve_message, daemon = True)
input_thread.start()

wrapper(main)
