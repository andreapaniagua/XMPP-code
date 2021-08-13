#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Andrea Paniagua
#carne 18733
#codigo consultado: https://github.com/poezio/slixmpp
import asyncio
import logging
import slixmpp
from slixmpp import ClientXMPP
from slixmpp.exceptions import IqError, IqTimeout
import sys
import getpass
import nest_asyncio
nest_asyncio.apply()

#permite evitar el error de loop y permite al sys poder detectar la plataforma que esta siendo usada pra ejecutar  los DNDs
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#clase encargada de registrar a los usuarios en el server

class RegisterBot(slixmpp.ClientXMPP):

    def __init__(self, jid, password):
        #se realiza el log in
        slixmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("register", self.register)
    #funcion principal que hace trigger al evento llamado  por process

    async def start(self, event):
        self.send_presence()
        await self.get_roster()
        self.disconnect()
        
    #registrar usuarios clase tomada del codigo de ejemplos
    async def register(self, iq):
        #mandar al nuevo usuario que sera ingresado al server
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password
        try:
            await resp.send()
            #al registrarse
            print("Account created for %s!" % self.boundjid)
        except IqError as e:
            # mensaje de error
            print("Could not register account: %s" %
                    e.iq['error']['text'])
        except IqTimeout:
            #esto ocurrira en caso el server no este levantado
            print("No response from server")
            self.disconnect()
        self.disconnect()
        
#Client es la clase encargada de los funcionamientas del usuario registrado

class Client(slixmpp.ClientXMPP):

    def __init__(self, user, passw):
        slixmpp.ClientXMPP.__init__(self, user, passw)
        self.jid = user
        self.password = passw
        self.room = ""
        self.nick = ""
        #definimos todos los handlers encargado de ejecutar las funciones y definimos los pluging que posee slixmpp, solo asi funciona segun https://profanity-im.github.io/plugins.html
        self.add_event_handler("message", self.message)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("groupchat_message", self.muc_message)
        self.add_event_handler("changed_status", self.wait_for_presences)
        self.register_plugin('xep_0030') 
        self.register_plugin('xep_0045') 
        self.register_plugin('xep_0004') 
        self.register_plugin('xep_0060') 
        self.register_plugin('xep_0199') 
        
        #definimos nuestro reciver y los precense que ejecutaran por eventos asincronos
        self.received = set()
        self.presences_received = asyncio.Event()
    #nuestra funcion para mandar mensajes a un chat grupal
    def muc_message(self, msg):

        if msg['mucnick'] != self.nick and self.nick in msg['body']:
            self.send_message(mto=msg['from'].bare,
                              mbody="I heard that, %s." % msg['mucnick'],
                              mtype='groupchat')
    #esta es la funcion encargada de manejar el chatroom
    def muc_online(self, presence):

        if presence['muc']['nick'] != self.nick:
            self.send_message(mto=presence['from'].bare,
                              mbody="Hello, %s %s" % (presence['muc']['role'],
                                                      presence['muc']['nick']),
                              mtype='groupchat')
    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            msg.reply("Thanks for sending\n%(body)s" % msg).send()

    def wait_for_presences(self, pres):
        self.received.add(pres['from'].bare)
        if len(self.received) >= len(self.client_roster.keys()):
            self.presences_received.set()
        else:
            self.presences_received.clear()
    async def start(self, event):
        self.send_presence()
        access = True
        print('connected\n')
        print("login  correcto\n")
        print("")
        while access:
            print("Menu de funciones: \n1. Mostrar todos los usuarios y su estado \n2. Agregar un usuario a contactos \n3. Mostrar detalles de un usuario \n4. Comunicacion 1 a 1 \n5. Conversacion grupal \n6. Mensaje de presencia \n7. Salir ")
            opcion = input("opcion a elegir es: ")
            if opcion == "1":
                try:
                    await self.get_roster()
                except IqError as err:
                    print('Error: %s' % err.iq['error']['condition'])
                except IqTimeout:
                    print('Error: Request timed out')
                self.send_presence()
                #se realiza una actualizacion de los presence
                print('Waiting for presence updates...\n')
                await asyncio.sleep(10)
                #varios loops que muestran los distintos detalles de los usuarios
                print('Roster for %s' % self.boundjid.bare)
                groups = self.client_roster.groups()
                for group in groups:
                    print('\n%s' % group)
                    print('-' * 72)
                    for self.jid in groups[group]:
                        sub = self.client_roster[self.jid]['subscription']
                        name = self.client_roster[self.jid]['name']
                        if self.client_roster[self.jid]['name']:
                            print(' %s (%s) [%s]' % (name, self.jid, sub))
                        else:
                            print(' %s [%s]' % (self.jid, sub))

                        connections = self.client_roster.presence(self.jid)
                        for res, pres in connections.items():
                            show = 'available'
                            if pres['show']:
                                show = pres['show']
                            print('   - %s (%s)' % (res, show))
                            if pres['status']:
                                print('       %s' % pres['status'])

            if opcion == "2":
                new_friend = (input("user: "))
                xmpp.send_presence_subscription(pto= new_friend + "@alumchat.xyz")
                print("Usuario agregado")
                #print("2")
            if opcion == "3":
                #codigo para mostrar detalles de un contanto
                print("Usuario de quien quiere saber su estatus\n")
                #obtenemos el usario a detallar
                userSt =  input("nombre del usuario: ")
                userSt = userSt + "@alumchat.xyz"
                self.send_presence()
                #roster del cliente para luego mostra los detalles del user
                await self.get_roster()
                self.client_roster
                print("Detalles: ", self.client_roster.presence(userSt))
                print("3")
            if opcion == "4":
                #codigo para enviar un mensaje 1 a 1 con otro usuario
                Userto = input("Usuario al que va dirigido el mensaje: ")
                mensaje = input("Mensaje: ")
                self.send_message(mto= UserTo + "@alumchat.xyz",
                          mbody= mensaje,
                          mtype='chat')
                print("4")
            if opcion == "5":
                #añador a chat grupal y enviar un mensaje
                print("Ingresar a un room\n")
                self.nick = input("Nombre para aparecer en el room: ")
                self.room = self.nick + "@alumchat.xyz"
                #eventhandler para manejar el room y quienes ingresan
                self.add_event_handler("muc::%s::got_online" % self.room,self.muc_online)
                await self.get_roster()
                self.send_presence()
                self.plugin['xep_0045'].join_muc(self.room,
                                         self.nick,
                                         wait=True)
                mensaje = input("Mensajer: ")
                self.muc_message(mensaje)

                print("5")
            if opcion == "6":
                #mensaje de presencia
                shw = input("Estado(chat, away, xa, dnd): ")
                stts = input("Mensaje: ")
                self.send_presence(pshow= shw, pstatus= stts)
                print("Presencia ha ambiado\n")
            if opcion == "7":
                access = False
                print("entraste")
                sys.exit("Desconectado")
                break
        print("saliste")
        self.disconnect()




if __name__ == '__main__':
    st_log = False
    print("Los mensajes que requieran usuario, requieren solo el nombre. el programa agregara el @alumchat.xyz")
    while st_log == False:
        print("Bienvenido al Proyecto 1 de chat con protocolo XMPP \n 1 - Iniciar sesion \n 2 - Registrarse \n 3 - Salir del chat\n")
        eleccion = input("opcion: ")
        if eleccion == "1":
            jid = input("Username: ")
            jid = jid + '@alumchat.xyz'
            password = input("Password: ")
            xmpp = Client(jid, password)
            if xmpp.connect() == None:
                xmpp.process()
            else:
                print("Error")

        if eleccion == '2':
            #codigo para registrarse
            userJID = input("userJID: ")
            password = input("password: ")

            xmpp = RegisterBot(userJID + "@alumchat.xyz", password)
            xmpp.register_plugin('xep_0066')
            xmpp.register_plugin('xep_0030') 
            xmpp.register_plugin('xep_0004')  
            xmpp.register_plugin('xep_0077') 
            xmpp['xep_0077'].force_registration = True
            xmpp.connect()
            print("usuario creado")
        if eleccion == '3':
            st_log = True
        if eleccion != '1' or eleccion != '2' or eleccion != '3':
            print("Intente de nuevo\n")
