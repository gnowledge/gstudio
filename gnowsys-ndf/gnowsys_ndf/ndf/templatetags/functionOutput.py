from es_tags import *
from nvd3 import pieChart
from nvd3 import discreteBarChart
from bs4 import BeautifulSoup
import requests

def get_download_name(download_url):
	#gets the download name from the download url
	last_slash = download_url.rfind('/')
	last_colon = download_url.rfind('.')
	download = download_url[last_slash+1:last_colon]
	return download

def get_resource_name(resource_url):
    #gets the resource name from the resource url
	last_slash = resource_url.rfind('/')
	last_colon = resource_url.rfind('.')
	resource = resource_url[last_slash+1:last_colon]
	return resource

def get_video_name(video_url):
    #gets the video name from the video url
	last_slash = video_url.rfind('/')
	last_colon = video_url.rfind('.')
	video = video_url[last_slash+1:last_colon]
	return video

def get_audio_name(audio_url):
    #gets the audio name from the audio url
	last_slash = audio_url.rfind('/')
	last_colon = audio_url.rfind('.')
	audio = audio_url[last_slash+1:last_colon]
	return audio

def get_image_name(image_url):
    #gets the image name from the image url
	last_slash = image_url.rfind('/')
	last_colon = image_url.rfind('.')
	image = image_url[last_slash+1:last_colon]
	return image

def get_page_name(page_url):
	r = requests.get('https://nroer.gov.in'+str(page_url))
	soup = BeautifulSoup(r.text,'html.parser')
	s = soup.find("h3", "text-gray")
	if s is None:
		return None
	else:
		return s.string 

def top_pages_op(top_pages_list):
	print "top pagess"
	xdata = []
	ydata = []
	for i in range(0,len(top_pages_list)):
		name = get_page_name(top_pages_list[i]['key'])
		if not name is None:
	 		xdata.append(str(name))
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
	 	xdata.append(str((get_download_name(top_downloads_list[i]['key']))))
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
	 	xdata.append(str((get_resource_name(top_resources_list[i]['key']))))
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
	 	xdata.append(str((get_video_name(top_videos_list[i]['key']))))
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
	 	xdata.append(str((get_audio_name(top_audios_list[i]['key']))))
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
	 	xdata.append(str((get_image_name(top_images_list[i]['key']))))
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


def top_pages_lastWeekop():
	top_list = top_pages_lastWeek()
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file = open('topPagesLastWeek.html', 'w')
	chart = discreteBarChart(name='discreteBarChart', height=400, width=400)

	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart.buildhtml()
	output_file.write(chart.htmlcontent)
	output_file.close()

def top_pages_lastMonthop():
	top_list = top_pages_lastMonth()
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file = open('topPagesLastMonth.html', 'w')
	chart = discreteBarChart(name='discreteBarChart', height=400, width=400)

	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart.buildhtml()
	output_file.write(chart.htmlcontent)
	output_file.close()

def top_pages_lastYearop():
	top_list = top_pages_lastYear()
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file = open('topPagesLastYear.html', 'w')
	chart = discreteBarChart(name='discreteBarChart', height=400, width=400)

	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart.buildhtml()
	output_file.write(chart.htmlcontent)
	output_file.close()

def top_users_lastWeekop():
	top_list = top_users_lastWeek()
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file = open('topUsersLastWeek.html', 'w')
	chart = discreteBarChart(name='discreteBarChart', height=400, width=400)

	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart.buildhtml()
	output_file.write(chart.htmlcontent)
	output_file.close()

def top_users_lastMonthop():
	top_list = top_users_lastMonth()
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file = open('topUsersLastMonth.html', 'w')
	chart = discreteBarChart(name='discreteBarChart', height=400, width=400)

	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart.buildhtml()
	output_file.write(chart.htmlcontent)
	output_file.close()

def top_users_lastYearop():
	top_list = top_users_lastYear()
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file = open('topUsersLastYear.html', 'w')
	chart = discreteBarChart(name='discreteBarChart', height=400, width=400)

	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart.buildhtml()
	output_file.write(chart.htmlcontent)
	output_file.close()

def top_downloads_lastWeekop():
	top_list = top_downloads_lastWeek()
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file = open('topDownloadsLastWeek.html', 'w')
	chart = discreteBarChart(name='discreteBarChart', height=400, width=400)

	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart.buildhtml()
	output_file.write(chart.htmlcontent)
	output_file.close()

def top_downloads_lastMonthop():
	top_list = top_downloads_lastMonth()
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file = open('topDownloadsLastMonth.html', 'w')
	chart = discreteBarChart(name='discreteBarChart', height=400, width=400)

	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart.buildhtml()
	output_file.write(chart.htmlcontent)
	output_file.close()

def top_downloads_lastYearop():
	top_list = top_downloads_lastYear()
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
	output_file = open('topDownloadsLastYear.html', 'w')
	chart = discreteBarChart(name='discreteBarChart', height=400, width=400)

	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart.buildhtml()
	output_file.write(chart.htmlcontent)
	output_file.close()

def top_resources_lastWeekop():
	top_list = top_resources_lastWeek()
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file = open('topResourcesLastWeek.html', 'w')
	chart = discreteBarChart(name='discreteBarChart', height=400, width=400)

	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart.buildhtml()
	output_file.write(chart.htmlcontent)
	output_file.close()

def top_resources_lastMonthop():
	top_list = top_resources_lastMonth()
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
	output_file = open('topResourcesLastMonth.html', 'w')
	chart = discreteBarChart(name='discreteBarChart', height=400, width=400)

	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart.buildhtml()
	output_file.write(chart.htmlcontent)
	output_file.close()

def top_resources_lastYearop():
	top_list = top_resources_lastYear()
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file = open('topResourcesLastYear.html', 'w')
	chart = discreteBarChart(name='discreteBarChart', height=400, width=400)

	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart.buildhtml()
	output_file.write(chart.htmlcontent)
	output_file.close()

def top_videos_lastWeekop():
	top_list = top_videos_lastWeek()
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file = open('topVideosLastWeek.html', 'w')
	chart = discreteBarChart(name='discreteBarChart', height=400, width=400)

	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart.buildhtml()
	output_file.write(chart.htmlcontent)
	output_file.close()

def top_videos_lastMonthop():
	top_list = top_videos_lastMonth()
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file = open('topVideosLastMonth.html', 'w')
	chart = discreteBarChart(name='discreteBarChart', height=400, width=400)

	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart.buildhtml()
	output_file.write(chart.htmlcontent)
	output_file.close()

def top_videos_lastYearop():
	top_list = top_videos_lastYear()
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file = open('topVideosLastYear.html', 'w')
	chart = discreteBarChart(name='discreteBarChart', height=400, width=400)

	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart.buildhtml()
	output_file.write(chart.htmlcontent)
	output_file.close()

def top_audios_lastWeekop():
	top_list = top_audios_lastWeek()
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file = open('topAudiosLastWeek.html', 'w')
	chart = discreteBarChart(name='discreteBarChart', height=400, width=400)

	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart.buildhtml()
	output_file.write(chart.htmlcontent)
	output_file.close()

def top_audios_lastMonthop():
	top_list = top_audios_lastMonth()
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file = open('topAudiosLastMonth.html', 'w')
	chart = discreteBarChart(name='discreteBarChart', height=400, width=400)

	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart.buildhtml()
	output_file.write(chart.htmlcontent)
	output_file.close()

def top_audios_lastYearop():
	top_list = top_audios_lastYear()
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file = open('topAudiosLastYear.html', 'w')
	chart = discreteBarChart(name='discreteBarChart', height=400, width=400)

	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart.buildhtml()
	output_file.write(chart.htmlcontent)
	output_file.close()

def top_images_lastWeekop():
	top_list = top_images_lastWeek()
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file = open('topImagesLastWeek.html', 'w')
	chart = discreteBarChart(name='discreteBarChart', height=400, width=400)

	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart.buildhtml()
	output_file.write(chart.htmlcontent)
	output_file.close()

def top_images_lastMonthop():
	top_list = top_images_lastMonth()
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file = open('topImagesLastMonth.html', 'w')
	chart = discreteBarChart(name='discreteBarChart', height=400, width=400)

	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart.buildhtml()
	output_file.write(chart.htmlcontent)
	output_file.close()

def top_images_lastYearop():
	top_list = top_images_lastYear()
	xdata = []
	ydata = []
	for key, value in top_list.items():
		xdata.append(key)
		ydata.append(value)
    	output_file = open('topImagesLastYear.html', 'w')
	chart = discreteBarChart(name='discreteBarChart', height=400, width=400)

	extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chart.add_serie(y=ydata, x=xdata, extra=extra_serie)
	chart.buildhtml()
	output_file.write(chart.htmlcontent)
	output_file.close()
