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
setting_name="../../gnowsys-ndf/gnowsys_ndf/settings.py"
temp_name="../../gnowsys-ndf/gnowsys_ndf/temp.py"
print("Thank You. Configuring your settings now...")
with open(temp_name,"a") as outfile:
	with open(setting_name,"r") as infile:
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
os.remove(setting_name)
os.rename(temp_name,setting_name)
			
