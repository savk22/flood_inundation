from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime
import urllib2
from tethys_sdk.gizmos import DatePicker
from tethys_sdk.gizmos import Button
from tethys_sdk.gizmos import SelectInput
from tethys_sdk.gizmos import RangeSlider

# import packages for NWM
from owslib.waterml.wml11 import WaterML_1_1 as wml
import requests as req
import datetime as dt
import csv
import os

import shutil
import numpy as np
import pandas as pd

@login_required()
def home(request):
	"""
	Controller for the app home page.
	"""
	# Check digits in month and day (i.e. 2016-05-09, not 2016-5-9)

	slider1 = RangeSlider(display_text='Slider 1',
	                      name='slider1',
	                      min=0,
	                      max=100,
	                      initial=50,
	                      step=1)


	def check_digit(num):
		num_str = str(num)
		if len(num_str) < 2:
			num_str = '0' + num_str
		return num_str

	# Find current time
	t_now = datetime.now()
	now_str = "{0}-{1}-{2}".format(t_now.year,check_digit(t_now.month),check_digit(t_now.day))

	# Forecast size dropdown
	forecast_range_select = SelectInput(display_text='Forecast Size',
	                                    name='forecast_range',
	                                    multiple=False,
	                                    options=[ ('Short', 'short_range'), ('Medium', 'medium_range')],
	                                    initial=['medium_range'],
	                                    original=['medium_range'])

	# Forecat date selector
	forecast_date_picker = DatePicker(name='forecast_date',
	                                  display_text='Forecast Date Start',
	                                  end_date='0d',
	                                  autoclose=True,
	                                  format='yyyy-mm-dd',
	                                  start_view='month',
	                                  today_button=True,
	                                  initial=now_str)

	# Forecast time selector
	forecast_time_select = SelectInput(display_text='Start Time',
	                                   name='comid_time',
	                                   multiple=False,
	                                   options=[('00:00', "00"), ('01:00', "01"), ('02:00', "02"),
	                                            ('03:00', "03"), ('04:00', "04"), ('05:00', "05"),
	                                            ('06:00', "06"), ('07:00', "07"), ('08:00', "08"),
	                                            ('09:00', "09"), ('10:00', "10"), ('11:00', "11"),
	                                            ('12:00', "12"), ('13:00', "13"), ('14:00', "14"),
	                                            ('15:00', "15"), ('16:00', "16"), ('17:00', "17"),
	                                            ('18:00', "18"), ('19:00', "19"), ('20:00', "20"),
	                                            ('21:00', "21"), ('22:00', "22"), ('23:00', "23")],
	                                   initial=['12'],
	                                   original=['12'])

	# View flood forecast button
	get_forecast = Button(display_text='View Flood Forecast',
	                      name='flood_forecast',
	                      attributes='form=forecast-form',
	                      submit=True)

	# View flood animation button
	get_increase = Button(display_text='View Flood Animation',
	                      name='flood_increase',
	                      attributes='form=increase-form',
	                      submit=True)

	# Get input from gizmos
	forecast_range = None
	forecast_date = None
	# comid_time = None

	#Calls Michaels API, output NWM data in one csv inside the data folder
	if request.GET:
		forecast_range = request.GET['forecast_range']

		forecast_date = request.GET['forecast_date']

		comid_time = request.GET['comid_time']
		app_dir = os.path.dirname(__file__)
		comid_dir = os.path.join(app_dir,'public/data/InundationLibrary')
		comid_list = [int(o) for o in os.listdir(comid_dir) if os.path.isdir(os.path.join(comid_dir,o)) and o.startswith('.') != True]


		csvdir = os.path.join(app_dir,'public/data/output.csv')


		with open(csvdir, 'wb') as fl:
			wr = csv.writer(fl, delimiter=',')
			wr.writerow(['configuration','comid','date','discharge'])
			for comid in comid_list:
				if forecast_range == 'short_range':
					url = 'https://apps.hydroshare.org/apps/nwm-forecasts/api/GetWaterML/?config=' + forecast_range + '&geom=channel_rt&variable=streamflow&COMID=' + str(comid) + '&startDate=' + forecast_date + '&time=' + comid_time
				elif forecast_range == 'medium_range':
					url = 'https://apps.hydroshare.org/apps/nwm-forecasts/api/GetWaterML/?config=' + forecast_range + '&geom=channel_rt&variable=streamflow&COMID=' + str(comid) + '&startDate=' + forecast_date

				response = req.get(url, verify=False)

				response_string = response.text.encode('utf-8')
				parse_wml = wml(response_string).response


				value_pairs_list = []
				# get api response
				variable = parse_wml.get_series_by_variable(var_name='Flow Forecast')
				value_list = variable[0].values[0]

				# list of tuples with date-value pairs
				value_pairs = value_list.get_date_values()

				for item in value_pairs:
					wr.writerow([forecast_range,str(comid),item[0].strftime('%Y-%m-%d %H:%M:%S'),item[1]])

		## Input folders for Xings code

		ratingcurve_path = os.path.join(app_dir,'public/data/RatingCurve')
		FPlibrary_path = os.path.join(app_dir,'public/data/InundationLibrary')
		NWCQ_path = csvdir
		NewFolderName = StreamflowToHeight(NWCQ_path, ratingcurve_path, FPlibrary_path, app_dir)

		context = {"forecast_range_select": forecast_range_select,
		           "forecast_date_picker": forecast_date_picker,
		           "forecast_time_select": forecast_time_select,
		           "get_forecast": get_forecast,
		           "get_increase": get_increase,
		           "NewFolderName": NewFolderName}
	else:
		context = {"forecast_range_select": forecast_range_select,
		           "forecast_date_picker": forecast_date_picker,
		           "forecast_time_select": forecast_time_select,
		           "get_forecast": get_forecast,
		           "get_increase": get_increase}

	return render(request, 'flood_inundation/home.html', context)

### Xing's code converts streamflow to depth through a rating curve then grabs the correlating flood map from the InundationLibrary

def StreamflowToHeight(NWCQ_path, ratingcurve_path, FPlibrary_path, app_dir):
	df = pd.read_csv(NWCQ_path, delimiter=',', usecols=(0, 1, 2, 3,))

	COMIDlist = df['comid'].unique()
	AvaiCOMIDlist = []

	for RC in os.listdir(ratingcurve_path):
		AvaiCOMIDlist.append(RC.split()[0])

	if df['configuration'][0] == 'short_range':
		FolderName = 'short_range_' + df['date'][0].replace(" ", "_").replace(":", "_").replace("/", "_")

		if os.path.exists(os.path.join(app_dir, 'public/data/results', FolderName)):
			shutil.rmtree(os.path.join(app_dir, 'public/data/results', FolderName))

		if not os.path.exists(os.path.join(app_dir, 'public/data/results', FolderName)):
			os.mkdir(os.path.join(app_dir, 'public/data/results', FolderName))

		if os.path.exists(os.path.join(app_dir, 'public/data/results', "Floodplain_" + FolderName)):
			shutil.rmtree(os.path.join(app_dir, 'public/data/results', "Floodplain_" + FolderName))

		if not os.path.exists(os.path.join(app_dir, 'public/data/results', "Floodplain_" + FolderName)):
			os.mkdir(os.path.join(app_dir, 'public/data/results', "Floodplain_" + FolderName))

		for i in range(15):

			Dischargelist = []
			Heightlist = []

			for j in range(len(COMIDlist)):
				##        np.savetxt(os.path.join(FolderName,str(df['date'][i].replace(" ","_").replace(":","_").replace("/","_"))+".csv"), np.column_stack((COMIDlist, Dischargelist)),
				##                   delimiter=',',header="COMID,Discharge", comments='')

				Discharge = df['discharge'][i + j * 15]
				Dischargelist.append(Discharge)

				if str(COMIDlist[j]) in AvaiCOMIDlist:
					H, Q = np.loadtxt(os.path.join(ratingcurve_path, str(COMIDlist[j]) + " Rating Curve.csv"),
					                  delimiter=',', skiprows=1,
					                  usecols=(1, 2,), unpack=True)

					H = H * 0.3048
					Q = Q * 0.0283168

					if np.any(Q):

						if Discharge < Q[0]:
							Height = Discharge / Q[0] * H[0]

						elif Discharge > Q[-1]:
							Height = H[-2] + (H[-1] - H[-2]) / (Q[-1] - Q[-2]) * (Discharge - Q[-2])

						else:
							Height = np.interp(Discharge, Q, H)
						Heightlist.append(Height)

						FPfiles = os.listdir(os.path.join(FPlibrary_path, str(COMIDlist[j])))
						H_available = []
						Suffix = "m.tif"

						for FPfile in FPfiles:
							if isfloat(FPfile[:3]):
								H_available.append(float(FPfile[:3]))


						H_available = np.asarray(H_available)
						H_round = find_nearest(H_available, Height)
						FPOutputFolder = os.path.join(app_dir, 'public/data/results', "Floodplain_" + FolderName,
						                              str(df['date'][i].replace(" ", "_").replace(":", "_").replace("/", "_")))

						if not os.path.exists(FPOutputFolder):
							os.mkdir(FPOutputFolder)

						shutil.copy2(os.path.join(FPlibrary_path, str(COMIDlist[j]),
						                          str(H_round) + Suffix), os.path.join(FPOutputFolder,
						                                                               str(COMIDlist[j]) + "_" + str(H_round) + Suffix))

					else:
						Heightlist.append(np.nan)

				else:
					Heightlist.append(np.nan)

			np.savetxt(os.path.join(app_dir, 'public/data/results',FolderName,
			                        str(df['date'][i].replace(" ", "_").replace(":", "_").replace("/", "_")) + ".csv"),
			           np.column_stack((COMIDlist, Dischargelist, Heightlist)),
			           delimiter=',', header="COMID,Discharge,StageHeight", comments='')

	if df['configuration'][0] == 'medium_range':
		FolderName = 'medium_range_' + df['date'][0].replace(" ", "_").replace(":", "_").replace("/", "_")

		if os.path.exists(os.path.join(app_dir, 'public/data/results', FolderName)):
			shutil.rmtree(os.path.join(app_dir, 'public/data/results', FolderName))

		if not os.path.exists(os.path.join(app_dir, 'public/data/results', FolderName)):
			os.mkdir(os.path.join(app_dir, 'public/data/results', FolderName))

		if os.path.exists(os.path.join(app_dir, 'public/data/results', "Floodplain_" + FolderName)):
			shutil.rmtree(os.path.join(app_dir, 'public/data/results', "Floodplain_" + FolderName))

		if not os.path.exists(os.path.join(app_dir, 'public/data/results', "Floodplain_" + FolderName)):
			os.mkdir(os.path.join(app_dir, 'public/data/results',"Floodplain_" + FolderName))

		for i in range(80):
			Dischargelist = []
			Heightlist = []

			for j in range(len(COMIDlist)):
				##        np.savetxt(os.path.join(FolderName,str(df['date'][i].replace(" ","_").replace(":","_").replace("/","_"))+".csv"), np.column_stack((COMIDlist, Dischargelist)),
				##                   delimiter=',',header="COMID,Discharge", comments='')

				Discharge = df['discharge'][i + j * 15]
				Dischargelist.append(Discharge)

				if str(COMIDlist[j]) in AvaiCOMIDlist:
					H, Q = np.loadtxt(os.path.join(ratingcurve_path, str(COMIDlist[j]) + " Rating Curve.csv"),
					                  delimiter=',', skiprows=1,
					                  usecols=(1, 2,), unpack=True)
					H = H * 0.3048
					Q = Q * 0.0283168

					if np.any(Q):
						if Discharge < Q[0]:
							Height = Discharge / Q[0] * H[0]
						elif Discharge > Q[-1]:
							Height = H[-2] + (H[-1] - H[-2]) / (Q[-1] - Q[-2]) * (Discharge - Q[-2])
						else:
							Height = np.interp(Discharge, Q, H)
						Heightlist.append(Height)
						FPfiles = os.listdir(os.path.join(FPlibrary_path, str(COMIDlist[j])))
						H_available = []
						Suffix = "m.tif"
						for FPfile in FPfiles:
							if isfloat(FPfile[:3]):
								H_available.append(float(FPfile[:3]))
						H_available = np.asarray(H_available)
						H_round = find_nearest(H_available, Height)
						FPOutputFolder = os.path.join(app_dir, 'public/data/results', "Floodplain_" + FolderName,
						                              str(df['date'][i].replace(" ", "_").replace(":", "_").replace("/", "_")))
						if not os.path.exists(FPOutputFolder):
							os.mkdir(FPOutputFolder)
						shutil.copy2(os.path.join(FPlibrary_path, str(COMIDlist[j]),
						                          str(H_round) + Suffix),
						             os.path.join(FPOutputFolder,
						                          str(COMIDlist[j]) + "_" + str(H_round) + Suffix))
					else:
						Heightlist.append(np.nan)
				else:
					Heightlist.append(np.nan)
			np.savetxt(os.path.join(app_dir, 'public/data/results', FolderName,
			                        str(df['date'][i].replace(" ", "_").replace(":", "_").replace("/", "_")) + ".csv"),
			           np.column_stack((COMIDlist, Dischargelist, Heightlist)),
			           delimiter=',', header="COMID,Discharge,StageHeight", comments='')

	return FolderName

def isfloat(value):
	try:
		float(value)
		return True
	except ValueError:
		return False


def find_nearest(array, value):
	idx = (np.abs(array - value)).argmin()
	return array[idx]


