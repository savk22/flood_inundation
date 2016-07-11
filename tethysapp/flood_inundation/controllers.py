from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime
import urllib2
from tethys_sdk.gizmos import DatePicker
from tethys_sdk.gizmos import Button
from tethys_sdk.gizmos import SelectInput

@login_required()
def home(request):
    """
    Controller for the app home page.
    """
    # Check digits in month and day (i.e. 2016-05-09, not 2016-5-9)
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

    # Dictionary for number of houses impacted by flood for each depth
    house_count_dict = {
        0: 0,
        0.5: 917,
        1: 1605,
        1.5: 2314,
        2: 3144,
        2.5: 4075,
        3: 5118,
        3.5: 6359,
        4: 7465,
        4.5: 8517,
        5: 9567,
        5.5: 10775,
        6: 12377,
        6.5: 13689,
        7: 14927,
        7.5: 16067,
        8: 17124,
        8.5: 18329,
        9: 19591,
        9.5: 20826,
        10: 21928,
        10.5: 22998,
        11: 24239
    }

    # I'm defining the context here because the items contained in this context are used  below (more items are added further down)
    context = {"forecast_range_select": forecast_range_select,
               "forecast_date_picker": forecast_date_picker,
               "forecast_time_select": forecast_time_select,
               "get_forecast": get_forecast,
               "get_increase": get_increase,
               "house_count_dict": house_count_dict}

    # Get input from gizmos
    forecast_range = None
    forecast_date = None
    comid_time = None

    if request.GET.get('forecast_range'):
        forecast_range = request.GET['forecast_range']
    if request.GET.get('forecast_date'):
        forecast_date = request.GET['forecast_date']
    if request.GET.get('comid_time'):
        comid_time = request.GET['comid_time']

    # Get forecast data
    if forecast_range and forecast_date and comid_time:

        # Only using one COMID for forecast data
        comid = '18229923'

        # URL for getting forecast data and put in a list
        time_series_list_api = []
        house_count_list = []
        if comid is not None and len(comid) > 0:
            lag = 't00z'
            forecast_size = request.GET['forecast_range']
            comid_time = "06"
            if forecast_size == "short_range":
                comid_time = request.GET['comid_time']
            # print comid_time
            # print comid
            # print forecast_date
            forecast_date_end = now_str
            url = 'https://apps.hydroshare.org/apps/nwm-forecasts/api/GetWaterML/?config={0}&geom=channel_rt&variable=streamflow&COMID={1}&lon=&lat=&startDate={2}&endDate={3}&time={4}&lag={5}'.format(forecast_range, comid, forecast_date, forecast_date_end, comid_time, lag)
            print url
            url_api = urllib2.urlopen(url)
            data_api = url_api.read()
            # print data_api
            x = data_api.split('dateTimeUTC=')
            x.pop(0)


            for elm in x:
                info = elm.split(' ')
                value = info[7].split('<')
                value1 = value[0].replace('>', '')
                value2 = float(value1)
                value_round = round(value2)
                value_round_int = int(value_round)
                if value_round_int < 90201:
                    value_round_int = 0
                elif value_round_int >= 90201 and value_round_int < 95274:
                    value_round_int = 0.5
                elif value_round_int >= 95274 and value_round_int < 103147:
                    value_round_int = 1
                elif value_round_int >= 103147 and value_round_int < 111671:
                    value_round_int = 1.5
                elif value_round_int >= 111671 and value_round_int < 120899:
                    value_round_int = 2
                elif value_round_int >= 120899 and value_round_int < 130890:
                    value_round_int = 2.5
                elif value_round_int >= 130890 and value_round_int < 141706:
                    value_round_int = 3
                elif value_round_int >= 141706 and value_round_int < 153417:
                    value_round_int = 3.5
                elif value_round_int >= 153417 and value_round_int < 166095:
                    value_round_int = 4
                elif value_round_int >= 166095 and value_round_int < 179820:
                    value_round_int = 4.5
                elif value_round_int >= 179820 and value_round_int < 194680:
                    value_round_int = 5
                elif value_round_int >= 194680 and value_round_int < 210768:
                    value_round_int = 5.5
                elif value_round_int >= 210768 and value_round_int < 228185:
                    value_round_int = 6
                elif value_round_int >= 228185 and value_round_int < 247042:
                    value_round_int = 6.5
                elif value_round_int >= 247042 and value_round_int < 267457:
                    value_round_int = 7
                elif value_round_int >= 267457 and value_round_int < 289559:
                    value_round_int = 7.5
                elif value_round_int >= 289559 and value_round_int < 313487:
                    value_round_int = 8
                elif value_round_int >= 313487 and value_round_int < 339393:
                    value_round_int = 8.5
                elif value_round_int >= 339393 and value_round_int < 367439:
                    value_round_int = 9
                elif value_round_int >= 367439 and value_round_int < 397803:
                    value_round_int = 9.5
                elif value_round_int >= 397803 and value_round_int < 430677:
                    value_round_int = 10
                elif value_round_int >= 430677 and value_round_int < 466267:
                    value_round_int = 10.5
                elif value_round_int >= 466267:
                    value_round_int = 11

                house_count_list.append(house_count_dict[value_round_int])
                time_series_list_api.append(value_round_int)

            # print time_series_list_api
            # Put forecast data ito a numbered list based on short or medium range
            if forecast_range == 'short_range':
                range_slider = range(1, 16)
            elif forecast_range == 'medium_range':
                range_slider = range(1,81)
            # range_list = zip(range_slider, time_series_list_api)
            range_list = [list(a) for a in zip(range_slider, time_series_list_api, house_count_list)]
            # print range_list

            # Items to be added to context, but not defined until just before this point
            context["forecast_range"] = forecast_range
            context["range_list"] = range_list




    return render(request, 'flood_inundation/home.html', context)