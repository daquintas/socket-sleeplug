import socket
import sys
import serial, time
import threading
import sqlite3

arduino = serial.Serial('/dev/ttyACM0', baudrate=9600, bytesize=8, parity='N', stopbits=1)

new_socket = True

def main():

	HOST = '192.168.43.137' #this is your localhost
	PORT = 8888

	new_socket = True

	print("conectando a la base de datos...")
	db_conector = sqlite3.connect('sleeplug.db')
	db_cursor = db_conector.cursor()

	while (new_socket):
		new_socket = False;

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#socket.socket: must use to create a socket.
		#socket.AF_INET: Address Format, Internet = IP Addresses.
		#socket.SOCK_STREAM: two-way, connection-based byte streams.
		print 'socket created'

		#Bind socket to Host and Port
		try:
			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			s.bind((HOST, PORT))
		except socket.error as err:
		    print 'Bind Failed, Error Code: ' + str(err[0]) + ', Message: ' + err[1]
		    sys.exit()

		print 'Socket Bind Success!'


		#listen(): This method sets up and start TCP listener.
		s.listen(10)
		print 'Socket is now listening'

		while 1:
			try:
				conn, addr = s.accept()
				print 'Connect with ' + addr[0] + ':' + str(addr[1])
				print('Estado del puerto: %s' % (arduino.isOpen()))
				arduino.setDTR(False)
				time.sleep(1)
				arduino.flushInput()
				arduino.setDTR(True)
				txt = ''
				print("Starting...")
				arduino.write('3')
				time.sleep(1)


				while True:
					buf = conn.recv(64)
					buf = buf.rstrip("\n\r")
					if buf =='1':
						print(buf)
						print 'entra uno'
						arduino.write(buf)
						time.sleep(0.1)
						while arduino.inWaiting() > 0:
							txt += arduino.read(1)
						print(txt)
						txt=''

						hora_tag = time.strftime("%c")
						comando_hora = [(1, hora_tag)]
						db_cursor.executemany("INSERT INTO cuna(comando, hora) VALUES(?, ?)", comando_hora)
						db_conector.commit()
					if buf == '0':
						print 'entra cero'
						print(buf)
						arduino.write(buf)
						time.sleep(0.1)
						while arduino.inWaiting() > 0:
							txt += arduino.read(1)
						print(txt)
						txt=''

						hora_tag = time.strftime("%c")
						comando_hora = [(0, hora_tag)]
						db_cursor.executemany("INSERT INTO cuna(comando, hora) VALUES(?, ?)", comando_hora)
						db_conector.commit()

					if buf == '' or buf == ' ':
						new_socket = True;
						s.close()
						break
				if(new_socket == True):
					break

			except socket.timeout as err:
				print ("EXCEPCION")
				print err
				conn, addr = s.accept()

		s.close()

	arduino.close()
	print('Estado del puerto: %s' % (arduino.isOpen()))

class MyThread(threading.Thread):
	def run(self):
		while True:
			db_conector = sqlite3.connect('sleeplug.db')
			db_cursor = db_conector.cursor()
			txt=''

			while arduino.inWaiting() > 0:
				txt += arduino.read(1)

			if txt == '2':
					hora_tag = time.strftime("%c")
					comando_hora = [(2, hora_tag)]
					db_cursor.executemany("INSERT INTO cuna(comando, hora) VALUES(?, ?)", comando_hora)
					db_conector.commit()
			if txt == '3':
					hora_tag = time.strftime("%c")
					comando_hora = [(3, hora_tag)]
					db_cursor.executemany("INSERT INTO cuna(comando, hora) VALUES(?, ?)", comando_hora)
					db_conector.commit()

if __name__ == '__main__':
	main()
