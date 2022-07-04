# -*- coding: utf-8 -*-

import telebot;
import sqlite3;
import time
import datetime
import onlyPrivatModule as pb

#-----Создание БД--------
conn = sqlite3.connect('students.db',check_same_thread=False)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS stud(
   studid INTEGER PRIMARY KEY AUTOINCREMENT,
   name TEXT,
   amountLessons INT,
   duration INT,
   pay INT,
   weekpayT INT,
   monthpayT INT,
   weekpayF INT,
   monthpayF INT,
   timetable TEXT)
""")
conn.commit()
date=datetime.datetime.now()


#------Работа бота-------
bot = telebot.TeleBot('TOKEN');
#Telegram bot token here
dic=[]
#создание нового ученика в базу данных по команте /new, /start и добавление имени, количества уроков, длительности, оплаты в час
#
@bot.message_handler(commands=['create','new'])
def newStudentName(message):
	print(dic)
	msg=bot.send_message(message.chat.id, "Введи имя ученика: ")
	bot.register_next_step_handler(msg, setStudentName)

def setStudentName(message):
	stname = message.text;
	bot.send_message(message.chat.id, "Имя ученика: "+stname);
	msg=bot.send_message(message.chat.id, "Введите количество уроков: ");
	bot.register_next_step_handler(msg, setAmountLessons);
	print("name "+stname)
	dic.append(stname)
	print(type(stname))

def setAmountLessons(message):
	amount=message.text;
	msg=bot.send_message(message.chat.id, "Количество уроков: "+amount);
	askDuration = bot.send_message(message.chat.id, "Введи длительность урока: ")
	bot.register_next_step_handler(msg, setDuration);
	print("amount " + amount)
	dic.append(amount)
	print(type(amount))

def setDuration(message):
	duration=message.text;
	if duration == "1":
		text=" час"
	elif duration == "1,5" or "1.5" or "2":
		text = " часа"
	msg=bot.send_message(message.chat.id, "Длительность уроков: "+duration+text);
	bot.send_message(message.chat.id, "Введи стоимость за час: ")
	print("duration " + duration)
	bot.register_next_step_handler(msg, setPay);
	dic.append(duration)
#Добавление в базу данных
def setPay(message):
	pay=message.text;
	msg=bot.send_message(message.chat.id, "Стоимость в час "+pay);
	print("pay "+pay);
	dic.append(pay)
	print(dic)
	payForWeek=float(dic[1])*float(dic[2])*float(dic[3])
	print(payForWeek)
	print(type(payForWeek))
	dic.append(payForWeek)
	payForMonth=payForWeek*4
	dic.append(payForMonth)
	bot.send_message(message.chat.id, "В неделю стоимость: "+str(payForWeek))
	bot.send_message(message.chat.id, "В месяц стоимость: "+str(payForWeek*4))
	msg=bot.send_message(message.chat.id, "Добавьте дни недели для занятий в формате:пн, пт, вт, ср, чт...несколько дней отделяются запятыми")
	bot.register_next_step_handler(msg,setTimetable)
#добавления словаря dic в БД
def addStudtodb():
	cur.execute("""INSERT INTO stud (name, amountLessons, duration, pay, weekpayT, monthpayT, timetable) VALUES(?,?,?,?,?,?,?)""", dic);
	conn.commit();
	print(dic)
#очистка словаря с данными после добавления в БД
	print(dic)
	print(type(dic))
	for i in dic[:]:
	     dic.remove(i)

#добавить дни занятий для ученика
def setTimetable(message):
	daysstr=message.text
	dayslist=daysstr.split(",")
	print(dayslist)
	dic.append(daysstr)
	print(dic)
	addStudtodb()

#выбор ученика по имени и выдача всех данных о нем
@bot.message_handler(commands=['select'])
def selectstud(message):
	msg=bot.send_message(message.chat.id, "Введите имя ученика, чтобы получить данные об уроках")
	bot.register_next_step_handler(msg,selectDB)

def selectDB(message):
	studName=message.text
	cur.execute("SELECT * FROM stud WHERE name = '"+studName+"'")
	data=cur.fetchall()
	print(data)
	if data==[]:
		bot.send_message(message.chat.id, "Нету такого ученика. Добавьте или введите имя корректно")
	else: pass
	for row in data:

		print(row)
		print(type(row))
		msgText=f"""Имя ученика: {row[1]}
		Количество занятий:{row[2]}
		Длительность занятий:{row[3]}
		Ставка в час:{row[4]}
		Стоимость занятия:{int(row[3]*int(row[4]))}
		Стоимость в неделю:{row[5]}
		Стоимость в месяц:{row[6]}
		Дни занятий:{row[9]}"""
		print(msgText)
		bot.send_message(message.chat.id, msgText)




#выписка из банка
@bot.message_handler(commands=['trans'])
#запрос даты с которой скачивать транзакции
###добавить запрос даты которой заканчивать транзакции
#Добавить сортировку по датам
#исправить порядок сообщений по датам
def askfordate(message):
	msg=bot.send_message(message.chat.id, "Введите дату с которой скачать транзакции в формате дд.мм.гггг:" )
	bot.register_next_step_handler(msg,setdate)
def getTransactions(message):
	msg=bot.send_message(message.chat.id, "Введите дату с которой скачать транзакции в формате дд.мм.гггг:" )
	bot.register_next_step_handler(msg,setdate)
def setdate(message):
	datestr=message.text
		#datestr.split(',')
	print(datestr)
	date=datetime.datetime.strptime(datestr, "%d.%m.%Y").strftime('%s')
	print(date)
	print(type(date))
	date = int(date)
	print(date)
	bot.send_message(message.chat.id, "Скачиваю с даты: "+datestr)
	st=pb.connectPrivat()
	pb.editPrivat(st)
	print("connected to privat")
	pb.connectMonobank()

	print(date)
	transDB = sqlite3.connect("transactions2.db")
	cursor=transDB.cursor()
	cursor.execute("SELECT * FROM transactions WHERE transtime >"+str(date)+" AND operationAmount < 0 ORDER BY transtime ASC")
	rows = cursor.fetchall()
	bot.send_message(message.chat.id, "Расходы:")
	moneysum=0
	for row in rows:
		print(row)
		moneysum=moneysum+row[7]
		bot.send_message(message.chat.id, f"""Транзакция с карты: {row[1]}
		Дата: {datetime.datetime.utcfromtimestamp(row[3]).strftime("%d.%m.%Y")}
		Описание: {row[4]}
		Сумма: {str(row[7])} {row[8]}
		Баланс: {row[11]}""")
	bot.send_message(message.chat.id,"Расходы в сумме: "+str(moneysum))
	cursor.execute("SELECT * FROM transactions WHERE transtime >"+str(date)+" AND operationAmount > 0 ORDER BY transtime ASC" )
	rows = cursor.fetchall()
	bot.send_message(message.chat.id, "Доходы:")
	moneysum=0
	for row in rows:
		if row[8]==980 or row[8]=="UAH" or row[8]=="980":
			currency="UAH"
		else:
			currency=row[8]
		bot.send_message(message.chat.id, f"""Транзакция с карты: {row[1]}
		Дата: {datetime.datetime.utcfromtimestamp(row[3]).strftime("%d.%m.%Y")}
		Описание: {row[4]}
		Сумма: {str(row[7])} {currency}
		Баланс: {row[11]}""")
		moneysum=moneysum+row[7]
	bot.send_message(message.chat.id,"Доходы в сумме: +"+str(moneysum))
	transDB.close()
#график по дням недели

@bot.message_handler(commands=['check'])

#Проверка оплат от учеников
def checkForPay(message):
	transDB = sqlite3.connect("transactions2.db")
	cursor=transDB.cursor()
	cursor.execute("SELECT * FROM transactions WHERE cardNumber = 'monobankcard5555' ORDER BY transtime ASC")
	Mrows=cursor.fetchall()
	print(Mrows)
	for row in Mrows:
		date=str(datetime.datetime.utcfromtimestamp(row[3]).strftime("%d.%m.%Y"))

		if "Від:" in row[4]:
			print(row)
			transFromWho=row[4].replace("Від: ", "")
			print(transFromWho)
			bot.send_message(message.chat.id, "Транзакция на карту МОНОБАНК в сумме "+str(row[6])+" UAH от "+transFromWho+" "+date)
	cursor.execute("SELECT * FROM transactions WHERE cardNumber = '5363542012827151' ORDER BY transtime ASC")
	#privat search
	Prows=cursor.fetchall()
	for row in Prows:
		print(row)
		date=str(datetime.datetime.utcfromtimestamp(row[3]).strftime("%d.%m.%Y"))
		if "Перевод с карты ПриватБанка через приложение Приват24. Отправитель:"  in row[4] and "Перевод на свою «Копилку»" not in row[4]:
			print(row)
			bot.send_message(message.chat.id, f"Транзакция на карту {str(row[1])} Приват24  в сумме "+str(row[6])+". От  "+row[4].replace("Перевод с карты ПриватБанка через приложение Приват24. Отправитель:"," ")+" Дата: "+date)
		elif "Зачисление перевода на карту" in row[4] and "Перевод на свою «Копилку»" not in row[4]:
			print(row)
			if row[7]==1000.0:
				bot.send_message(message.chat.id, f"Транзакция на карту {str(row[1])}. Сумма: 1000 UAH от ЗНО Вадим. "+date)
			elif "TRANSFERWISE" in row[4]:
			 	bot.send_message(message.chat.id, f"Транзакция на карту {str(row[1])}. Сумма: {row[6]} от Анастасия "+date)
			else:
				bot.send_message(message.chat.id, f"Транзакция на карту {str(row[1])} Приват24  в сумме "+str(row[6])+". "+row[4].replace("Зачисление перевода на карту", " ")+date)
				bot.send_message(message.chat.id, "Не удалось определить от кого. "+date)
				#добавить реплай маркап с обозначением от кого транзакция










	#задачи: создать ученика, создать количество уроков, создать длительность урока, сумму к оплате, статус оплаты







bot.polling(none_stop=True, interval=0);
