# a simple socket server 

#### this is a simple demo to serve and collect data from clients, at the same time users can send messages to all connected clients <br>  简单的 socket 服务器，获取客户端的数据并保存在数据库，同时用户可以通过网页发送数据给客户端

the socket server should be able to handle large amount of clients at the same time, though I haven't tested it

## the project include those files:
| file name | usage |
| :-------| :------------|
|index.php | the web entrance, the only page users should see | 
|clear_data.php | clear all data in db, users need not care|
|get_datas.php | backend to get data from db, users need not care|
|send_message.php | backend to send message to socket server, users need not care|
| main.py | the socket server |

## fire up the socket server and web server manualy without installation
```bash
# in project directory
python3 mian.py &
php -S 0.0.0.0:8080 &
```

## clients connect to socket server
use port: 8000

protocol: raw socket

## install 
```bash
sudo apt update
sudo apt install php7.2-cli
sudo apt install php7.2-sqlite3
sudo apt install python3
# in project directory
sh install.sh
```

## uninstall 
```bash
sh uninstall.sh
```

## run and stop the server
```bash
myserver start
myserver stop
```

## open the browser at http://<your ip or url>:8080
you should se something like this
![](./statics/imag1.png)

