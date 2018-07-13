from nvd3 import pieChart
from nvd3 import discreteBarChart
import requests 

def top_pages_op(top_pages_list):
	print "top pagess"
	xdata = []
	ydata = []
	for i in range(0,len(top_pages_list)):
	 	xdata.append(top_pages_list[i]['key'])
	 	ydata.append(top_pages_list[i]['doc_count'])
   	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topPagesBar.html', 'w')
   	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topPagesPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600) 
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()

def top_users_op(top_users_list):
	print "top users"
	xdata = []
	ydata = []
	for i in range(0,len(top_users_list)):
	 	xdata.append(str(top_users_list[i]['key']))
	 	ydata.append(top_users_list[i]['doc_count'])
	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topUsersBar.html', 'w')
	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topUsersPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600) 
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()

def top_downloads_op(top_downloads_list):
	xdata = []
	ydata = []
	for i in range(0,len(top_downloads_list)):
	 	xdata.append(top_downloads_list[i]['key'])
	 	ydata.append(top_downloads_list[i]['doc_count'])
   	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topDownloadsBar.html', 'w')
   	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topDownloadsPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600) 
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()

def top_resources_op(top_resources_list):
	xdata = []
	ydata = []
	for i in range(0,len(top_resources_list)):
	 	xdata.append(top_resources_list[i]['key'])
	 	ydata.append(top_resources_list[i]['doc_count'])
   	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topResourcesBar.html', 'w')
   	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topResourcesPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600) 
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()


def top_videos_op(top_videos_list):
	xdata = []
	ydata = []
	for i in range(0,len(top_videos_list)):
	 	xdata.append(top_videos_list[i]['key'])
	 	ydata.append(top_videos_list[i]['doc_count'])
   	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topVideosBar.html', 'w')
   	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topVideosPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600) 
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()


def top_audios_op(top_audios_list):
	xdata = []
	ydata = []
	for i in range(0,len(top_audios_list)):
	 	xdata.append(top_audios_list[i]['key'])
	 	ydata.append(top_audios_list[i]['doc_count'])
   	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topAudiosBar.html', 'w')
   	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topAudiosPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600) 
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()

def top_images_op(top_images_list):
	xdata= []
	ydata = []
	for i in range(0,len(top_images_list)):
	 	xdata.append(top_images_list[i]['key'])
	 	ydata.append(top_images_list[i]['doc_count'])
   	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topImagesBar.html', 'w')
   	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topImagesPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600) 
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()


def top_pages_lastWeekop(top_list):
	xdata = []
	ydata = []
	for key, value in top_list.items():
			xdata.append(key)
			ydata.append(value)
    	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topPagesLastWeekBar.html', 'w')
	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topPagesLastWeekPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600) 
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()

def top_pages_lastMonthop(top_list):
	xdata = []
	ydata = []
	for key, value in top_list.items():
			xdata.append(key)
			ydata.append(value)
    	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topPagesLastMonthBar.html', 'w')
	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topPagesLastMonthPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600) 
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45	
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()

def top_pages_lastYearop(top_list):
	xdata = []
	ydata = []
	for key, value in top_list.items():
			xdata.append(key)
			ydata.append(value)
    	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topPagesLastYearBar.html', 'w')
	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topPagesLastYearPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600) 
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()

def top_users_lastWeekop(top_list):
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topUsersLastWeekBar.html', 'w')
	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topUsersLastWeekPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600) 
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()

def top_users_lastMonthop(top_list):
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topUsersLastMonthBar.html', 'w')
	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topUsersLastMonthPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600) 
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()

def top_users_lastYearop(top_list):
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topUsersLastYearBar.html', 'w')
	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topUsersLastYearPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600)
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45 
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()

def top_downloads_lastWeekop(top_list):
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topDownloadsLastWeekBar.html', 'w')
	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topDownloadsLastWeekPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600) 
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()

def top_downloads_lastMonthop(top_list):
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topDownloadsLastMonthBar.html', 'w')
	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topDownloadsLastMonthPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600) 
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()

def top_downloads_lastYearop(top_list):
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topDownloadsLastYearBar.html', 'w')
	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topDownloadsLastYearPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600) 
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()

def top_resources_lastWeekop(top_list):
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topResourcesLastWeekBar.html', 'w')
	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topResourcesLastWeekPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600) 
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()

def top_resources_lastMonthop(top_list):
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topResourcesLastMonthBar.html', 'w')
	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topResourcesLastMonthPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600) 
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45	
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()

def top_resources_lastYearop(top_list):
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topResourcesLastYearBar.html', 'w')
	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topResourcesLastYearPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600) 
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45	
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()

def top_videos_lastWeekop(top_list):
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topVideosLastWeekBar.html', 'w')
	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topVideosLastWeekPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600) 
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()

def top_videos_lastMonthop(top_list):
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topVideosLastMonthBar.html', 'w')
	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topVideosLastMonthPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600) 
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()

def top_videos_lastYearop(top_list):
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topVideosLastYearBar.html', 'w')
	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topVideosLastYearPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600) 
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()

def top_audios_lastWeekop(top_list):
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topAudiosLastWeekBar.html', 'w')
	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topAudiosLastWeekPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600) 
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()

def top_audios_lastMonthop(top_list):
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topAudiosLastMonthBar.html', 'w')
	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topAudiosLastMonthPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600) 
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()

def top_audios_lastYearop(top_list):
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topAudiosLastYearBar.html', 'w')
	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topAudiosLastYearPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600) 
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()

def top_images_lastWeekop(top_list):
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topImagesLastWeekBar.html', 'w')
	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topImagesLastWeekPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600) 
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()

def top_images_lastMonthop(top_list):
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topImagesLastMonthBar.html', 'w')
	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topImagesLastMonthPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600) 
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()

def top_images_lastYearop(top_list):
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file1 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topImagesLastYearBar.html', 'w')
	output_file2 = open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/templates/ndf/topImagesLastYearPie.html', 'w')
	chart1 = discreteBarChart(name='discreteBarChart', height=600, width=600)
	chart2 = pieChart(name='pieChart', color_category='category20c', height=600, width=600) 
	chart1.margin_bottom = 300
	chart1.axislist['xAxis']['rotateLabels'] = +45
	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart1.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart2.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart1.buildhtml()
	chart2.buildhtml()
	output_file1.write(chart1.htmlcontent)
	output_file2.write(chart2.htmlcontent)
	output_file1.close()
	output_file2.close()
