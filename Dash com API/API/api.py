from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    # Recebe o arquivo
    file = request.files['file']
    file_ext = file.filename.split('.')[-1]
    
    # Carrega os dados dependendo do formato
    if file_ext == 'csv':
        df = pd.read_csv(file)
    elif file_ext in ['xls', 'xlsx']:
        df = pd.read_excel(file)
    else:
        return jsonify({'error': 'Formato de arquivo inválido'}), 400

    # Processamento de dados (substitua com a lógica para cada gráfico)
    result = {
        'previsaoTotalEntrantes': process_previsao_total(df),
        
    }

    return jsonify(result)

# Funções de processamento (exemplo)
def process_previsao_total(df):

    df['ds'] = pd.to_datetime(df['ds'])
    df_2024 = df[df['ds'].dt.year == 2024]
    df_2024_monthly = df_2024.groupby(df_2024['ds'].dt.month)['D'].sum()

    janeiro_2024 = df_2024_monthly.get(1, 0)
