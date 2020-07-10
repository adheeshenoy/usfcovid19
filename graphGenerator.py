import pandas as pd
import plotly.graph_objs as go
from datetime import datetime
import constants as const


# Tracers
def generate_daily_bar_graph(tampa, stPete):
    tracerList = []
    tracerList.append(
        go.Bar(x=tampa['dates'],
               y=tampa['cases'],
               name='Tampa',
               marker_color=const.DARK_GREEN))
    tracerList.append(
        go.Bar(x=stPete['dates'],
               y=stPete['cases'],
               name='St. Petersburg',
               marker_color=const.LIGHT_GOLD))
    return tracerList


def generate_total_scatter_graph(tampa, stPete):
    tracerList = []
    tampa['cases'] = tampa['cases'].cumsum()
    stPete['cases'] = stPete['cases'].cumsum()

    tracerList.append(
        go.Scatter(x=tampa['dates'],
                   y=tampa['cases'],
                   name='Tampa',
                   mode='lines',
                   line=dict(color=const.DARK_GREEN, width=4)))
    tracerList.append(
        go.Scatter(x=stPete['dates'],
                   y=stPete['cases'],
                   name='St. Petersburg',
                   mode='lines',
                   line=dict(color=const.LIGHT_GOLD, width=4)))
    return tracerList


def generate_employee_student_total_graph(student, employee, health=None):
    tracerList = []
    student['cases'] = student['cases'].cumsum()
    employee['cases'] = employee['cases'].cumsum()
    if health is not None:
        health['cases'] = health['cases'].cumsum()
        tracerList.append(
            go.Scatter(x=health['dates'],
                       y=health['cases'],
                       name='USF Health Employee',
                       line = dict(color = const.TEAL)))
    tracerList.append(
        go.Scatter(x=student['dates'], y=student['cases'], name='Student', line = dict(color = const.STORM)))
    tracerList.append(
        go.Scatter(x=employee['dates'], y=employee['cases'], name='Employee', line = dict(color = const.APPLE)))
    return tracerList


def generate_employee_student_daily_graph(student, employee, health=None):
    tracerList = []
    tracerList.append(
        go.Bar(x=student['dates'], y=student['cases'], name='Student', marker_color = const.STORM))
    tracerList.append(
        go.Bar(x=employee['dates'], y=employee['cases'], name='Employee', marker_color = const.APPLE))
    if health is not None:
        tracerList.append(
            go.Bar(x=health['dates'],
                   y=health['cases'],
                   name='USF Health Employee', marker_color = const.TEAL))
    return tracerList


def generate_box_plot(student, employee, health=None):
    tracerList = []
    tracerList.append(
        go.Box(y=student['cases'],
               name='Student',
               boxpoints='all',
               boxmean=True,
               marker_color = const.STORM))
    tracerList.append(
        go.Box(y=employee['cases'],
               name='Employee',
               boxpoints='all',
               boxmean=True,
               marker_color = const.APPLE))
    if health is not None:
        tracerList.append(
            go.Box(y=health['cases'],
                   name='USF Health Employee',
                   boxpoints='all',
                   boxmean=True,
                   marker_color = const.TEAL))
    return tracerList


def generate_pie_plot(student, employee, health=None):
    if health is not None:
        values = [
            int(student['cases'].sum()),
            int(employee['cases'].sum()),
            int(health['cases'].sum())
        ]
        labels = ['Student', 'Employee', 'USF Health Employee']
        colors = [const.STORM, const.APPLE, const.TEAL]
    else:
        values = [int(student['cases'].sum()), int(employee['cases'].sum())]
        labels = ['Student', 'Employee']
        colors = [const.STORM, const.APPLE]
    return [
        go.Pie(labels=labels,
               values=values,
               hole=.3,
               marker=dict(colors=colors))
    ]


# Layouts
def general_graph_layout(title):
    return dict(title=dict(text=title,
                           font=dict(size=22, color=const.DARK_GREEN)),
                xaxis=dict(tickfont=dict(size=16)),
                yaxis=dict(tickfont=dict(size=16),
                           title=dict(text='Number of Cases',
                                      font=dict(size=16))),
                dragmode=False,
                legend=dict(bgcolor=const.GREY,
                            font=dict(size=14)))


def general_bar_layout(title):
    return dict(
        title=dict(text=title, font=dict(size=22, color=const.DARK_GREEN)),
        xaxis=dict(
            tickfont=dict(size=16),
            rangeselector=dict(
                margin=dict(b=2),
                font=dict(size=14, color=const.DARK_GREEN),
                bgcolor=const.GREY,
                buttons=list([
                    dict(count=15,
                         label="15 Days",
                         step="day",
                         stepmode="backward"),
                    dict(count=1,
                         label="1 month",
                         step="month",
                         stepmode="backward"),
                    dict(count=3,
                         label="3 months",
                         step="month",
                         stepmode="backward"),
                    #   dict(count=6,
                    #        label="6 months",
                    #        step="month",
                    #        stepmode="backward"),
                    dict(label='All', step="all")
                ]))),
        yaxis=dict(tickfont=dict(size=16),
                   title=dict(text='Number of Cases', font=dict(size=16))),
        dragmode=False,
        legend=dict(bgcolor=const.GREY, font=dict(size=14)),
    )


def stacked_graph_layout(title):
    return dict(
        barmode = 'stack',
        title=dict(text=title, font=dict(size=22, color=const.DARK_GREEN)),
        xaxis=dict(
            tickfont=dict(size=16),
            rangeselector=dict(
                margin=dict(b=2),
                font=dict(size=14, color=const.DARK_GREEN),
                bgcolor=const.GREY,
                buttons=list([
                    dict(count=15,
                         label="15 Days",
                         step="day",
                         stepmode="backward"),
                    dict(count=1,
                         label="1 month",
                         step="month",
                         stepmode="backward"),
                    dict(count=3,
                         label="3 months",
                         step="month",
                         stepmode="backward"),
                    #   dict(count=6,
                    #        label="6 months",
                    #        step="month",
                    #        stepmode="backward"),
                    dict(label='All', step="all")
                ]))),
        yaxis=dict(tickfont=dict(size=16),
                   title=dict(text='Number of Cases', font=dict(size=16))),
        dragmode=False,
        legend=dict(bgcolor=const.GREY, font=dict(size=14)),
    )
