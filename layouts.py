import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import constants as const

# Navigation Bar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Overview", href="#", external_link=True)),
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
    id = 'navigation',
    dark=True,
    brand_style=dict(fontSize=30),
    style=dict(position='sticky',
               top=0,
               zIndex=99,
               borderBottom="solid 1px white"))

# Alert
alert = html.Div([
    dbc.Alert(
            "Disclaimer: The purpose of this website is only to present the COVID-19 data on the USF Campuses. We do not take ownership of the data as it was acquired from the USF Coronavirus website.",
            id="alert-fade",
            dismissable=True,
            is_open=True,
            style = dict(color = 'black',background = const.LIGHT_GOLD, padding = '1rem', margin = '0.5rem')
        )
])

# Popover for graphs
tampaCollapse = html.Div(
    [
        dbc.Button(
            "What does this Graph mean?",
            id="tampa-collapse-button",
            className="mb-3",
            color="primary",
        ),
        dbc.Collapse(
            dbc.Card(dbc.CardBody("Tampa collapse")),
            id="tampa-collapse",
        ),
    ]
)

stPeteCollapse = html.Div(
    [
        dbc.Button(
            "What does this Graph mean?",
            id="st-pete-collapse-button",
            className="mb-3",
            color="primary",
        ),
        dbc.Collapse(
            dbc.Card(dbc.CardBody("St pete collapse")),
            id="st-pete-collapse",
        ),
    ]
)

# Card overview
# Tampa Card layout
tampaCardContent = [
    dbc.CardHeader(html.H4("Tampa Campus"),style = dict(background = const.GREY, color = const.DARK_GREEN)),
    dbc.CardBody([
        html.H5("Total Cases", className="card-title"),
        html.H6(
            "",
            id='tampa-card-totalcases',
            className="card-text",
        ),
        html.H6(
            "",
            id='tampa-card-health-totalcases',
            className="card-text",
        ),
        html.H5("Latest update", className="card-title"),
        html.H6(
            "",
            id='tampa-card-update',
            className="card-text",
        ),
    ], style = dict(background = 'white', color = 'black')),
]

# St. Pete card layout
stPeteCardContent = [
    dbc.CardHeader(html.H4("St. Petersburg Campus"),  style = dict(background = const.GREY, color = const.DARK_GREEN)),
    dbc.CardBody([
        html.H5("Total Cases", className="card-title"),
        html.H6(
            "",
            id='st-pete-card-totalcases',
            className="card-text",
        ),
        html.H5("Latest update", className="card-title"),
        html.H6(
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
            dbc.Col(dbc.Card(stPeteCardContent, style = dict(color = 'black')),
                    className='col-sm')
        ],
        className="mb-4",
        align = "stretch",
        style = dict(marginTop = '2rem')
    )
],className = 'd-flex justify-content-center', id='cards')

# General Graphs
dailyBarGraph = dcc.Graph(id='daily-bar-graph',
                          config=dict(displaylogo=False,
                                      displayModeBar=False,
                                      scrollZoom=False))

totalScatterGraph = dcc.Graph(id='total-scatter-graph',
                              config=dict(displaylogo=False,
                                          displayModeBar=False,
                                          scrollZoom=False))

# Tab Contents
# Tampa tab contents
tampaEmployeeStudentGraph = html.Div([
    dcc.Graph(id='tampa-employee-student-health-pie',
              config=dict(displaylogo=False,
                          displayModeBar=False,
                          scrollZoom=False)),
    html.Div(
        [
            tampaCollapse,
            # tampaBoxGraphPopover,
            dcc.Graph(id='tampa-employee-student-health-box',
              config=dict(displaylogo=False,
                          displayModeBar=False,
                          scrollZoom=False)),
        ]
    ),
    dcc.Graph(id='tampa-employee-student-total-graph',
              config=dict(displaylogo=False,
                          displayModeBar=False,
                          scrollZoom=False)),
    dcc.Graph(id='tampa-employee-student-daily-graph',
              config=dict(displaylogo=False,
                          displayModeBar=False,
                          scrollZoom=False)),
])

# Tampa Jumbotron
tampaJumbotron = dbc.Jumbotron(
    [
        dbc.Container(
            [
                html.H1("Summary", className="display-3", style = dict(color = const.DARK_GREEN)),
                html.Hr(className="my-2"),
                html.Br(),
                html.Ul([
                    html.Li(html.H4('', id='tampa-overview')),
                    html.Li(html.H4('', id='health-overview')),
                    html.Li(html.H4('', id='tampa-daily-average')),
                ]),
            ],
            fluid=True,
        )
    ],
    fluid=True,
)

# Tampa Tab Layout
tampaTab = dbc.Card(dbc.CardBody([tampaJumbotron, tampaEmployeeStudentGraph]),
                    className="mt-3")

# St. Pete Tab layout
stPeteEmployeeStudentGraph = html.Div([
    dcc.Graph(id='st-pete-employee-student-health-pie',
              config=dict(displaylogo=False,
                          displayModeBar=False,
                          scrollZoom=False)),
    html.Div(
        [
            # stPeteBoxGraphPopover,
            stPeteCollapse,
            dcc.Graph(id='st-pete-employee-student-health-box',
              config=dict(displaylogo=False,
                          displayModeBar=False,
                          scrollZoom=False)),
        ]
    ),
    dcc.Graph(id='st-pete-employee-student-total-graph',
              config=dict(displaylogo=False,
                          displayModeBar=False,
                          scrollZoom=False)),
    dcc.Graph(id='st-pete-employee-student-daily-graph',
              config=dict(displaylogo=False,
                          displayModeBar=False,
                          scrollZoom=False)),
])

# St. Pete Jumbotron
stPeteJumbotron = dbc.Jumbotron(
    [
        dbc.Container(
            [
                html.H1("Summary", className="display-3", style = dict(color = const.DARK_GREEN)),
                html.Hr(className="my-2"),
                html.Br(),
                html.Ul([
                    html.Li(html.H4('', id='st-pete-overview')),
                    html.Li(html.H4('', id='st-pete-daily-average')),
                ])
            ],
            fluid=True,
        )
    ],
    fluid=True,
)

# St Pete tab layout
stPeteTab = dbc.Card(dbc.CardBody(
    [stPeteJumbotron, stPeteEmployeeStudentGraph]),
                     className="mt-3")

# Tab creation
tabs = dbc.Tabs(
    [
        dbc.Tab(tampaTab,
                label="USF Tampa Campus",
                label_style={"color": const.DARK_GREEN},
                tab_id='tampa-tab'),
        dbc.Tab(stPeteTab,
                label="USF St. Petersburg Campus",
                label_style={"color": const.DARK_GREEN},
                tab_id='st-pete-tab'),
    ],
    id='campus-tabs',
    active_tab="tampa-tab",
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
    html.Div([tabs]),
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
        html.H5('Made by'),
        html.Div(
            [
                html.A('Adheesh Shenoy', href = 'https://www.linkedin.com/in/adheeshenoy/', target = '__blank'),
                html.Img(src = '/assets/LI-In-Bug.png'),
            ]
        ),
        # html.H6('&'),
        html.Div(
            [
                html.A('Rafael Flores Souza', href = 'https://www.linkedin.com/in/rafael-flores-souza/', target = '__blank'),
                html.Img(src = '/assets/LI-In-Bug.png'),
            ]
        ),
    ], id = 'footer')
])