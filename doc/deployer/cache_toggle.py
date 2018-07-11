import os
invalid=0
choice=-1
try:
	choice=int(input("Would you like to turn cache on (1) or off (0) ? "))
except:
	invalid=1

while((choice!=0 and choice!=1) or invalid==1):
	try:
		choice=int(input("Please enter a valid value "))
		invalid=0
	except:
		invalid=1

print("Thank You. Configuring your settings now...")
with open("temp.py","a") as outfile:
	with open("settings.py","r") as infile:
		for line in infile:
			if('MAX_ENTRIES' in line):
				print(line)
				temp=line
				index=temp.find(':')
				if(choice==0):
					temp=temp[:index+1]
					temp+='0\n'
				elif(choice==1):
					temp=temp[:index+1]
					temp+='1000000\n'
				print(temp)
				outfile.write(temp)
			else:
				outfile.write(line)
os.remove("settings.py")
os.rename("temp.py","settings.py")
			
