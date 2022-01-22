import socket
import time
import sys, select
import os
from termios import tcflush, TCIFLUSH


#Takes input for a certain time
def timedinput(arg, time):
	tcflush(sys.stdin, TCIFLUSH)
	print (arg)
	i, o, e = select.select( [sys.stdin], [], [], time)

	if (i):
	  return sys.stdin.readline().strip()
	else:
	  return False;


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = ''
port = 9999


s.connect((host, port))

print("\t\t\t\t##############################")
print("\t\t\t\t#                            #")
print("\t\t\t\t#  WELCOME TO THE MEGA QUIZ  #")
print("\t\t\t\t#                            #")
print("\t\t\t\t##############################\n\n")
time.sleep(1)

print("\tWait for the players to join....\n\n")



while True:
	response = s.recv(2048).decode("utf-8")
	print("\t" + "Your player id is : " + response)
	if(len(response)):
		break



# INDICATION THAT PLAYERS HAVE JOINED THE GAME
while True:
	start = s.recv(2048).decode("utf-8")
	if(start[0] == 'y'):
		print("\n\t\t\t\t-------------------------\n")
		print("\t\t\t\t-----GAME STARTS NOW-----\n")
		print("\t\t\t\t-------------------------\n")
		break




# Recieving questions
while True:
	i, o, e = select.select([s], [], [], 50)
	if(i):
		question = s.recv(2048).decode("utf-8")
		print("\t" + question)
		time.sleep(2)
	#Question recieved and printed
	

	#Taking buzzer input
	p = timedinput("\n\tType anything for the buzzer, 10 seconds for the buzzer : ", 10)
	# print("p : ", p)

	# You sent the buzzer
	if(p != False):

		if(p == ""):
			p = "enter"

		s.send(p.encode('utf-8'))

		i, o, e = select.select([s], [], [], 1)

		if(i):
			q = s.recv(2048).decode("utf-8")
			# print("q : ", q)

			# You were on time
			if(q[0] == "Y"):
				print("\tYou pressed the buzzer first")

	
				ans = timedinput("\tType the answer option in 10 seconds :", 10)
				# print("ans : ", ans)
				if(ans != False):
					if(ans == ""):
						ans = "enter"
					ans = ans.lower()
					s.send(ans.encode("utf-8"))

				i, o, e = select.select([s], [], [], 10)
				if(i):
					anjaam = s.recv(2048).decode("utf-8")
					print("\t" + anjaam )
				else:
					print("\tsome error occured!")
			else:
				print(f"\tSomeone already pressed the buzzer\n")
		else:
			print("wait for the next question...\n")
			waste = s.recv(2048)

	else:
		print("\tYou did not press the buzzer so wait for the next question".upper())
		waste = s.recv(2048).decode("utf-8")
		# print("waste : "+ waste)

	print("\n\n-------------------------------------------------------------------------------------------------------------------------------------------")
	print('\n\n')
	


	i, o, e = select.select([s], [], [], 50)
	if(i):
		r = s.recv(2048).decode("utf-8").strip()
		# print("r : ", r)
		if(r[:2] == "mv"):
			print(f"\n\tYOUR CURRENT SCORE IS {r[2:]}\n")
			time.sleep(6)
			os.system('clear')
			continue;
		else:
			print(f"\n\tYOUR CURRENT SCORE IS {r[3:]}\n")
			print("\n\tGAME ENDED\n")
			break;
	else:
		print("\tsome error occured")




i, o, e = select.select([s], [], [], 20)
if(i):
	result = s.recv(2048).decode("utf-8")
	print(f"\n\t{result}\n".upper())
	


time.sleep(3)
print("\n\tTHANKS FOR PLAYING")

s.close()





























