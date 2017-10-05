import csv
import MySQLdb as sql

flag=0
count =0
# round1 = {}
db  = sql.connect('139.59.17.132','user2','passw','civicq')
c = db.cursor()

query = " INSERT INTO questions VALUES "
with open('AllRounds.csv') as file:
	readr = csv.reader(file)
	for r in readr:
		if(r[0] == "ROUND6"):
			flag =1
			continue;
		if(flag==1):
			count +=1
			# r[1] == ques_id			# r[2] == ques in quotes			# r[3] == ques_img 			# r[4] == op1			# r[5] ==op2			# r[6] == op3			# r[7] == op4			# r[8] == ans			# r[9] == pt_wt			# r[10] == money_wt			# r[11] == flag
			if(r[10] ==''):
				r[10] = 'null'
			val = "('" + r[1] +"','" + r[2] +"','" + r[3] +"','"+ r[4] +"','"+ r[5] +"','"+ r[6] +"','"+ r[7] +"','"+ r[8] +"','"+ r[11] +"','"+ r[9] +"','"+ r[10] +"')"
			# print(val)
			try:
				print(c.execute(query + val + ";"))
				# print(query + val + ";")
				# c.execute(sql)
				# Commit your changes in the database
				db.commit()

			except Exception as e:
				# Rollback in case there is any error
				print(e)
				db.rollback()
				pass
		if(count == 25):
			flag=0
# disconnect from server
db.close()