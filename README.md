# chat_app
- socket programing -- chat app, have client and server
- before run, make sure using python 3.10 and fulfil the requirement libraries list in requirement.txt 

## Read Flow
- client: to run, call client_gui.py
  - frontend: client_gui.py -- prompt the user for action and display the process response
  - backend: client.py -- the logic and actual communication with the server

- server: to run, call server.py
  - server-logic: server.py -- listening and handling incoming connection and request.
  - server-database: db_logic.py -- database helper module, communicate with users and messages database