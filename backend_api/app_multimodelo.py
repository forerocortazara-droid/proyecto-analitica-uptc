import os
import pandas as pd
import joblib
from flask import Flask, request, jsonify

app = Flask(__name__)

# Diccionario para guardar en memoria los modelos que se vayan cargando
model_assets_cache = {}

def load_model_assets(faculty_name):
    """
    Busca de forma inteligente el archivo .pkl usando la palabra clave de la facultad.
    """
    # Pasamos a mayúsculas y cambiamos espacios por guiones bajos
    search_term = faculty_name.strip().upper().replace(" ", "_")
    
    if search_term in model_assets_cache:
        return model_assets_cache[search_term]

    # Escaneamos la carpeta y guardamos los nombres de archivos .pkl
    pkl_files_in_folder = [file for file in os.listdir('.') if file.endswith('.pkl')]

    # Sacamos la palabra clave principal (quitando "FACULTAD_DE_" si viene en el texto)
    keyword = search_term.replace("FACULTAD_DE_", "")

    filename_model = None
    for file in pkl_files_in_folder:
        # Buscamos si la palabra clave (ej: "INGENIERIA" o "CIENCIAS_DE_LA_EDUCACION") está en el archivo
        if keyword in file.upper():
            filename_model = file
            break

    # Si no lo encuentra, nos avisa qué archivos sí hay
    if not filename_model:
        raise ValueError(
            f"La API busca un archivo que contenga '{keyword}'. "
            f"Pero en tu carpeta actual SOLO existen estos archivos .pkl: {pkl_files_in_folder}"
        )
    
    try:
        model = joblib.load(filename_model)
        columns_order = model.feature_names_in_.tolist()
        model_assets_cache[search_term] = {
            'model': model,
            'columns_order': columns_order
        }
        return model_assets_cache[search_term]
    except Exception as e:
        raise ValueError(f"Error al cargar '{filename_model}': {str(e)}")
       
def preprocess_data(raw_data, columns_order):
    """
    Toma al estudiante y lo alinea perfectamente con la estructura del modelo cargado.
    """
    df_input = pd.DataFrame([raw_data])
    
    numeric_cols = ['ESTRATO', 'FORANEO', 'JOVEN', 'PROMEDIO_HISTORICO_SEDE']
    for col in numeric_cols:
        if col in df_input.columns:
            df_input[col] = pd.to_numeric(df_input[col], errors='coerce')
            
    categorical_cols = ['PERIODO', 'JORNADA', 'MODALIDAD', 'NOMBRE_SEDE', 'GENERO', 'ORIGEN_GEOGRAFICO']
    df_processed = pd.get_dummies(df_input, columns=[col for col in categorical_cols if col in df_input.columns])
    
    # Creamos la plantilla con las columnas exactas que este modelo en particular exige
    df_final = pd.DataFrame(0, index=[0], columns=columns_order)
    
    for col in df_final.columns:
        if col in df_processed.columns:
            df_final[col] = df_processed[col].values[0]
        elif col in numeric_cols and col in df_input.columns:
            df_final[col] = df_input[col].values[0]
        else:
            df_final[col] = 0

    return df_final

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'estado': 'Fallo', 'error': 'No se recibieron datos JSON'}), 400
            
        # OBLIGATORIO: Ahora la petición debe decir a qué facultad pertenece el estudiante
        faculty = data.get('FACULTAD')
        if not faculty:
            return jsonify({'estado': 'Fallo', 'error': 'El campo "FACULTAD" es obligatorio.'}), 400
        
        # Cargar el modelo correcto de forma dinámica
        try:
            assets = load_model_assets(faculty)
        except ValueError as ve:
            return jsonify({'estado': 'Fallo', 'error': str(ve)}), 400
            
        model = assets['model']
        columns_order = assets['columns_order']
        
        # Preprocesar con el orden de este modelo
        df_features = preprocess_data(data, columns_order)
        
        # Predicción y cálculo de probabilidades
        prediccion = int(model.predict(df_features)[0])
        probabilidades = model.predict_proba(df_features)[0]
        prob_riesgo = float(probabilidades[1]) * 100
        
        perfil = "Alto Riesgo" if prediccion == 1 else "Bajo Riesgo / Estable"
        recomendacion = (
            "Se sugiere remitir a tutorías prioritarias, acompañamiento por psicología "
            "y revisión de carga académica según el protocolo de permanencia UPTC."
            if prediccion == 1 else "Estudiante en rangos seguros. Continuar con monitoreo de rutina."
        )
        
        return jsonify({
            'estado': 'Exitoso',
            'facultad_procesada': faculty.upper(),
            'perfil_riesgo': perfil,
            'probabilidad_desercion': f"{prob_riesgo:.2f}%",
            'recomendacion_institucional': recomendacion
        })

    except Exception as e:
        return jsonify({'estado': 'Fallo', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)