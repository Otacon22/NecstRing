#!/usr/bin/python2

import base64
import sys
import hashlib

def add_user(user, password):
	sha = hashlib.sha1()
	sha.update(password)
	sha.update("c5d22d1f16b8")

	with open("users.txt", "a") as users:
		users.write(user + " " + base64.b64encode(sha.digest()) + '\n')

def del_user(user):
	f = open("users.txt", "r")
	dump = f.readlines()
	f.close()

	f = open("users.txt", "w")
	for line in dump:
			if line.split(' ')[0] != user:
					f.write(line)
	f.close()

if sys.argv[1] == 'add':
	add_user(sys.argv[2], sys.argv[3])
elif sys.argv[1] == 'del':
	del_user(sys.argv[2])
else:
	print sys.argv[0] + " {add, del} username [password]"

