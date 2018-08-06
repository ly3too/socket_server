#!/usr/bin/env python3
'''
    clients -> messageque1 -> Sinker (to db)
    webserver -> messageque2 -> clients(observer)
'''
import threading
from threading import Thread
from threading import Lock
import socket
import os, fcntl
import selectors
import sqlite3
from datetime import datetime
import errno
import copy


class Mydb:
    MAX_BUF_SIZE = 8192

    def __init__(self, name:str):
        self.db = sqlite3.connect(name)
        self.db.execute("create table if not exists datas(time datetime, data text)")
        self.db.commit()

    def save_data(self, data: str):
        cur = self.db.cursor()
        cur.execute("insert into datas values(?, ?)", (datetime.now(), data))
        self.db.commit()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

class MessageQue:
    def __init__(self):
        self.data = ""
        self.lock = Lock()


class ClientHandler:
    def __init__(self, db: Mydb):
        self.db = db
        self.datas = ""
        self.data_to_write = ""

    def on_ready_read(self, key, sel: selectors.EpollSelector, keys):
        '''
        read data from client and save to the buffer of itself. then sink to database (line based)
        :return:
        '''
        data = b''
        try:
            data = key.fileobj.recv(1024)
            print("client read: " + data.decode('utf-8'))
        except IOError as e:
            print(e.strerror)

        if not data:
            # client stoped to send
            print('client: ', key.fd, " closed")
            keys.discard(key)
            key.fileobj.close()
            sel.unregister(key.fileobj)

            # sink data left
            if self.datas:
                if self.datas[-1] != '\n':
                    self.datas += '\n'
                self.db.save_data(self.datas)
                self.datas = ""

        else:
            # received some data
            self.datas += data.decode()
            datas = self.datas.split('\n')
            for i in range(len(datas)-1):
                self.db.save_data(datas[i])
            self.datas = datas[-1]

    def on_ready_write(self, key, data:str, keys:set):
        '''
        check if data ready in messageque, append to the buffer of itself. try to send all data to client
        :return:
        '''
        print("send message to client: ", key.fd)
        try:
            self.data_to_write += data
            num = key.fileobj.send(self.data_to_write.encode())
            self.data_to_write = self.data_to_write[num:]
        except IOError as e:
            print(e.strerror)
            keys.discard(key)
            key.fileobj.close()



class WebHandler:
    def __init__(self, messageque: MessageQue):
        self.messageque = messageque
        self.datas = ""

    def on_ready_read(self, key, sel: selectors.EpollSelector):
        '''
        read data into the buffer of itself and write lines to messageque
        :return:
        '''
        data = b''
        try:
            data = key.fileobj.recv(1024)
            print('received from webserver: ', data.decode())
        except IOError as e:
            print(e.strerror)

        if not data:
            # web server closed
            print('fd: ', key.fd, "closed")
            sel.unregister(key.fileobj)
            key.fileobj.close()
            if self.datas:
                if self.datas[-1] != '\n':
                    self.datas += '\n'
                self.messageque.lock.acquire()
                self.messageque.data += self.datas
                self.messageque.lock.release()
        else:
            # received some data
            self.datas += data.decode()
            datas = self.datas.split('\n')
            self.messageque.lock.acquire()
            for i in range(len(datas)-1):
                self.messageque.data += datas[i] + '\n'
            self.messageque.lock.release()
            self.datas = datas[-1]


class MyServer:

    def __init__(self, host, port, messageque:MessageQue, handlerClass, initer):
        self.lstn_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lstn_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.lstn_sock.bind((host, port))
        self.lstn_sock.setblocking(False)
        self.enabled = True
        self.sel = selectors.EpollSelector()
        self.lstn_sock.listen(5)
        self.initer = initer
        self.handlerClass = handlerClass
        self.messageque = messageque
        print("socket {} listening {}:{} ".format(self.lstn_sock, host, port))

    def run(self):
        print("{} running".format(threading.current_thread()))
        self.sel.register(self.lstn_sock, selectors.EVENT_READ, self.lstn_sock)
        self.keys = set()
        self.db = Mydb(*self.initer)

        while self.enabled:
            for key, mask in self.sel.select(1):
                if key.data == self.lstn_sock:
                    conn, addr = self.lstn_sock.accept()
                    print("server accteped: ", conn.fileno(), "from ", addr)
                    conn.setblocking(False)
                    newkey = self.sel.register(conn, selectors.EVENT_READ, self.handlerClass(self.db))
                    self.keys.add(newkey)
                else:
                    handler = key.data
                    print("fd: {} ready to be read".format(key.fd))
                    handler.on_ready_read(key, self.sel, self.keys)

            # check if there is data to write to clients
            self.messageque.lock.acquire()
            data_from_web = ""
            if (self.messageque.data):
                data_from_web = copy.deepcopy(self.messageque.data)
                self.messageque.data = ""
            self.messageque.lock.release()
            if data_from_web:
                for key in self.keys.copy():
                    key.data.on_ready_write(key, data_from_web, self.keys)


class WebListener:

    def __init__(self, host, port, messageque:MessageQue, handlerClass):
        self.lstn_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lstn_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.lstn_sock.bind((host, port))
        self.lstn_sock.setblocking(False)
        self.enabled = True
        self.sel = selectors.EpollSelector()
        self.lstn_sock.listen(5)
        self.handlerClass = handlerClass
        self.messageque = messageque
        print("socket {} listening {}:{} ".format(self.lstn_sock, host, port))

    def run(self):
        print("{} running".format(threading.current_thread()))
        self.sel.register(self.lstn_sock, selectors.EVENT_READ, self.lstn_sock)

        while self.enabled:
            for key, mask in self.sel.select(1):
                if key.data == self.lstn_sock:
                    conn, addr = self.lstn_sock.accept()
                    print("weblistener accteped: ", conn.fileno(), "from ", addr)
                    conn.setblocking(False)
                    self.sel.register(conn, selectors.EVENT_READ, self.handlerClass(self.messageque))
                else:
                    handler = key.data
                    handler.on_ready_read(key, self.sel)


if __name__ == "__main__":
    path = os.path.dirname(os.path.realpath(__file__))
    print(path)
    messageque = MessageQue()
    client_server = MyServer('0.0.0.0', 8000, messageque, ClientHandler, [path+'/test.db'])
    web_listener = WebListener('localhost', 8001, messageque, WebHandler)
    t2 = Thread(target=web_listener.run)
    t1 = Thread(target=client_server.run)
    t1.start()
    t2.start()

    t1.join()
    t2.join()
    exit(0)

