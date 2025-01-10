from flask import Flask, request, jsonify, render_template
import pandas as pd
from flask_cors import CORS
import os
import logging
import tempfile
from datetime import datetime

app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'templates'))
CORS(app)

logging.basicConfig(level=logging.INFO)

#region Funções de processamento para a aba "futuras"

def process_futuras_previsao_total(df):
    """
    Calcula a previsão total para o próximo ano, agrupada por mês, usando a aba 'futuras'.
    """
    date_col = next((col for col in df.columns if 'ds' in col), None)
    if not date_col:
        return []
    
    value_col = next((col for col in df.columns if 'y' in col), None)
    if not value_col:
        return []
    
    df[date_col] = pd.to_datetime(df[date_col])
    previsao_mensal = df.groupby(df[date_col].dt.to_period('M'))[value_col].sum().reset_index()
    previsao_mensal['mes'] = previsao_mensal[date_col].dt.strftime('%B')
    previsao_mensal = previsao_mensal[['mes', value_col]]
    previsao_mensal.rename(columns={value_col: 'valor'}, inplace=True)
    return previsao_mensal.to_dict('records')


def process_futuras_total_ano_vs_ano(df):
    """
    Calcula o total das colunas numéricas por ano para a aba 'futuras'.
    Considera apenas os dois últimos anos presentes nos dados.
    """
    date_col = next((col for col in df.columns if 'ds' in col), None)
    if not date_col:
          return []
    
    df[date_col] = pd.to_datetime(df[date_col])
    df['ano'] = df[date_col].dt.year
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if not numeric_cols:
         return []
    
    numeric_cols.remove('ano') if 'ano' in numeric_cols else None
    
    
    last_two_years = sorted(df['ano'].unique())[-2:]
    df_filtered = df[df['ano'].isin(last_two_years)]
    
    total_por_ano = df_filtered.groupby('ano')[numeric_cols].sum().reset_index()
    total_por_ano.rename(columns={'ano': 'ano'}, inplace=True)
    
    
    total_por_ano_dict = total_por_ano.to_dict('records')
    #calculando o total com o total de todas colunas numéricas
    for item in total_por_ano_dict:
      item['total'] = 0
      for col in numeric_cols:
        try:
          item['total'] += item[col]
        except:
           logging.warning(f"Erro ao somar a coluna {col} no total, valor nao numerico")
      for col in numeric_cols:
          if col in item:
              del item[col]

    
    return total_por_ano_dict


def process_futuras_comparativo_ano_vs_ano(df):
    """
    Calcula o total das colunas numéricas por ano e a diferença percentual entre anos para a aba 'futuras'.
    Considera apenas os dois últimos anos presentes nos dados.
    """
    date_col = next((col for col in df.columns if 'ds' in col), None)
    if not date_col:
          return []
    
    df[date_col] = pd.to_datetime(df[date_col])
    df['ano'] = df[date_col].dt.year

    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if not numeric_cols:
        return []
    numeric_cols.remove('ano') if 'ano' in numeric_cols else None
    
    last_two_years = sorted(df['ano'].unique())[-2:]
    if len(last_two_years) < 2:
        return []

    df_filtered = df[df['ano'].isin(last_two_years)]

    total_por_ano = df_filtered.groupby('ano')[numeric_cols].sum().reset_index()
    
    total_por_ano.rename(columns={'ano':'ano'},inplace=True)
    
    total_por_ano_dict = total_por_ano.to_dict('records')

    for item in total_por_ano_dict:
      item['total'] = 0
      for col in numeric_cols:
          try:
            item['total'] += item[col]
          except:
             logging.warning(f"Erro ao somar a coluna {col} no total, valor nao numerico")
      for col in numeric_cols:
        if col in item:
            del item[col]
    
    if len(total_por_ano_dict) < 2:
        return []

    ano_anterior = total_por_ano_dict[0]['total']
    ano_atual = total_por_ano_dict[1]['total']

    diferenca_percentual = ((ano_atual - ano_anterior) / ano_anterior) * 100 if ano_anterior != 0 else 0

    return [{
        'ano': last_two_years[1],
        'diferenca_percentual': diferenca_percentual,
    }]

def process_futuras_previsao_por_categoria(df):
    """
    Calcula a previsão por categoria para cada mês, usando a aba 'futuras'.
    """
    date_col = next((col for col in df.columns if 'ds' in col), None)
    if not date_col:
          return []

    value_col = next((col for col in df.columns if 'y' in col), None)
    if not value_col:
          return []

    cat_col = next((col for col in df.columns if 'categoria' in col), None)
    if not cat_col:
          return []
    
    df[date_col] = pd.to_datetime(df[date_col])
    df['mes'] = df[date_col].dt.strftime('%B')
    
    previsao_por_categoria = df.groupby(['mes',cat_col])[value_col].sum().reset_index()
    previsao_por_categoria = previsao_por_categoria[['mes',cat_col, value_col]]
    previsao_por_categoria.rename(columns={value_col: 'previsao', cat_col:'categoria'}, inplace=True)

    return previsao_por_categoria.to_dict('records')

def process_futuras_total_proximo_mes(df):
    """
    Calcula o total previsto para o próximo mês, usando a aba 'futuras'.
    """
    date_col = next((col for col in df.columns if 'ds' in col), None)
    if not date_col:
         return {'total': 0}

    value_col = next((col for col in df.columns if 'y' in col), None)
    if not value_col:
          return {'total': 0}
    
    df[date_col] = pd.to_datetime(df[date_col])
    proximo_mes = (datetime.now().replace(day=1) + pd.DateOffset(months=1))

    df_proximo_mes = df[df[date_col].dt.to_period('M') == proximo_mes.strftime('%Y-%m')]


    total_previsto_proximo_mes = df_proximo_mes[value_col].sum() if not df_proximo_mes.empty else 0
    
    return {'total': total_previsto_proximo_mes}

#endregion


@app.route('/', methods=['GET'])
def index():
    return render_template('Dashboard.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    logging.info("Requisição para /upload recebida")
    if 'file' not in request.files:
        logging.error("Nenhum arquivo foi enviado na requisição")
        return jsonify({"error": "Nenhum arquivo foi enviado"}), 400
    file = request.files['file']
    if file.filename == '':
        logging.error("Nenhum arquivo foi enviado na requisição")
        return jsonify({"error": "Nenhum arquivo foi enviado"}), 400

    logging.info(f"Arquivo recebido: {file.filename}, Tipo: {file.content_type}")
    temp_filepath = None
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
           file.save(temp_file.name)
           temp_filepath = temp_file.name

        if file.filename.endswith('.csv'):
            df_futuras = pd.read_csv(temp_filepath, sep=';')
            df_futuras = df_futuras.dropna(how='all')
        elif file.filename.endswith('.xlsx'):
            df_futuras = pd.read_excel(temp_filepath, sheet_name='futuras')
        else:
            logging.error(f"Formato de arquivo '{file.filename}' não suportado")
            return jsonify({"error": "Formato de arquivo não suportado. Use .csv ou .xlsx"}), 400

        for col in df_futuras.columns:
            if col != 'ds':
                try:
                    df_futuras[col] = pd.to_numeric(df_futuras[col])
                except ValueError:
                    logging.error(f"Erro ao converter a coluna {col} para numérica")
                    return jsonify({"error": f"Erro ao converter a coluna {col} para numérica"}), 400
            
        if df_futuras.empty:
              logging.error("O arquivo está vazio ou não encontrado")
              return jsonify({"error": "O arquivo está vazio ou não encontrado"}), 404

        if not all(col in df_futuras.columns for col in ['ds', 'y']):
              logging.error("Colunas 'ds' ou 'y' não encontradas no arquivo")
              return jsonify({"error": "Colunas 'ds' ou 'y' não encontradas no arquivo"}), 400
          
        results = {}
          
        if 'ds' in df_futuras.columns and 'y' in df_futuras.columns:
            try:
                results["previsao_total"] = process_futuras_previsao_total(df_futuras)
            except Exception as e:
                logging.error(f"Erro ao processar a previsão total: {e}", exc_info=True)
                return jsonify({"error": f"Erro ao processar a previsão total: {e}"}), 500
        if 'ds' in df_futuras.columns:
            try:
                results["total_ano_vs_ano"] = process_futuras_total_ano_vs_ano(df_futuras)
            except Exception as e:
                logging.error(f"Erro ao processar o total ano vs ano: {e}", exc_info=True)
                return jsonify({"error": f"Erro ao processar o total ano vs ano: {e}"}), 500
        if 'ds' in df_futuras.columns:
            try:
                results["comparativo_ano_vs_ano"] = process_futuras_comparativo_ano_vs_ano(df_futuras)
            except Exception as e:
                logging.error(f"Erro ao processar o comparativo ano vs ano: {e}", exc_info=True)
                return jsonify({"error": f"Erro ao processar o comparativo ano vs ano: {e}"}), 500
        if 'ds' in df_futuras.columns and 'y' in df_futuras.columns and 'categoria' in df_futuras.columns:
            try:
                results["previsao_por_categoria"] = process_futuras_previsao_por_categoria(df_futuras)
            except Exception as e:
                logging.error(f"Erro ao processar a previsão por categoria: {e}", exc_info=True)
                return jsonify({"error": f"Erro ao processar a previsão por categoria: {e}"}), 500
        if 'ds' in df_futuras.columns and 'y' in df_futuras.columns:
            try:
                results["total_proximo_mes"] = process_futuras_total_proximo_mes(df_futuras)
            except Exception as e:
                logging.error(f"Erro ao processar o total do proximo mes: {e}", exc_info=True)
                return jsonify({"error": f"Erro ao processar o total do proximo mes: {e}"}), 500
          
        return jsonify(results)

    except FileNotFoundError:
        logging.error("Arquivo não encontrado", exc_info=True)
        return jsonify({"error": "Arquivo não encontrado"}), 500
    except KeyError:
        logging.error("Aba 'futuras' não encontrada", exc_info=True)
        return jsonify({"error": "Aba 'futuras' não encontrada"}), 404
    except Exception as e:
        logging.exception(f"Erro ao processar o arquivo: {e}")
        return jsonify({"error": f"Erro ao processar o arquivo: {e}"}), 500
    finally:
        if temp_filepath:
            os.remove(temp_filepath)


if __name__ == '__main__':
    app.run(debug=True)