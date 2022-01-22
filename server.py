import socket
import sys
import time
import select
import random
from que import question_list, opt_list, ans_list


all_connections = []
all_address = {}
all_names = {}
scores = {}
winner = 0


# To randomize the lists
c = list(zip(question_list, opt_list, ans_list))
random.shuffle(c)
question_list, opt_list, ans_list = zip(*c)


# Create a Socket ( connect two computers)
def create_socket():
    try:
        global host
        global port
        global s
        host = ""
        port = 9999
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    except socket.error as msg:
        print("Socket creation error: " + str(msg))



# Binding the socket and listening for connections
def bind_socket():
    try:
        global host
        global port
        global s
        print("\tBinding the Port: " + str(port))

        s.bind((host, port))
        s.listen(5)

    except socket.error as msg:
        print("Socket Binding error" + str(msg) + "\n" + "Retrying...")
        bind_socket()



# Handling connection from multiple clients and saving to a list
def accepting_connections():

    #giving just 10 seconds to the clients to establish the connection
    #settimeout will turn off the socket after 10 seconds
    print("\t10 SECONDS FOR THE PARTICIPANTS TO JOIN\n")
    s.settimeout(12)

    while 1:
        try:
            conn, address = s.accept()

            all_connections.append(conn)
            all_address[conn] = address

            print("\t" + address[0] + " joined the game!")

        except socket.timeout as e:
            print('\n\tNO CONNECTIONS AFTER 10 SECONDS...')
            s.close()
            break


    #if there are less than 2 participants
    if(len(all_connections) <= 1):
        print(f"\tNeed at least 2 participants, {len(all_connections)} joined")
        sys.exit();


    print("\n");



    #if they send nothing then the error will occur which we will pass
    for i, conn in enumerate(all_connections):
        el = "Player"+str(i+1)

        conn.send(el.encode("utf-8"))
        all_names[conn] = el
        print("\tPlayer id set for " + all_address[conn][0] + " as "+el)


    #if all names are given for the connections start the game
    print("\tAll ids given to the players, lets start the game in 5 seconds\n")


    #This is to ensure that game starts at the same time for everyone.
    #When this y will reach the other side, it will signal to start game
    time.sleep(5)
    for i in all_connections:
        i.send("y".encode("utf-8"))
        scores[i] = 0




# FUNCTION TO CLEAR THE SOCKET
def empty_socket(sock):

    i, o, e = select.select([sock],[],[], 1)
    if (i):
        ans = sock.recv(2048)
        # print("\ti ate up ", ans)




#function to tell if the buzzer is pressed and who pressed the buzzer first
def buzzer(time):
    for conn in all_connections:
        conn.setblocking(0)

    i, o, e = select.select(all_connections, [], [], time+2)

    if(i):
        kachraa = i[0].recv(2048).decode("utf-8")
        print("\tbuzzer : ", kachraa)
        i[0].send("Yes".encode("utf-8"))

        for conn in all_connections:
            if(conn != i[0]):
                conn.send(f"No{all_names[i[0]]}".encode("utf-8"))

        return [True, i[0]]

    else:
        return [False, 1]




# IT ACCEPTS THE ANSWER AND GIVES THE SCORE TO THE BUZZER PRESSER 
def eval_question(presser, qno, time):
    i, o, e = select.select([presser], [], [], time)

    if(i):
        ans = presser.recv(2048).decode("utf-8")
        print("\t--> Ans given : ", ans, "\n\n")

        if ans[0] == ans_list[qno][0]:
            scores[presser] += 1
            presser.send("You answered it right, You earn 1 point".encode("utf-8"))
        else:
            scores[presser] -= 0.5
            presser.send("You answered it wrong, You lose 0.5 points".encode("utf-8"))
    else:
        scores[presser] -= 0.5
        presser.send("You failed to answer it in time, You lose 0.5 points".encode("utf-8"))



# THIS FUNCTION SIGNALS THE END OF THE QUESTION TIME TO EVERY CLIENT
def moveon(sig, scorecard):
    mess = "mv"
    if(sig == 0):
        mess = "end"
    for i in all_connections:
        i.send((mess+str(scores[i]) + "\n\n" + "\tSCORECARD : \n\n" + scorecard).encode("utf-8"))



########################################
# THE MAIN PROGRAM STARTS FROM HERE ON #
########################################


create_socket()
bind_socket()
accepting_connections()



for qno in range(len(question_list)):
    # Print the question
    print(f"\tQUES {qno+1} :-")
    print(f"\n\t-----> {question_list[qno]}\n\t{opt_list[qno]}")


    #sending question to everyone
    for j in all_connections:
        j.send(f"QUES {qno+1} :-\n-----> {question_list[qno]}\n\t{opt_list[qno]}".encode("utf-8"))
    time.sleep(2)


    # It will contain whether the buzzer is pressed and who pressed it
    press = buzzer(10)


    if(press[0]):
        eval_question(press[1], qno, 10)
        print(f"\t{all_names[press[1]]} PRESSED THE BUZZER FIRST\n")
    else:
        print("\tBUZZER NOT PRESSED IN TIME, time to move to the next question\n")
        for conn in all_connections:
            conn.send("wastesig".encode("utf-8"))

    time.sleep(5)



    print("\tAfter completion of question :-\n")
    time.sleep(2)


    scorecard = ""
    scorecard += "\t{0:20} {1:20} {2}\n".format("ADDRESS", "NAME", "SCORE")
    for conn in all_connections:
        scorecard += "\t{0:20} {1:20} {2}\n".format(all_address[conn][0], all_names[conn], scores[conn])
    scorecard += "\n\n"

    print(scorecard);
    # print("\t{0:20} {1:20} {2}".format("ADDRESS", "NAME", "SCORE"))
    # for conn in all_connections:
    #     print("\t{0:20} {1:20} {2}".format(all_address[conn][0], all_names[conn], scores[conn]))
    # print("\n\n")


    for conn in all_connections:
        if(scores[conn] >= 5):
            winner = conn
    time.sleep(4)



    if(qno == len(question_list)-1 or winner):
        moveon(0, scorecard)      
        for conn in all_connections:
            if conn == press[1]:
                continue
            empty_socket(conn)
        break
    else:
        moveon(1, scorecard)
        for conn in all_connections:
            if conn == press[1]:
                continue
            empty_socket(conn)

    time.sleep(1)



for conn in all_connections:
    if(conn == winner):
        conn.send(f"Congrats! You won the game. Your score is {scores[conn]}".encode("utf-8"))
    else:
        if(winner):
            conn.send(f"You lost the game. Your score is {scores[conn]}".encode('utf-8'))
        else:
            conn.send(f"The game is tied. Your score is {scores[conn]}".encode('utf-8'))


time.sleep(10)
s.close()
for i in all_connections:
    i.close()
















