#!/usr/bin/env python

import web
import os
from time import time, sleep, strftime, localtime
from getpass import getpass
from web import form
from radius import RADIUS
from settings import *
from string import letters

import hashlib
import base64

#if not radiusIp: radiusIp = raw_input("Insert Radius server address: ")
#if not radiusSecret: radiusSecret = getpass("Insert Radius server password: ")

lastrequest = 0
lastexecutions = {}
validChars = letters+" "
logFd = open(logfile, "a")

salt = "c5d22d1f16b8"

def log(text):
    logFd.write(strftime("%d/%m/%Y %H:%M:%S", localtime()) + " - " + text + "\n")
    logFd.flush()

def authenticate_from_file(uname, passwd):
    f = open('users.txt', 'r')
    for l in f:
        t = l.split(' ')
        sha = hashlib.sha1()
        sha.update(passwd)
        sha.update(salt)
        if uname == t[0] and sha.digest() == base64.b64decode(t[1]):
            return True
    return False

def authenticate(uname, passwd):
    global lastrequest

    if (time()-lastrequest)<2: sleep(2) # To prevent bruteforce on radius

    r = RADIUS(radiusSecret, radiusIp, radiusPort)
    r.timeout = 10

    lastrequest = time() # Save time of request (to prevent bruteforce)

    if r.authenticate(uname, passwd):
        return True
    else:
		return authenticate_from_file(uname, passwd)

def avviso(nome, porta):
    lingua = "it"
    nome = nome.replace(".", " ")
    for l in nome:
        if not (l in validChars):
            log("Warning: OS command injection in name")
            return

    testo = "E' in attesa alla porta " + nome + ". Andate ad aprire la porta "+ annunciPorte[porta]
    testo = testo.replace(" ","+")
    os.system("mplayer -http-header-fields 'User-Agent: Mozilla' \"http://translate.google.com/translate_tts?ie=UTF-8&tl="+lingua+"&q="+testo+"\" > /dev/null 2> /dev/null &")


urls = (
    '/(.*)', 'RingPage'
)

app = web.application(urls, globals())

render = web.template.render('templates/')

login_form = form.Form(
    form.Textbox("username", description = "Username"),
    form.Password("password", description = "Password"),
    form.Dropdown("porta", args = porte , value = porte[0],
                  description = "Porta da aprire"),
    form.Button("Suona il campanello", type = "submit",
                  description = "Enter"),
    validators = []
)

class RingPage:
    def GET(self,*args):
        f = login_form()
        return render.login(f, None, None)

    def POST(self, *args):
        f = login_form()
        username = str(web.input()["username"])
        password = str(web.input()["password"])
        porta = porte.index(str(web.input()["porta"]))

        if authenticate(username, password) and (not username in banlist):
            log("Richiesta esecuzione da %s" %(username))
            if not (username in lastexecutions) or (time()-lastexecutions[username]) > 20:
                lastexecutions[username] = time()
                log("Avviso lanciato per porta numero " + str(porta))
                avviso(username, porta)
                return render.login(login_form(), "success", "Login effettuato, campanello suonato")

            else:
                log("Richiesta annullata: too fast")
                return render.login(login_form(), "error", "Too fast: attendi 20 secondi prima di rieseguire")

        else:
            log("Autorizzazione negata per %s" %(username))
            return render.login(login_form(), "error", "Autorizzazione negata")

if __name__ == "__main__":
    app.run()

