from flask import Flask, request, jsonify, render_template
import pandas as pd
from flask_cors import CORS
import os
import logging
import tempfile

app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'templates'))
CORS(app)

logging.basicConfig(level=logging.INFO)


#region Funções de processamento para a aba "futuras"

def process_futuras_previsao_total(df):
    """
    Calcula a previsão total para o próximo ano, agrupada por mês, usando a aba 'futuras'.
    """
    if 'ds' not in df.columns or 'y_previsto' not in df.columns:
        return []
    
    df['ds'] = pd.to_datetime(df['ds'])
    previsao_mensal = df.groupby(df['ds'].dt.to_period('M'))['y_previsto'].sum().reset_index()
    previsao_mensal['mes'] = previsao_mensal['ds'].dt.strftime('%B')
    previsao_mensal = previsao_mensal[['mes', 'y_previsto']]
    previsao_mensal.rename(columns={'y_previsto': 'total'}, inplace=True)
    return previsao_mensal.to_dict('records')
def process_futuras_total_ano_vs_ano(df):
    """
    Calcula o total das colunas numéricas por ano para a aba 'futuras'.
    Considera apenas os dois últimos anos presentes nos dados.
    """

def process_futuras_comparativo_ano_vs_ano(df):
    """
    Calcula o total das colunas numéricas por ano e a diferença percentual entre anos para a aba 'futuras'.
    Considera apenas os dois últimos anos presentes nos dados.
    """
    
def process_futuras_previsao_por_categoria(df):
    """
    Calcula a previsão por categoria para cada mês, usando a aba 'futuras'.
    """
   
def process_futuras_total_proximo_mes(df):
    """
    Calcula o total previsto para o próximo mês, usando a aba 'futuras'.
    """
    
#endregion


@app.route('/', methods=['GET'])
def index():
    return render_template('Dashboard.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo foi enviado"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo foi enviado"}), 400

    logging.info(f"Arquivo recebido: {file.filename}, Tipo: {file.content_type}")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
            file.save(temp_file.name)
            temp_filepath = temp_file.name

        df_futuras = pd.read_excel(temp_filepath, sheet_name='futuras', engine='openpyxl')
        os.remove(temp_filepath)

        if df_futuras.empty:
             return jsonify({"error": "Aba 'futuras' está vazia ou não encontrada"}), 404

        results = {
            "previsao_total": process_futuras_previsao_total(df_futuras),
            "total_ano_vs_ano": process_futuras_total_ano_vs_ano(df_futuras),
            "comparativo_ano_vs_ano": process_futuras_comparativo_ano_vs_ano(df_futuras),
            "previsao_por_categoria": process_futuras_previsao_por_categoria(df_futuras),
            "total_proximo_mes": process_futuras_total_proximo_mes(df_futuras),
        }

        return jsonify(results)


    except FileNotFoundError:
        return jsonify({"error": "Arquivo não encontrado"}), 500
    except KeyError:
        return jsonify({"error": "Aba 'futuras' não encontrada"}), 404
    except Exception as e:
        logging.exception(f"Erro ao processar o arquivo: {e}")
        return jsonify({"error": f"Erro ao processar o arquivo: {e}"}), 500



if __name__ == '__main__':
    app.run(debug=True)