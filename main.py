from IPython.display import clear_output,display

clear_output(wait=True)
import ipywidgets as widgets

# modificar_datos_label = widgets.Label(value='Modificar Datos')
global accordion
modificar_datos_opciones = ['Seleccionar Datos','Generadores', 'Demanda']

dropdown = widgets.Dropdown(options=modificar_datos_opciones)

def on_option_selected(change):
    selected_option = change.new
    if selected_option == 'Generadores':
      clear_output()
      display(accordion)
      %run scripts/widget_generators.py
    if selected_option == 'Demanda':
      clear_output()
      display(accordion)
      %run scripts/widget_demand.py

dropdown.observe(on_option_selected, names='value')

# modificar_datos_container = widgets.VBox([modificar_datos_label,dropdown], layout=widgets.Layout(border = '2px solid lightgrey', padding='5px'))
# modificar_datos_container.layout.width = '500px'

# dropdown.layout = widgets.Layout(border = '2px solid lightgrey', padding='10px')
# dropdown.layout.width = '500px'
modificar_datos_container = widgets.VBox([dropdown],layout=widgets.Layout(border = '2px solid lightgrey', padding='5px') )
modificar_datos_container.layout.width = '500px'

resolver_button = widgets.Button(description = 'Resolver')
resolver_container = widgets.VBox([resolver_button],layout=widgets.Layout(border = '2px solid lightgrey', padding='5px'))
resolver_container.layout.width = '500px'

def on_resolver_button_clicked(_):
  %run scripts/solver.py
resolver_button.on_click(on_resolver_button_clicked)

representar_resultados_label = widgets.Label(value='Representar Resultados')
representar_resultados_opciones = ['Generación','Reservas']


checkbox_nuclear = widgets.Checkbox(description='Nuclear',value=True)
checkbox_lignite = widgets.Checkbox(description='Lignite',value=True)
checkbox_subbitumin = widgets.Checkbox(description='Subbitumin',value=True)
checkbox_bituminous = widgets.Checkbox(description='Bituminous',value=True)
checkbox_anthracite = widgets.Checkbox(description='Anthacite',value=True)
checkbox_CCGT = widgets.Checkbox(description='CCGT',value=True)
checkbox_fueloil = widgets.Checkbox(description='Fuel oil',value=True)
checkbox_gas = widgets.Checkbox(description='Gas',value=True)
checkbox_hydrores = widgets.Checkbox(description='Reservoir',value=True)
checkbox_hydroror = widgets.Checkbox(description='Run-of-River',value=True)
checkbox_hydropum = widgets.Checkbox(description='Pump',value=True)
checkbox_solar = widgets.Checkbox(description='Solar',value=True)
checkbox_wind = widgets.Checkbox(description='Wind',value=True)
checkbox_pns = widgets.Checkbox(description='PNS',value=True)
checkbox_demand = widgets.Checkbox(description='Demand',value=True)

checkbox_widget = widgets.VBox([
    widgets.HBox([checkbox_nuclear, checkbox_lignite, checkbox_subbitumin]),
    widgets.HBox([checkbox_bituminous, checkbox_anthracite, checkbox_CCGT]),
    widgets.HBox([checkbox_fueloil, checkbox_gas, checkbox_hydrores]),
    widgets.HBox([checkbox_hydroror, checkbox_hydropum, checkbox_solar]),
    widgets.HBox([checkbox_wind, checkbox_pns, checkbox_demand])
])

plot_gen_button = widgets.Button(description='Crear Plot')

def on_gen_button_clicked(_):
    checked_indexes = [index for index, checkbox in enumerate([
        checkbox_nuclear, checkbox_lignite, checkbox_subbitumin,
        checkbox_bituminous, checkbox_anthracite, checkbox_CCGT,
        checkbox_fueloil, checkbox_gas, checkbox_hydrores,
        checkbox_hydroror, checkbox_hydropum, checkbox_solar,
        checkbox_wind, checkbox_pns, checkbox_demand
    ]) if checkbox.value]
    # print(checked_indexes)
    generation_df = pd.read_csv('Data/Output/Generation.csv', index_col = 0)
    demand_df = pd.read_csv('Data/Output/Demand.csv', index_col = 0)
    merged_df = pd.merge(generation_df, demand_df, left_index=True, right_on='Period')

    selected_cols = [merged_df.columns[index] for index in checked_indexes]
    plot_df = merged_df[selected_cols]
    plot_df.plot(kind='area', stacked = False, linewidth=0)
plot_gen_button.on_click(on_gen_button_clicked)


def cerrar_plots():
  clear_output()
  display(accordion)
cerrar_plots_button = widgets.Button(description='Cerrar Plots')
cerrar_plots_button.on_click(lambda _: cerrar_plots())

gen_box = widgets.VBox([checkbox_widget,plot_gen_button, cerrar_plots_button])

reserva_res = widgets.Checkbox(description='Reservoir',value=True)
reserva_pum = widgets.Checkbox(description='Pump',value=True)
plot_reserva_button = widgets.Button(description='Crear Plot')

def on_plot_reserva_button_clicked(_):
    selected_checkboxes = []
    if reserva_res.value:
        selected_checkboxes.append('reserva_res')
    if reserva_pum.value:
        selected_checkboxes.append('reserva_pum')
    print('Selected Checkboxes:', selected_checkboxes)
plot_reserva_button.on_click(on_plot_reserva_button_clicked)
reserva_buttons = widgets.VBox([plot_reserva_button, cerrar_plots_button])
reserva_box = widgets.VBox([reserva_res, reserva_pum, reserva_buttons])

plot_accordion = widgets.Accordion(children = [gen_box, reserva_box])
plot_accordion.set_title(0,'Generación')
plot_accordion.set_title(1,'Reservas')


accordion = widgets.Accordion(children = [modificar_datos_container,resolver_container,plot_accordion])
accordion.set_title(0,'Modificar Datos')
accordion.set_title(1,'Resolver')
accordion.set_title(2,'Ver Resultados')
display(accordion)
