import plotly.graph_objs as go
import constants as const
import helper_functions as hf

# Tracers
def generate_daily_bar_graph(locationList):
    '''Return tracers for daily bar graph based on location'''
    return [
        go.Bar(
            x=location['dates'],
            y=location['cases'],
            name=name,
            marker_color=color,
        )
        for location, color, name in zip(
            locationList, const.GENERAL_COLORS, const.CAMPUS_NAMES
        )
    ]

def generate_total_scatter(selection, location_list, prediction_list):
    '''Return tracers for total scatter graphs based on location'''
    try:
        tracer_list = []
        if selection == 'actual':
            for location, color, name in zip(location_list, const.GENERAL_COLORS, const.CAMPUS_NAMES):
                location['cases'] = location['cases'].cumsum()
                tracer_list.append(go.Scatter(
                    x=location['dates'],
                    y=location['cases'],
                    name=name, mode='lines+markers', line=dict(color=color, width=3)))
        elif selection == 'prediction':
            for location, color, name, col_name in zip(prediction_list, const.GENERAL_COLORS, const.CAMPUS_NAMES,
                                                       const.PREDICTION_COL_NAMES):
                tracer_list.append(go.Scatter(
                    x=location['DS'],
                    y=location[col_name],
                    name=name, mode='lines', line=dict(color=color, width=3)))

        return tracer_list
    except Exception as e:
        print(e)


def generate_employee_student_total_graph(occupationList):
    '''Return tracers for total scatter graph based on occupation'''
    tracerList = []
    
    for occupation, color, name in zip(occupationList, const.OCCUPATION_COLORS, const.OCCUPATION_NAMES):
        occupation['cases'] = occupation['cases'].cumsum()
        tracerList.append(
            go.Scatter(x=occupation['dates'],
               y=occupation['cases'],
               name=name,
               mode = 'lines+markers',
               line = dict(color = color, width = 3)
               )
        )
    return tracerList


def generate_employee_student_daily_graph(occupationList):
    '''Return tracers for daily bar graph based on occupation'''
    return [
        go.Bar(
            x=occupation['dates'],
            y=occupation['cases'],
            name=name,
            marker_color=color,
        )
        for occupation, color, name in zip(
            occupationList, const.OCCUPATION_COLORS, const.OCCUPATION_NAMES
        )
    ]


def generate_box_plot(occupationList):
    '''Return tracers for box plot based on occupation'''
    return [
        go.Box(
            y=occupation['cases'],
            name=name,
            boxpoints='all',
            boxmean=True,
            marker_color=color,
        )
        for occupation, color, name in zip(
            occupationList, const.OCCUPATION_COLORS, const.OCCUPATION_NAMES
        )
    ]


def generate_pie_plot(occupationList):
    '''Return tracers for pie plot based on occupation'''
    values = [occupation['cases'].sum() for occupation in occupationList]
    return [
        go.Pie(labels=const.OCCUPATION_NAMES,
               values=values,
               hole=.3,
               marker=dict(colors=const.OCCUPATION_COLORS))
    ]

# Layouts
def general_graph_layout(title):
    '''Returns a general layout for a graph'''
    return dict(title=dict(text=title,
                           font=dict(size=22, color=const.DARK_GREEN)),
                xaxis=dict(tickfont=dict(size=16)),
                yaxis=dict(tickfont=dict(size=16),
                           title=dict(text='Number of Cases',
                                      font=dict(size=16))),
                dragmode=False,
                legend=dict(bgcolor=const.GREY,
                            font=dict(size=14)),
                # TODO Add lines on every occasion
                # shapes = dict(type = 'line',
                #               x0='2020-08-24 00:00:00',
                #               y0=0,
                #               x1='2020-08-24 00:00:00',
                #               y1=450,
                #               line = dict(color='Blue',
                #                           width = 3)
                #               )
                )

def generate_bar_layout(title, barmode):
    '''Returns a layout for a bar graph with the barmode dependent on the 
    input'''
    layout = dict(
        barmode = barmode,
        title=dict(text=title, font=dict(size=22, color=const.DARK_GREEN)),
        xaxis=dict(
            tickfont=dict(size=16),
            # rangeselector=
            ),
                # dict(
                # margin=dict(b=2),
                # font=dict(size=14, color=const.DARK_GREEN),
                # bgcolor=const.GREY,
                # buttons=list([
                #     dict(count=15,
                #          label="15 Days",
                #          step="day",
                #          stepmode="backward"),
                #     dict(count=1,
                #          label="1 month",
                #          step="month",
                #          stepmode="backward"),
                    # dict(count=3,
                    #      label="3 months",
                    #      step="month",
                    #      stepmode="backward"),
                    #   dict(count=6,
                    #        label="6 months",
                    #        step="month",
                    #        stepmode="backward"),
                #     dict(label='All', step="all")
                # ]))),
        yaxis=dict(tickfont=dict(size=16),
                   title=dict(text='Number of Cases', font=dict(size=16))),
        dragmode=False,
        legend=dict(bgcolor=const.GREY, font=dict(size=14)),
    )
    
    hf.add_range_selector(layout, default = '1m')
    return layout

def generate_line():
    return 