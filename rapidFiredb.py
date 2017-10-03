import csv
import MySQLdb as sql

flag=0
count =0
# round1 = {}
db  = sql.connect('139.59.17.132','user2','passw','civicq')
c = db.cursor()

query = " INSERT INTO rapidFire VALUES "
with open('RapidFire.csv') as file:
	readr = csv.reader(file)
	for r in readr:
		# print r
		if(r[0] == "ROUND 6"):
			flag =1
			continue;
		if(flag==1):
			count +=1
			# print r
			# r[0] == ques_id			
			# r[1] == ques in quotes		
			# r[2] == ques_img 		
			# r[3] == ans
			# r[4] == money_per
			# r[5] == flag
			# if(r[10] ==''):
				# r[10] = 'null'
			val = "('" +r[0] + "','" + r[1] +"','" + r[2] +"','" + r[3] +"','"+ r[5] +"','"+ r[6] + "')"
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
		if(count == 12):
			flag=0
# disconnect from server
db.close()