import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import constants as const

# Navigation Bar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("USF Covid-19 Page", href="https://www.usf.edu/coronavirus/", external_link=True, target = '__blank')),
        dbc.NavItem(
            dbc.NavLink("Campus Information",
                        href="#daily-bar-graph",
                        external_link=True)),
        dbc.NavItem(
            dbc.NavLink("Data Table",
                        href="#table-header",
                        external_link=True))
    ],
    brand="COVID-19 Dashboard for University Of South Florida",
    brand_href="https://www.usf.edu/coronavirus/",
    color=const.LIGHT_GREEN,
    fluid=True,
    expand = 'lg',
    id = 'navigation',
    dark=True,
    style=dict(overflowX = 'hidden',
               borderBottom="solid 1px white"),
    )

# Alert
alert = html.Div([
    dbc.Alert(
            "Disclaimer: The purpose of this website is only to present the COVID-19 data on the USF Campuses. We do not take ownership of the data as it was acquired from the USF Coronavirus website.",
            id="alert-fade",
            dismissable=True,
            is_open=True,
        )
])

# Collapse for graphs
tampaCollapse = html.Div(
    [
        dbc.Button(
            "What does this Graph mean?",
            id="tampa-collapse-button",
            className="mb-3",
            color="primary",
        ),
        dbc.Collapse(
            dbc.Card(dbc.CardBody([
                html.H5('The plot represents the distribution of Covid-19 cases through their quartiles'),
                html.Ul([
                    html.Li(html.H6('The number of cases per day for an occupation is concentrated between the lower(Q1) and upper(Q3) quartiles.')),
                    html.Li(html.H6('The mean represents the average number of daily reported cases for the occupation.')),
                ]),
                html.H5('''The data suggests that students on the Tampa Campus have a higher mean and a more distributed box
                                plot. This could be due to a higher probability of students assembling in groups.''')
                ]),style = dict(background = const.GREY)),
            id="tampa-collapse",style = dict(textAlign = 'left')
        ),
    ],
)


# Card overview
# Tampa Card layout
tampaCardContent = [
    dbc.CardHeader(html.H4("Tampa Campus"),style = dict(background = const.GREY, color = const.DARK_GREEN)),
    dbc.CardBody([
        html.H4("Total Cases", className="card-title"),
        html.H5(
            "",
            id='tampa-card-totalcases',
            className="card-text",
        ),
        html.H4("Latest update", className="card-title"),
        html.H5(
            "",
            id='tampa-card-update',
            className="card-text",
        ),
    ], style = dict(background = 'white', color = 'black')),
]

# Health
healthCardContent = [
    dbc.CardHeader(html.H4("USF Health"),style = dict(background = const.GREY, color = const.DARK_GREEN)),
    dbc.CardBody([
        html.H4("Total Cases", className="card-title"),
        html.H5(
            "",
            id='tampa-card-health-totalcases',
            className="card-text",
        ),
        html.H4("Latest update", className="card-title"),
        html.H5(
            "",
            id='tampa-card-health-update',
            className="card-text",
        ),
    ], style = dict(background = 'white', color = 'black')),
]

# St. Pete card layout
stPeteCardContent = [
    dbc.CardHeader(html.H4("St. Petersburg Campus"),  style = dict(background = const.GREY, color = const.DARK_GREEN)),
    dbc.CardBody([
        html.H4("Total Cases", className="card-title"),
        html.H5(
            "",
            id='st-pete-card-totalcases',
            className="card-text",
        ),
        html.H4("Latest update", className="card-title"),
        html.H5(
            "",
            id='st-pete-card-update',
            className="card-text",
        ),
    ], style = dict(background = 'white', color = 'black')),
]

# Card Layout
cards = html.Div([
    dbc.Row(
        [
            dbc.Col(dbc.Card(tampaCardContent),
                    className='col-sm'),
            dbc.Col(dbc.Card(stPeteCardContent),
                    className='col-sm'),
            dbc.Col(dbc.Card(healthCardContent),
                    className='col-sm')
        ],
        className="mb-4 w-50",
        align = "stretch",
        style = dict(marginTop = '1rem')
    )
],className = 'd-flex justify-content-center', id='cards')

# General Graphs
dailyBarGraph = dcc.Graph(id='daily-bar-graph',
                          config=dict(
                                        doubleClickDelay = 1,
                                        displaylogo=False,
                                        displayModeBar=False,
                                        scrollZoom=False))

totalScatterGraph = dcc.Graph(id='total-scatter-graph',
                              config=dict(displaylogo=False,
                                          displayModeBar=False,
                                          scrollZoom=False)) 

collapse = html.Div(
    [
        dbc.Button(
            "What does this Graph mean?",
            id="collapse-button",
            className="mb-3",
            color="primary",
        ),
        dbc.Collapse(
            dbc.Card(dbc.CardBody(
                                  id = 'collapse-text'),style = dict(background = const.GREY)),
            id="collapse",style = dict(textAlign = 'left')
        ),
    ],
)

EmployeeStudentGraph = html.Div([
    dcc.Graph(id='employee-student-health-pie',
              config=dict(displaylogo=False,
                          displayModeBar=False,
                          scrollZoom=False)),
    dcc.Graph(id='employee-student-total-graph',
              config=dict(displaylogo=False,
                          displayModeBar=False,
                          scrollZoom=False)),
    dcc.Graph(id='employee-student-daily-graph',
              config=dict(
                        doubleClickDelay = 1,
                        displaylogo=False,
                          displayModeBar=False,
                          scrollZoom=False)),
    html.Div(
        [
            dcc.Graph(id='employee-student-health-box',
              config=dict(displaylogo=False,
                          displayModeBar=False,
                          scrollZoom=False)),
            collapse,
        ],style = dict(textAlign = 'center') 
    ),
])


generalJumbotron = dbc.Jumbotron(
    [
        dbc.Container(
            [
                html.H1("Summary", className="display-5", style = dict(color = const.DARK_GREEN)),
                html.Hr(className="my-2"),
                html.Br(),
                html.Ul([
                    html.Li(html.H4('', id='general-overview')),
                    html.Li(html.H4('', id='general-daily-average')),
                ]),
            ],
            fluid=True,
        )
    ],
    fluid=True,
)

generalTabs = dbc.Card(
    [
        dbc.CardHeader(
            dbc.Tabs(
                [
                    dbc.Tab(label="USF Tampa", tab_id="tampa"),
                    dbc.Tab(label="USF St. Petersburg", tab_id="st-pete"),
                    dbc.Tab(label="USF Health", tab_id="health"),
                    # dbc.Tab(label="USF Sarasota-Manatee", tab_id="sarasota-manatee"),
                ],
                id="general-tabs",
                card=True,
                active_tab="tampa",
            )
        ),
        dbc.CardBody(
            html.Div([
                generalJumbotron,
                EmployeeStudentGraph
            ], className = "card-text mt-3")
        ),
    ]
)

# Main Layout
USFLayout = html.Div([
    navbar,
    alert,
    html.Div([
        cards,
    ], className='container-fluid'),
    html.Div([html.Div([
        totalScatterGraph,
        dailyBarGraph,
    ])]),
    # html.Div([tabs], style = dict( background = 'white')),
    html.Div([generalTabs], style = dict( background = 'white')),
    html.Div([
        html.H1('Data Table', id = 'table-header', style = dict(color = const.DARK_GREEN, padding = '1rem')),
        dash_table.DataTable(
            id = 'table',
            style_header={
                'backgroundColor': const.GREY,
                'fontWeight': 'bold',
                'fontSize' : '1rem',
                'color' : const.DARK_GREEN,
            },
            style_cell = dict(textAlign = 'center')
        )
    ], className = 'container-fluid w-50', style = dict(textAlign = 'center')),
    html.Footer([
        html.H5('Made by,'),
        html.Div(
            [
                html.A('Adheesh Shenoy', href = 'https://www.linkedin.com/in/adheeshenoy/', target = '__blank'),
                html.Img(src = '/assets/LI-In-Bug.png'),
            ]
        ),
        html.Div(
            [
                html.A('Rafael Flores Souza', href = 'https://www.linkedin.com/in/rafael-flores-souza/', target = '__blank'),
                html.Img(src = '/assets/LI-In-Bug.png'),
            ]
        ),
    ], id = 'footer', style = dict(borderTop =  "solid 1px white"))
])