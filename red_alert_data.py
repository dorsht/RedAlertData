#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from bidi.algorithm import get_display
from tkinter import *
from tkinter import ttk


def show_plot_data(plot_data, windows_title, x_label, y_label):
    plot_data.plot(kind="barh")
    fig_manager = plt.get_current_fig_manager()
    fig_manager.set_window_title(windows_title)
    fig_manager.window.state('zoomed')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.tight_layout()
    plt.show()


def get_oref_data():
    current_datetime = datetime.today()
    starting_operation_date = datetime(2020, 5, 10).date()  # Operation starting date.
    current_date = current_datetime.date()
    oref_url = f'https://www.oref.org.il//Shared/Ajax/GetAlarmsHistory.aspx?lang=he&fromDate={starting_operation_date.day}.{starting_operation_date.month}.{starting_operation_date.year}&toDate={current_date.day}.{current_date.month}.{current_date.year}&mode=0 '
    oref_json = requests.get(oref_url).json()
    return oref_json


def arrange_data():
    """ Currently, I'm not using the date field, this is the reason I didn't drop it from the df, maybe I'll use it
    in the future."""
    df = pd.DataFrame.from_records(get_oref_data())
    df['data'] = df['data'].str.split(',')
    df.rename(columns={'data': 'area_name'}, inplace=True)
    df = df.explode('area_name')
    df['area_name'] = df['area_name'].str.strip()
    # Correct some data:
    df = df[df['area_name'].str.len() > 2]
    df['area_name'].replace('אשדוד - אזור תעשייה צפוני ונ', 'אשדוד - אזור תעשייה צפוני', inplace=True)
    return df


def show_num_of_alerts_per_area(df):
    map_of_areas = {}
    for index, row in df.iterrows():
        area_name = row['area_name']
        if area_name not in map_of_areas.keys():
            map_of_areas[area_name] = 1
        else:
            map_of_areas[area_name] += 1
    # Sorting data by number of alerts:
    # Reverse for descending order.
    map_of_areas = dict(sorted(map_of_areas.items(), key=lambda item: item[1], reverse=True))
    first_values = list(map_of_areas.values())[:40]
    first_keys = list(map(lambda area: get_display(area), list(map_of_areas.keys())[:40]))
    plotdata = pd.DataFrame({"Alerts": first_values}, index=first_keys)
    show_plot_data(plotdata, 'Number of alerts by areas, the 40 most alerted areas', 'Number of alerts', 'Area')


def show_num_of_alerts_per_hour(df):
    map_of_hours = {}
    for index, row in df.iterrows():
        hour = int(row['time'][0:2])
        if hour not in map_of_hours.keys():
            map_of_hours[hour] = 1
        else:
            map_of_hours[hour] += 1
    # Sorting data by hours:
    # noinspection PyTypeChecker
    # Reverse for descending order.
    map_of_hours = dict(sorted(map_of_hours.items(), key=lambda item: item[0], reverse=True))
    plotdata = pd.DataFrame({"Alerts": map_of_hours.values()}, index=map_of_hours.keys())
    show_plot_data(plotdata, 'Number of alerts by hours', 'Number of alerts', 'Hour')


def arrange_data_for_each_specific_area(df):
    map_of_areas_and_hours = {}
    set_of_areas = list()
    for index, row in df.iterrows():
        area_name = row['area_name']
        if area_name not in set_of_areas:
            set_of_areas.append(area_name)
        hour = int(row['time'][0:2])
        if area_name not in map_of_areas_and_hours.keys():
            map_of_areas_and_hours[area_name] = {}
            current_area = map_of_areas_and_hours[area_name]
            current_area[hour] = 1
        else:
            current_area = map_of_areas_and_hours[area_name]
            if hour in current_area.keys():
                current_area[hour] += 1
            else:
                current_area[hour] = 1
    set_of_areas = list(sorted(set_of_areas, key=lambda item: item))
    return map_of_areas_and_hours, set_of_areas


def show_data(df):
    map_of_areas_and_hours, set_of_areas = arrange_data_for_each_specific_area(df)

    main_window = Tk()
    main_window.title("Red alert data")
    main_window.geometry("300x150")

    longest_length = len(max(set_of_areas, key=len))
    dim_combo = ttk.Combobox(main_window, state='readonly', values=set_of_areas, width=longest_length + 5)
    dim_combo.set(set_of_areas[0])  # Default option, first value
    dim_combo.pack()

    def create_data_for_area_and_plot():
        selected_area_name = dim_combo.get()
        map_of_hours = dict(sorted(map_of_areas_and_hours[selected_area_name].items(), key=lambda item: item[0], reverse=True))  # Reverse for descending order.
        hours = list(map_of_hours.keys())
        alerts_in_hour = list(map_of_hours.values())
        plotdata = pd.DataFrame({"Alerts": alerts_in_hour}, index=hours)
        show_plot_data(plotdata, 'Number of alerts by hours in {0}'.format(selected_area_name), 'Number of alerts',
                       'Hour')

    show_data_for_specific_area_button = Button(main_window, text="Show area data",
                                                command=create_data_for_area_and_plot)
    show_data_for_specific_area_button.pack()
    show_num_of_alerts_by_most_alerted_areas_button = Button(main_window,
                                                             text="Show number of alerts by 40 most alerted areas",
                                                             command=lambda: show_num_of_alerts_per_area(df))
    show_num_of_alerts_by_most_alerted_areas_button.pack()
    show_num_of_alerts_by_hours_button = Button(main_window, text="Show number of alerts by hours",
                                                command=lambda: show_num_of_alerts_per_hour(df))
    show_num_of_alerts_by_hours_button.pack()
    mainloop()


def main():
    df = arrange_data()
    show_data(df)


if __name__ == '__main__':
    main()
