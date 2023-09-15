from flask import Flask, render_template, request
import pandas as pd
from datetime import date
import webbrowser  # Importar la biblioteca webbrowser

app = Flask(__name__)

# Variable global para el mensaje de error
mensaje_error_text = ""

@app.route("/", methods=["GET", "POST"])
def index():
    global mensaje_error_text

    if request.method == "POST":
        codigo_buscar = request.form["codigo"]
        codigo_buscar = str(codigo_buscar)

        # Cargar el archivo CSV en un DataFrame
        url_hoja = "https://docs.google.com/spreadsheets/d/1-ZrhfR9VFIuZyBpBNNWp5JArNRZzy-ldJ1w1As4VG2c"
        nombre_hoja = "INICIO"
        url_csv = f"{url_hoja}/gviz/tq?tqx=out:csv&sheet={nombre_hoja}"
        df = pd.read_csv(url_csv, header=11)

        # Cambia el nombre a columnas sin nombre y elimina columnas vacías
        df.rename(columns={'Unnamed: 0': 'Fecha'}, inplace=True)
        df.rename(columns={'Unnamed: 2': 'Clave catastral'}, inplace=True)
        df.rename(columns={'Unnamed: 11': 'TIEMPO DIAS'}, inplace=True)
        
        # Elimina columnas vacías
        columnas_a_eliminar = [f'Unnamed: {i}' for i in range(12, 23)]

        for columna in columnas_a_eliminar:
            if columna in df.columns:
                df.drop(columns=[columna], inplace=True)

        df['Nro_Tramite'] = df['Nro_Tramite'].astype(str)

        # Buscar el código en el DataFrame
        filtro = df[df['Nro_Tramite'] == codigo_buscar]

        # Actualizar el mensaje de error
        if filtro.empty:
            mensaje_error_text = "No existe el trámite"
        else:
            mensaje_error_text = ""  # Limpiar el mensaje de error si no es necesario

            # Ordenar el DataFrame por la columna 'Fecha' de manera ascendente
            pd.options.mode.chained_assignment = None
            filtro['Fecha'] = pd.to_datetime(filtro['Fecha'], format='%d/%m/%Y')
            filtro = filtro[::-1].reset_index(drop=True)

            filtro['Fecha'] = pd.to_datetime(filtro['Fecha'])
            result_df = filtro.reset_index(drop=True)

            # Calcular los tiempos para las filas excepto la última
            for i in range(len(result_df) - 1):
                result_df.loc[i, 'TIEMPO DIAS'] = (result_df['Fecha'][i + 1] - result_df['Fecha'][i]).days

            # Calcular el tiempo para la última fila usando la Fecha actual
            current_date = pd.Timestamp(date.today())
            result_df.loc[len(result_df) - 1, 'TIEMPO DIAS'] = (current_date - result_df['Fecha'][len(result_df) - 1]).days
            
            # Formatear la columna Fecha
            result_df['Fecha'] = result_df['Fecha'].dt.strftime('%Y-%m-%d')

            # Convertir los resultados a un formato que se puede pasar a la plantilla HTML
            resultados = result_df.to_dict(orient='records')
            return render_template("index.html", mensaje_error=mensaje_error_text, resultados=resultados)

    return render_template("index.html", mensaje_error=mensaje_error_text)

if __name__ == "__main__":
    # Abrir automáticamente el navegador en http://127.0.0.1:5000
    webbrowser.open("http://127.0.0.1:5000")
    
    # Ejecutar la aplicación Flask
    app.run(debug=True)