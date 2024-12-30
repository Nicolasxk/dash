from flask import Flask, request, jsonify
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Funções de processamento 

def process_previsao_total(df):
    df['ds'] = pd.to_datetime(df['ds'])
    df_2024 = df[df['ds'].dt.year == 2024]
    previsao_mensal = df_2024.groupby(df_2024['ds'].dt.month)[df.columns[9:]].sum().reset_index()
    previsao_mensal['valor'] = previsao_mensal[df.columns[9:]].sum(axis=1)
    previsao_mensal = previsao_mensal[['mes', 'valor']]
    return previsao_mensal.to_dict('records')

def process_entrantes(df):
    if 'D' not in df.columns or df['D'].isnull().all():
        return []
    df['ds'] = pd.to_datetime(df['ds'])
    last_month = df['ds'].max().month
    last_year = df['ds'].max().year
    df_last_month = df[(df['ds'].dt.month == last_month) & (df['ds'].dt.year == last_year)]
    entrantes_reais = df_last_month.groupby(df_last_month['ds'].dt.month)['D'].sum().reset_index()
    entrantes_reais.columns = ['mes', 'valor']
    return entrantes_reais.to_dict('records')

def process_total_ano_vs_ano(df):
    total_por_ano = df.groupby(df['ds'].dt.year)[df.columns[9:]].sum().reset_index()
    total_por_ano['total'] = total_por_ano[df.columns[9:]].sum(axis=1)
    total_por_ano = total_por_ano[['ano', 'total']]
    return total_por_ano.to_dict('records')

def process_comparativo_ano_vs_ano(df):
    total_por_ano = df.groupby(df['ds'].dt.year)[df.columns[9:]].sum().reset_index()
    total_por_ano['total'] = total_por_ano[df.columns[9:]].sum(axis=1)
    total_por_ano = total_por_ano[['ano', 'total']]
    total_por_ano['diferenca_percentual'] = total_por_ano['total'].pct_change() * 100
    return total_por_ano.to_dict('records')

def process_previsao_por_categoria(df):
    previsao_por_categoria = df.copy()
    previsao_por_categoria['mes'] = previsao_por_categoria['ds'].dt.month

    previsao_cols = df.columns[9:]
    df_melted = pd.DataFrame()

    for col in previsao_cols:
        temp_df = pd.melt(previsao_por_categoria, id_vars=['mes'], value_vars=[col], var_name='categoria', value_name='previsao')
        temp_df['categoria'] = temp_df['categoria'].str.replace('_previsto', '')
        df_melted = pd.concat([df_melted, temp_df])

    previsao_por_categoria = df_melted.groupby(['mes', 'categoria'])['previsao'].sum().reset_index()
    return previsao_por_categoria.to_dict('records')

def process_total_proximo_mes(df):
    df['ds'] = pd.to_datetime(df['ds'])
    next_month = (df['ds'].max().month % 12) + 1 # Pega o próximo mês, considerando a virada do ano
    next_month_year = df['ds'].max().year + (1 if df['ds'].max().month == 12 else 0) # Adiciona 1 ao ano se o último mês for dezembro
    df_next_month = df[(df['ds'].dt.month == next_month) & (df['ds'].dt.year == next_month_year)]
    total_proximo_mes = df_next_month[df.columns[9:]].sum().sum()
    return {'total': total_proximo_mes}

def process_proximos_eventos(df):
    if 'evento' not in df.columns or 'data_evento' not in df.columns:
        return []

    df['data_evento'] = pd.to_datetime(df['data_evento'], errors='coerce')
    if df['data_evento'].isnull().all():
        return []

    today = pd.to_datetime('today')
    next_7_days = today + pd.DateOffset(days=7)
    df_next_events = df[(df['data_evento'] >= today) & (df['data_evento'] <= next_7_days)]
    proximos_eventos = df_next_events[['data_evento', 'evento']].sort_values(by='data_evento').drop_duplicates()
    return proximos_eventos.to_dict('records')

def process_dados_diarizados(df):
    if 'D' not in df.columns or df['D'].isnull().all():
        return []
    df['ds'] = pd.to_datetime(df['ds'])
    dados_diarios = df.groupby(df['ds'].dt.date)['D'].sum().reset_index()
    dados_diarios.columns = ['data', 'total']
    return dados_diarios.to_dict('records')

# Rota Flask

@app.route('/', methods=['POST'])
def upload_file():
    file = request.files['file']
    file_ext = file.filename.split('.')[-1]

    if file_ext == 'csv':
        df = pd.read_csv(file)
    elif file_ext == 'xlsx':
        df = pd.read_excel(file)
    else:
        return jsonify({'error': 'Formato de arquivo não suportado'}), 400

    if 'ds' in df.columns:
        df['ds'] = pd.to_datetime(df['ds'], errors='coerce')

    # Dicionário de resultados
    result = {
        'previsaoTotalEntrantes': process_previsao_total(df),
        'entrantes': process_entrantes(df),
        'totalAnoVsAno': process_total_ano_vs_ano(df),
        'comparativoAnoVsAno': process_comparativo_ano_vs_ano(df),
        'previsaoPorCategoria': process_previsao_por_categoria(df),
        'totalProximoMes': process_total_proximo_mes(df),
        'proximosEventos': process_proximos_eventos(df),
        'dadosDiarizados': process_dados_diarizados(df),
    }

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)