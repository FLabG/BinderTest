
import ipywidgets as widgets
import pandas as pd

def updateCSV(df, filename):
    for column in range(len(df.columns)):
        for row in range(1, len(df)):
            widget = grid_list[column][row]
            new_value = widget.value
            df.iloc[row, column] = new_value
    df = df.transpose()
    df = df.set_index(df.columns[0])
    df.columns = df.iloc[0]
    df = df[1:]
    df.index.name = 'g'
    filename = filename + '.csv'
    path = 'Data/Input/Parameters/' + filename
    df.to_csv(path)

global data
data = pd.read_csv('Data/Input/Parameters/Generators.csv')
data = data.transpose()
data = data.reset_index()

container = widgets.GridBox(layout=widgets.Layout(grid_template_columns="repeat(auto-fit, minmax(60px, 90px))"))

g_names = data.iloc[0].tolist()
p_names = data.iloc[:, 0].tolist()
p_labels = [widgets.Label(value=name) for name in p_names]

container.children += tuple(p_labels)

grid_list = []

for column in range(len(data.columns)):
    if column == 0:
        g_name = 'Parameters'
    else:
        g_name = g_names[column]

    g_widget = [widgets.Label(value=g_name)]

    for row in range(1, len(data)):
        p_value = data.iloc[row, column]

        try:
            value = float(p_value)
            widget = widgets.FloatText(value=value, layout=widgets.Layout(width='auto'))
        except ValueError:
            widget = widgets.Label(value=p_value)

        g_widget.append(widget)

    grid_list.append(g_widget)

container.children = [widgets.VBox(children=row) for row in grid_list]

filename_input = widgets.Text(value='Generators-nuevo', description='Nombre:')
button = widgets.Button(description='Guardar cambios')

def save_changes(_):
    filename = filename_input.value.strip()
    updateCSV(data, filename)

button.on_click(save_changes)

display(widgets.VBox([container, button, filename_input]))