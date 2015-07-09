1)Creating temporary variables for faster lookup:
	Lists are very commonly used data structure for storing mutating information in python. While using lists we frequently use append methods on them. This append function when combined with loops is a costly operation but with a fairly simple hack the time can be reduced.
def func1():
	lst1=[]
	lst2=[]
	for i in range(500):
		lst1.append(i)
		lst2.append(i+500)
	for j in lst2:
		lst1.append(j)

def func2():
	lst1=[]
	lst2=[]
	l1_append_temp=lst1.append #a tempoary variable
	l2_append_temp=lst2.append #lookup for append already done
	for i in range(500):
		l1_append_temp(i)
		l2_append_temp(i+500)
	for j in lst2:
		l1_append_temp(j)

Using timeit library of python we timed the functions got the following results:
	func1-0.048635005950927734
	func2-0.032353162765502930
(Note that here we are dealing with relatively small data so the time difference may be small but with big data the difference can be huge)

Here for each loop we look for the append function of the list and then use the function but by using the temporary variable (where we store the lookup early on) we skip the first step. 

We can use the same technique for commonly used queries on databases present within loops.
Eg- dB_find_temp=node_collection.find
    	
(Note that using this when there are no loops present gives no time advantage.Infact using this without loops can lead to loss of readability and also the problem of many local variables being present)

2)Multiprocessing library of python:
	Because of GIL (Global Interpreter Lock) working with threads in python is not very easy as was the case with old languages like C.
GIL of python interpreter synchronizes the execution of threads so that only one thread can execute at a time even if the computer has multiple cores and can run threads simultaneously. Still, using multiprocessing library allows the programmer some leeway where he can use the multiple cores to some extent.(But note that using this library creates a big software overhead and thus must be used only when dealing with big loops).In python also the old rule that 'multiprocessing must be used only when dealing with independent objects' applies.

def func3():
	for each_gapp in already_selected_gapps:
            gapp_name = each_gapp["name"]
            if gapp_name in gapps_list:
                gapps_list_remove(gapp_name)

import multiprocessing
def func4():
	processes=[]
        n1=len(already_selected_gapps)
        lst1=already_selected_gapps
        x=mp.cpu_count()
        n2=n1/x
        for i in x:#dividing the list (of independent elements) by number of cores and passing each partition to one thread 
          processes.append(mp.Process(target=multi_,args=(lst1[i*n2:(i+1)*n2])))
        for i in x:
          processes[i].start()
        for i in x:
          processes[i].join()

def multi_(lst):#the logic of the loop must be put in a function so that each thread can use it
              for each_gapp in lst:
                gapp_name = each_gapp["name"]

                if gapp_name in gapps_list:
                    gapps_list_remove(gapp_name)


3)List comprehensions:
	The best way to visualize list comprehensions is thinking of them as sets in set-builder form. This is an excellent alternative to loops dealing with lists as it results in faster computations.

	A={x^2:x is in (1,2,3)}={1,4,9}

def func5():
	lst=[]
	lst2=[]
	for i in range(500):
		lst2.append(i)
	for i in lst2:
		lst.append(i*i)

def func6():
	lst2=[]
	lst2_append_temp=lst2.append
	for i in range(500):
		lst2_append_temp(i)
	lst=[i*i for i in lst2] #see the similarity with set builder form

Using timeit library of python we timed the functions got the following results:
	func5-0.047894954681396484
	func6-0.021952867507934570
(Note that here we are dealing with relatively small data so the time difference may be small but with big data the difference can be huge)

The general format of list comprehension is:
	[expression for item in old_list if condition]

This  is equivalent to:
	for item in old_list:
		if condition:
			expression

Eg-
	new_lst = [x**2 for x in old_lst if x%2==0]
is equivalent to
	new_lst=[]
	for x in old_lst:
		if x%2==0:
			new_lst.append(x**2)
Note that here old_lst must be different from new_lst and also that new_lst must be empty (if not new_lst will be replaced)
