import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.figure_factory as ff
from dash.dependencies import Input, Output, State, Event
import datetime

### ------------------- ###

app = dash.Dash()
app.config.supress_callback_exceptions=True  # fix for slider's id

data = pd.read_csv('data/bdcuentas.csv')
categories = pd.read_csv('data/categories.csv')
percentages = pd.read_csv('data/percentages.csv')
months = ['Enero','Febrero','Marzo', 'Abril','Mayo','Junio','Julio',
		'Agosto','Septiembre','Octubre','Noviembre','Diciembre']

i = datetime.datetime.now() 

def total(data):
	return data.groupby('category').sum()

#data actual
data_ac = data[data['month']==months[(i.month)-1].lower()]
perc_ac = percentages[percentages['month']==months[(i.month)-1].lower()]

app.layout = html.Div([
	html.Div([html.H2("Budget Control App"),], className='banner'),	
	
	html.Div(children=[
		html.Div([
			# Elegir el mes para ver
			dcc.Dropdown(id='actual-month',
			    options=[{'label': s, 'value': s.lower()} for s in months],	    
			    value=months[(i.month)-1].lower()
				),
			# Sliders interactivo para los porcentajes de las categorías
			html.Div([html.Div(id='perc-slider-div')], style={'marginLeft': '10px'}),
	
			html.Div([
		      		html.Button('Guardar Estado', type='button', id='save-perc-btn'),
		      		html.Div(id='saved-msg')
		      		], style={"text-align":"center"})			

		], className='three columns wind-histogram'),
		
		# Gráfico del estado actual
	 	html.Div([
	 		#html.Div([dcc.Graph(id='totales')
	 		html.Div([dcc.Graph(id='totales')
	 		],style={'width': '50%','position':'center', 'left': '50%', 'margin':'0 auto', 'display': 'inline-block', 'padding': '0 20', 'text-align':'center'}),
	 		dcc.Graph(id='current-status')
	 		#, className='four columns wind-histogram', style={"text-align":"center"})
		], className='nine columns wind-histogram')
 	], className='row wind-speed-row'),

 	# Segunda fila
    html.Div([
     # tabla de resumen
	    html.Div(children=[
	    	html.Div([html.H3("Resumen")], className='Title'),
		    html.Div(id='summary')
		], className='six columns wind-histogram'),

	    # Formulario para nueva entrada
	  	html.Div(children=[
	      # content
		    html.Div(children=[html.Div([
		            html.H3("Nuevo movimiento")
		        ], className='Title'),
		      # form
		      	html.Form(id='mov-form', children=[			       
		      		html.Div([
		      			html.Div([		      				
		      				html.P("Monto: "), 
		      				dcc.Input(type='text', id='in-monto', placeholder='monto', value=''),

		      				html.P("Categoría: "),
		      				dcc.Dropdown(id='drop-cat', value='')

		      			], className='six columns wind-histogram'),

		      			html.Div([
		      				html.P('Tipo: '),
		      				dcc.RadioItems(id='radio-tipo',
			                               options=[{'label': 'Gasto', 'value': 'egreso'},
			                                        {'label': 'Ingreso', 'value': 'ingreso'}],
			                               value='egreso', labelStyle={'display': 'inline-block'}),

		      				html.P("Detalles: "), 
		      				dcc.Textarea(id='details', placeholder='Detalles de la compra...',
			                                value='sin detalles', style={'width': '100%'})
		      			], className='six columns wind-histogram'),

		      			html.Br(),
		      			html.Div([
		      				html.Button('Guardar', type='button', id='save-btn', form='mov-form')
		      			], style={"text-align":"center"})
		      		])
		        ],)
		      ],) 
		    ], className='six columns wind-histogram')
  	], className='row wind-speed-row'),
  
    # tabla de transacciones    
    html.Div(id='div-trans',children=[
	    html.Div([html.H3("Últimos movimientos del mes")], className='Title'),
	    html.Div(dcc.Graph(id='trans-table'))
	    #html.Div(id='transactions')
    ], className='row wind-speed-row'),

	##hidden div for current data
	html.Div(id='json_month_data',style={'display':'none'}),
	html.Br(),

    ## hidden div for data updating
    #html.Div(id='dataupdate', style={'display': 'none'}),
    html.Div(id='json_current_data',style={'display':'none'}),
	html.Br(),
    # para el porcentaje
    html.Div(id='json_month_perc',style={'display':'none'}),
    html.Br(),
    html.Div(id='json_current_perc',style={'display':'none'}),

    # div oculto para la primera instancia de datos mensuales
    #html.Div(id='json_month'),

], style={'padding': '0px 10px 15px 10px',
          'marginLeft': 'auto', 'marginRight': 'auto', "width": "1300px",
          'boxShadow': '0px 0px 5px 5px rgba(204,204,204,0.4)'}
)

# Selección interactiva de categorías para el tipo de movimiento
@app.callback(
	Output('drop-cat', 'options'),
	[Input('radio-tipo', 'value')]
)
def cat_select_drop(radio_value):
	cat = list(categories[categories.type==radio_value].categories)
	return [{'label': s.title(), 'value': s} for s in cat]

# datos iniciales del mes
@app.callback(
	Output('json_month_data','children'),
	[Input('actual-month','value')],
	)
def choose_data(month):
	month_data = data[data.month==month]
	month_data.index = np.arange(len(month_data))
	return month_data.to_json()

# porcentajes iniciales del mes
@app.callback(
	Output('json_month_perc','children'),
	[Input('actual-month','value')],
	)
def choose_perc(month):
	month_perc = percentages[percentages.month==month]
	return month_perc.to_json()
			 
# generar lista de sliders de porcentajes
@app.callback(
	Output('perc-slider-div', 'children'),
	[Input('json_month_perc', 'children')]
	)
def perc_list(json_perc): 
	actual_perc = pd.read_json(json_perc)
	actual_perc = actual_perc.sort_values('category')
	actual_perc.index = np.arange(len(actual_perc))
	
	l = []
	for i in range(len(actual_perc)):
		l = l + [
			html.P(actual_perc.category.iloc[i].title()),
			dcc.Slider(id=actual_perc.category.iloc[i][:4],
				min=0,
			    max=10,
			    marks={i: (i*10) for i in range(11)},
			    value=float(actual_perc.percentage.iloc[i]/10),
			    updatemode='mouseup'),
			html.Br()]
	return l

# actualizar datos
@app.callback(
	Output('json_current_data', 'children'), 
	[Input('save-btn', 'n_clicks'),	Input('json_month_data', 'children')],
	state=[
		State('json_current_data', 'children'),
		State('in-monto', 'value'),	State('actual-month', 'value'),
		State('radio-tipo', 'value'), State('drop-cat', 'value'),
		State('details', 'value')]
	)
def current_data(n_clicks, json_month_data, json_cur_data,
				 monto, month, tipo, cat, details):
	if n_clicks == None:
		cur_data = pd.read_json(json_month_data).sort_index(axis=0)
	else:
		cur_data = pd.read_json(json_cur_data).sort_index(axis=0)
		
	cur_data = cur_data[data.columns]
	
	if monto != '' and cat != '':
		newmov = [(i.day, month, i.year, monto, cat, tipo, details)]
		nm = pd.DataFrame.from_records(newmov, columns=cur_data.columns.values) 
		# agregando el nuevo movimiento al final de la tabla de datos del mes
		cur_data = pd.concat([cur_data, nm],ignore_index=True)

		# guardando en el archivo
		nm.to_csv('data/bdcuentas.csv', mode='a', header=False, index=False)

	return cur_data.to_json()


#actualizar tabla cuando se actualicen los valores con nuevos movimientos
@app.callback(
	Output('trans-table', 'figure'), 
	[Input('json_current_data', 'children')]
)
def update_table(json_cur_data):
	df = pd.read_json(json_cur_data).sort_index(axis=0)
	df = df.tail(min(len(df), 15))	
	df = df[data.columns]
	df = df.sort_index(ascending=False)
	
	return ff.create_table(df, colorscale=[[0, '#42C4F7 '],[.5, '#f2e5ff'],[1, '#ffffff']])

# actualizar los porcentajes
@app.callback(
	Output('json_current_perc', 'children'), 
	[Input('ahor','value'),	Input('alim','value'),
	Input('impr','value'), 	Input('otro','value'),
	Input('tran','value'), 	Input('vivi','value')],
	state=[State('json_current_perc','children'),
			State('json_month_perc', 'children')]
)
def current_perc(ahor, alim, impr, otro, tran, vivi, json_cur_perc, json_month_perc):
	if json_cur_perc == None:
		cur_perc = pd.read_json(json_month_perc).sort_values('category')
	else:
		cur_perc = pd.read_json(json_cur_perc).sort_values('category')
		# actualizando porcentajes
		cur_perc.percentage = (ahor*10, alim*10, impr*10, otro*10, tran*10, vivi*10)
		
	cur_perc.index = np.arange(len(cur_perc))
	return cur_perc.to_json() 


# Guardar los porcentajes nuevos
@app.callback(
	Output('saved-msg','children'),
	[Input('save-perc-btn', 'n_clicks')],
	state=[State('json_current_perc','children')]
	)
def permanent_perc(n_clicks, json_current_perc):
	# porcentajes completos de todos los meses
	global_perc = percentages.copy()
	# porcentages actuales (mes y estado actual de sliders)
	cur_perc = pd.read_json(json_current_perc).sort_values('category')  
	# indices del global que coinciden con el mes actual
	indexes = global_perc[global_perc.month.isin(cur_perc.month.iloc[0])].index
	#indexes = global_perc[global_perc.month==cur_perc.month.iloc[0]].index
	# reescribir los datos del mes con los actuales
	global_perc.loc[indexes] = [cur_perc.category.values, cur_perc['month'][0],
								cur_perc.percentage.values]
	# escribir en el archivo csv
	try:
		global_perc.to_csv('data/percentages.csv', index=False)
		return "Porcentajes fijados!"
	except:
		return "No se pudo guardar! Intenta otra vez."
	
#actualización de la tabla de resumen
@app.callback(
	Output('summary', 'children'),
	[Input('json_current_perc', 'children'),
	Input('json_current_data', 'children')],
	state= [State('json_month_perc', 'children'),
		State('json_month_data', 'children')]
	)
def update_summary(json_perc, json_data, month_perc, month_data):
	if json_perc == None:
		p = pd.read_json(month_perc)
	else: 
		p = pd.read_json(json_perc)
	if json_data == None:
		d = pd.read_json(month_data)
	else:
		d = pd.read_json(json_data)
		
	p = p.sort_values('category', ascending=True)
	p.index = np.arange(len(p))
	d = d.sort_index()
	
	# totales por categoría
	intotal = total(d[d.type=='ingreso']).amount.sum()
	egtotal = total(d[d.type=='egreso'].loc[:,['amount','category']]) # gastos 

	# ahorro aparte
	ahorro = p[p.category=='ahorro']
	ahorro = pd.concat([ahorro,
				pd.DataFrame({'lim': ahorro['percentage']* intotal / 100})],
				axis = 1)

	# porcentajes sin ahorro
	perc = p[p.category!='ahorro'].sort_values('category')
		
	# limites del presupuesto por categorias
	limites = round(perc.percentage*intotal / 100,2)
	limites = pd.DataFrame(limites)
	limites.columns = ['limite']

	if len(egtotal) != len(perc):
		for cat in perc.category:
			if cat in egtotal.index.values:
				continue
			else:
				egtotal.loc[cat] = 0
				
	egtotal = egtotal.sort_index(axis=0)
	limites.index = egtotal.index
	
	
	# presupuesto sobrante 
	sobrante = round(limites.limite - egtotal.amount,2)
	sobrante = pd.DataFrame(sobrante, columns=['sobrante'])
	
	# exceso
	exceso = pd.DataFrame([0 if i > 0 else i*(-1) for i in sobrante.sobrante],	
			index=egtotal.index, columns=['exceso'])
	

	perc = pd.DataFrame(perc, columns=['percentage'])
	perc.index = egtotal.index
	cat = pd.DataFrame(perc.index.values, index=perc.index, columns=['categoría'])
	
	# tabla resumen
	tabla = pd.concat([cat, egtotal, perc, limites, sobrante, exceso], axis=1)
	tabla.colums = [i.title() for i in list(tabla.columns.values)]
	tabla.index = np.arange(len(tabla))
	

	dtotal = {'Ingresos': [intotal], 'Ahorro': [ahorro.lim[0]],
	 		 'Gastos': [egtotal.amount.sum()], 
	 		 'Disponible': [sobrante.sobrante.sum()]}
	tabla_totales = pd.DataFrame.from_dict(dtotal)
	tabla_totales = tabla_totales[['Ingresos','Ahorro','Gastos', 'Disponible']]
	
	return [
		dcc.Graph(id='summary-table', figure=ff.create_table(tabla, colorscale=[[0, '#42C4F7 '],[.5, '#f2e5ff'],[1, '#ffffff']])),
		html.Div(id='json_summary', children=tabla.to_json(), style={'display':'none'}),
		html.Div(id='json_totales', style={'display':'none'}, children=tabla_totales.to_json())
		]

#Imprimir tabla de totales
@app.callback(
	Output('totales','figure'),
	[Input('json_totales','children')]
	)
def cur_totales(json_totales):
	#df = pd.read_json(json_totales)

	tabla_res = ff.create_table(pd.read_json(json_totales), colorscale=[[0, '#42C4F7 '],[.5, '#f2e5ff'],[1, '#ffffff']])

	for i in range(len(tabla_res.layout.annotations)):
		tabla_res.layout.annotations[i].font.size = 20
		#tabla_res.layout.annotations[i].font.color ='blue'

	return tabla_res
    


	#return ff.create_table(pd.read_json(json_totales), colorscale=[[0, '#42C4F7 '],[.5, '#f2e5ff'],[1, '#ffffff']])

# Actualizar gráfico
@app.callback(
    Output('current-status', 'figure'),
    [Input('json_summary','children')]
)
def update_graph(summary):
    d = pd.read_json(summary).sort_index(axis=0, ascending=False)
    exc = [value*(-1) if value < 0 else 0 for value in d.sobrante]   
    aux = [limite if gasto > limite else gasto for gasto, limite in zip(d.amount, d.limite)]
    disp = [0 if value < 0 else value for value in d.sobrante]
    cat = [i.title() for i in d['categoría']]

    gasto = go.Bar(y=cat, x=aux, name='Gasto', orientation='h',
        marker=dict(color='rgb(66,196,247)'))
    limite = go.Bar(y=cat, x=disp, name='Presupuesto', orientation='h',
        marker=dict(color='rgb(33,183,33)'))
    exceso = go.Bar(y=cat, x=exc, name='Exceso', orientation='h',
        marker=dict(color='rgb(255,51,51)'))

    return go.Figure(data=[gasto, limite, exceso], layout=go.Layout(barmode='stack'))

#### init server #####
external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/737dc4ab11f7a1a8d6b5645d26f69133d97062ae/dash-wind-streaming.css",
                "https://fonts.googleapis.com/css?family=Raleway:400,400i,700,700i",
                "https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i"]
for css in external_css:
    app.css.append_css({"external_url": css})

if __name__ == '__main__':
    app.run_server()
