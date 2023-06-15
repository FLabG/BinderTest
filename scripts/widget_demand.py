from IPython.display import display, clear_output
import ipywidgets as widgets
import pandas as pd

demand_data = pd.read_csv('Data/Input/Parameters/Demand.csv')

d_dict = {}


filename_input = widgets.Text(value='Demand-nuevo', description='Nombre:')
button = widgets.Button(description='Guardar cambios')

def save_changes(_):
    filename = filename_input.value.strip()
    updateCSV(filename)

button.on_click(save_changes)

for index, row in demand_data.iterrows():
    p_widget = widgets.Label(value=row['p'], layout=widgets.Layout(width='40px'))
    value_widget = widgets.FloatText(value=row['p_d'])
    d_dict[row['p']] = (p_widget, value_widget)

demand_widgets = widgets.VBox([widgets.HBox([p_widget, value_widget]) for p_widget, value_widget in d_dict.values()])

def updateCSV(filename):
    for period, (p_widget, value_widget) in d_dict.items():
        demand_data.loc[demand_data['p'] == period, 'p_d'] = value_widget.value
    filename = filename + '.csv'
    path = 'Data/Input/Parameters/' + filename
    df.to_csv(path,index=false)

update_button = widgets.Button(description='Guardar Cambios')
update_button.on_click(save_changes)

def sumar_button_clicked(_):
    rango_sumar_str = rango_sumar.value.strip()
    sumando = float(cantidad_sumar.value)
    print(rango_sumar_str)
    if rango_sumar_str:
        rango_sumar_parts = rango_sumar_str.split('-')
        period0_sumar = int(rango_sumar_parts[0].strip())
        end_period = int(rango_sumar_parts[1].strip())
        for period in range(168):
            if period0_sumar <= period <= end_period:
                d_dict['p'+str(period)][1].value += sumando
    demand_widgets = widgets.VBox([widgets.HBox([p_widget, value_widget]) for p_widget, value_widget in d_dict.values()])
rango_sumar = widgets.Text(description='Rango:', value='1-168')
cantidad_sumar = widgets.Text(description='Cantidad:', value='0')
sumar_button = widgets.Button(description='Sumar')
sumar_button.on_click(sumar_button_clicked)
sumar_widgets = widgets.HBox([sumar_button, rango_sumar, cantidad_sumar])


def multiplicar_button_clicked(_):
    rango_multiplicar_str = rango_multiplicar.value.strip()
    factor = float(cantidad_multiplicar.value)
    print(rango_multiplicar_str)
    if rango_multiplicar_str:
        rango_multiplicar_parts = rango_multiplicar_str.split('-')
        period0_multiplicar = int(rango_multiplicar_parts[0].strip())
        periodf_multiplicar = int(rango_multiplicar_parts[1].strip())
        for period in range(168):
            if period0_multiplicar <= period <= periodf_multiplicar:
                d_dict['p'+str(period)][1].value *= factor
    demand_widgets = widgets.VBox([widgets.HBox([p_widget, value_widget]) for p_widget, value_widget in d_dict.values()])
rango_multiplicar = widgets.Text(description='Rango:', value='1-168')
cantidad_multiplicar = widgets.Text(description='Cantidad:', value='0')
multiplicar_button = widgets.Button(description='Multiplicar')
multiplicar_button.on_click(multiplicar_button_clicked)
multiplicar_widgets = widgets.HBox([multiplicar_button, rango_multiplicar, cantidad_multiplicar])






filename_input = widgets.Text(value='Demand-nuevo', description='Nombre:')

guardar_widgets = widgets.HBox([button, filename_input])



display(widgets.VBox([guardar_widgets,sumar_widgets,multiplicar_widgets, demand_widgets,guardar_widgets,sumar_widgets,multiplicar_widgets]))
# display(sumar_widgets )