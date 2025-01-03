from flask import Flask, request, jsonify, send_from_directory,render_template
import pandas as pd
from flask_cors import CORS
import os

app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'templates'))
CORS(app)

#region Funções de processamento para a aba "previsoes"

def process_previsao_total(df):
    """
    Calcula a previsão total para o ano de 2024, agrupada por mês.
    """
    if 'ds' not in df.columns:
        return []
    df['ds'] = pd.to_datetime(df['ds'])
    df_2024 = df[df['ds'].dt.year == 2024]
    previsao_cols = [col for col in df.columns if col.startswith('y_') and col != 'y_previsto']
    previsao_mensal = df_2024.groupby(df_2024['ds'].dt.to_period('M'))[previsao_cols].sum().reset_index()
    previsao_mensal['valor'] = previsao_mensal[previsao_cols].sum(axis=1)
    previsao_mensal['mes'] = previsao_mensal['ds'].dt.strftime('%Y-%m')
    previsao_mensal = previsao_mensal[['mes', 'valor']]
    return previsao_mensal.to_dict('records')

def process_entrantes(df):
    """
    Calcula o total de 'y' (entrantes reais) para o último mês disponível nos dados.
    """
    if 'ds' not in df.columns or 'y' not in df.columns:
        return []
    df['ds'] = pd.to_datetime(df['ds'])
    last_month = df['ds'].max().month
    last_year = df['ds'].max().year
    df_last_month = df[(df['ds'].dt.month == last_month) & (df['ds'].dt.year == last_year)]
    entrantes_reais = df_last_month.groupby(df_last_month['ds'].dt.to_period('M'))['y'].sum().reset_index()
    entrantes_reais['mes'] = entrantes_reais['ds'].dt.strftime('%Y-%m')
    entrantes_reais.columns = ['ds', 'valor', 'mes']
    return entrantes_reais.to_dict('records')

def process_total_ano_vs_ano(df):
    """
    Calcula o total das colunas numéricas por ano.
    """
    if 'ds' not in df.columns:
        return []
    df['ds'] = pd.to_datetime(df['ds'])
    numeric_cols = [col for col in df.select_dtypes(include=['number']).columns if col != 'ds']
    total_por_ano = df.groupby(df['ds'].dt.year)[numeric_cols].sum().reset_index()
    total_por_ano['total'] = total_por_ano[numeric_cols].sum(axis=1)
    total_por_ano.rename(columns={'ds': 'ano'}, inplace=True)
    total_por_ano = total_por_ano[['ano', 'total']]
    return total_por_ano.to_dict('records')

def process_comparativo_ano_vs_ano(df):
    """
    Calcula o total das colunas numéricas por ano e a diferença percentual entre anos.
    """
    if 'ds' not in df.columns:
        return []
    df['ds'] = pd.to_datetime(df['ds'])
    numeric_cols = [col for col in df.select_dtypes(include=['number']).columns if col != 'ds']
    total_por_ano = df.groupby(df['ds'].dt.year)[numeric_cols].sum().reset_index()
    total_por_ano['total'] = total_por_ano[numeric_cols].sum(axis=1)
    total_por_ano.rename(columns={'ds': 'ano'}, inplace=True)
    total_por_ano = total_por_ano[['ano', 'total']]
    total_por_ano['diferenca_percentual'] = total_por_ano['total'].pct_change() * 100
    return total_por_ano.to_dict('records')

def process_previsao_por_categoria(df):
    """
    Calcula a previsão por categoria para cada mês.
    """
    if 'ds' not in df.columns:
        return []

    df_previsao = df.copy()
    df_previsao['mes'] = pd.to_datetime(df_previsao['ds']).dt.to_period('M')
    previsao_cols = [
        col
        for col in df.columns
        if col.startswith('y_') and col != 'y_previsto' and col != 'y'
    ]

    if not previsao_cols:
        return []

    df_melted = pd.DataFrame()
    for col in previsao_cols:
        temp_df = pd.melt(
            df_previsao,
            id_vars=['mes'],
            value_vars=[col],
            var_name='categoria',
            value_name='previsao',
        )
        temp_df['categoria'] = temp_df['categoria'].str.replace('_previsto', '')
        df_melted = pd.concat([df_melted, temp_df])

    previsao_por_categoria = (
        df_melted.groupby(['mes', 'categoria'])['previsao'].sum().reset_index()
    )
    previsao_por_categoria['mes'] = previsao_por_categoria['mes'].dt.strftime('%Y-%m')
    return previsao_por_categoria.to_dict('records')

def process_total_proximo_mes(df):
    """
    Calcula o total previsto para o próximo mês.
    """
    if 'ds' not in df.columns:
        return {'total': 0}
    df['ds'] = pd.to_datetime(df['ds'])
    next_month = (df['ds'].max().month % 12) + 1
    next_month_year = df['ds'].max().year + (1 if df['ds'].max().month == 12 else 0)
    df_next_month = df[(df['ds'].dt.month == next_month) & (df['ds'].dt.year == next_month_year)]
    cols_to_sum = [col for col in df.columns if col.startswith('y_') and col != 'y_previsto' and df[col].dtype.kind in 'iufc']
    total_proximo_mes = df_next_month[cols_to_sum].sum().sum() if not df_next_month.empty else 0
    return {'total': total_proximo_mes}

#endregion

#region Funções de processamento para a aba "futuras"

def process_futuras_previsao_total(df):
    """
    Calcula a previsão total para o próximo ano, agrupada por mês, usando a aba 'futuras'.
    """
    if 'ds' not in df.columns:
        return []
    df['ds'] = pd.to_datetime(df['ds'])
    next_year = df['ds'].max().year + 1
    df_next_year = df[df['ds'].dt.year == next_year]
    previsao_cols = [col for col in df.columns if col.startswith('y_') and col != 'y_previsto']
    previsao_mensal = df_next_year.groupby(df_next_year['ds'].dt.to_period('M'))[previsao_cols].sum().reset_index()
    previsao_mensal['valor'] = previsao_mensal[previsao_cols].sum(axis=1)
    previsao_mensal['mes'] = previsao_mensal['ds'].dt.strftime('%Y-%m')
    previsao_mensal = previsao_mensal[['mes', 'valor']]
    return previsao_mensal.to_dict('records')

def process_futuras_total_ano_vs_ano(df):
    """
    Calcula o total das colunas numéricas por ano para a aba 'futuras'.
    Considera apenas os dois últimos anos presentes nos dados.
    """
    if 'ds' not in df.columns:
        return []

    df['ds'] = pd.to_datetime(df['ds'])
    numeric_cols = [
        col for col in df.select_dtypes(include=['number']).columns if col != 'ds'
    ]

    # Considera apenas os dois últimos anos
    last_two_years = sorted(df['ds'].dt.year.unique())[-2:]
    df = df[df['ds'].dt.year.isin(last_two_years)]

    total_por_ano = df.groupby(df['ds'].dt.year)[numeric_cols].sum().reset_index()
    total_por_ano['total'] = total_por_ano[numeric_cols].sum(axis=1)
    total_por_ano.rename(columns={'ds': 'ano'}, inplace=True)
    total_por_ano = total_por_ano[['ano', 'total']]
    return total_por_ano.to_dict('records')

def process_futuras_comparativo_ano_vs_ano(df):
    """
    Calcula o total das colunas numéricas por ano e a diferença percentual entre anos para a aba 'futuras'.
    Considera apenas os dois últimos anos presentes nos dados.
    """
    if 'ds' not in df.columns:
        return []

    df['ds'] = pd.to_datetime(df['ds'])
    numeric_cols = [
        col for col in df.select_dtypes(include=['number']).columns if col != 'ds'
    ]

    # Considera apenas os dois últimos anos
    last_two_years = sorted(df['ds'].dt.year.unique())[-2:]
    df = df[df['ds'].dt.year.isin(last_two_years)]

    total_por_ano = df.groupby(df['ds'].dt.year)[numeric_cols].sum().reset_index()
    total_por_ano['total'] = total_por_ano[numeric_cols].sum(axis=1)
    total_por_ano.rename(columns={'ds': 'ano'}, inplace=True)
    total_por_ano = total_por_ano[['ano', 'total']]
    total_por_ano['diferenca_percentual'] = total_por_ano['total'].pct_change() * 100
    return total_por_ano.to_dict('records')

def process_futuras_previsao_por_categoria(df):
    """
    Calcula a previsão por categoria para cada mês, usando a aba 'futuras'.
    """
    if 'ds' not in df.columns:
        return []

    df_futuras = df.copy()
    df_futuras['mes'] = pd.to_datetime(df_futuras['ds']).dt.to_period('M')
    previsao_cols = [
        col
        for col in df.columns
        if col.startswith('y_') and col != 'y_previsto' and col != 'y'
    ]

    if not previsao_cols:
        return []

    df_melted = pd.DataFrame()
    for col in previsao_cols:
        temp_df = pd.melt(
            df_futuras,
            id_vars=['mes'],
            value_vars=[col],
            var_name='categoria',
            value_name='previsao',
        )
        temp_df['categoria'] = temp_df['categoria'].str.replace('_previsto', '')
        df_melted = pd.concat([df_melted, temp_df])

    previsao_por_categoria = (
        df_melted.groupby(['mes', 'categoria'])['previsao'].sum().reset_index()
    )
    previsao_por_categoria['mes'] = previsao_por_categoria['mes'].dt.strftime('%Y-%m')
    return previsao_por_categoria.to_dict('records')

def process_futuras_total_proximo_mes(df):
    """
    Calcula o total previsto para o próximo mês, usando a aba 'futuras'.
    """
    if 'ds' not in df.columns:
        return {'total': 0}
    df['ds'] = pd.to_datetime(df['ds'])
    next_month = (df['ds'].max().month % 12) + 1
    next_month_year = df['ds'].max().year + (1 if df['ds'].max().month == 12 else 0)
    df_next_month = df[(df['ds'].dt.month == next_month) & (df['ds'].dt.year == next_month_year)]
    cols_to_sum = [col for col in df.columns if col.startswith('y_') and col != 'y_previsto' and df[col].dtype.kind in 'iufc']
    total_proximo_mes = df_next_month[cols_to_sum].sum().sum() if not df_next_month.empty else 0
    return {'total': total_proximo_mes}

#endregion

@app.route('/', methods=['GET'])
def index():
    return render_template('Dashboard.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    print("Rota /upload acessada!")  # Verifica se a rota está sendo chamada
    if 'file' not in request.files:
        print("request.files:", request.files)  # Imprime o conteúdo de request.files
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    file = request.files['file']
    print("file:", file)  # Verifica se o objeto file foi obtido

    if file.filename == '':
        print("file.filename:", file.filename)  # Verifica o nome do arquivo
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400

    file_ext = file.filename.split('.')[-1]

    # Verifica se o tipo de arquivo é suportado
    if file_ext not in ['csv', 'xlsx']:
        return jsonify({'error': 'Formato de arquivo não suportado'}), 400

    # Processar o arquivo aqui
    if file_ext == 'csv':
        df = pd.read_csv(file)
        df_futuras = pd.DataFrame()
    elif file_ext == 'xlsx':
        xl = pd.ExcelFile(file)
        df = xl.parse('previsoes') if 'previsoes' in xl.sheet_names else pd.DataFrame()
        df_futuras = xl.parse('futuras') if 'futuras' in xl.sheet_names else pd.DataFrame()
    else:
        return jsonify({'error': 'Formato de arquivo não suportado'}), 400

    # Dicionário de resultados
    result = {
        'previsaoTotalEntrantes': process_previsao_total(df),
        'entrantes': process_entrantes(df),
        'totalAnoVsAno': process_total_ano_vs_ano(df),
        'comparativoAnoVsAno': process_comparativo_ano_vs_ano(df),
        'previsaoPorCategoria': process_previsao_por_categoria(df),
        'totalProximoMes': process_total_proximo_mes(df),
        'proximosEventos': [],
        'dadosDiarizados': [],
        'futurasPrevisaoTotal': process_futuras_previsao_total(df_futuras),
        'futurasTotalAnoVsAno': process_futuras_total_ano_vs_ano(df_futuras),
        'futurasComparativoAnoVsAno': process_futuras_comparativo_ano_vs_ano(df_futuras),
        'futurasPrevisaoPorCategoria': process_futuras_previsao_por_categoria(df_futuras),
        'futurasTotalProximoMes': process_futuras_total_proximo_mes(df_futuras),
    }

    return jsonify({'success': True, 'data': result})

if __name__ == '__main__':
    app.run(debug=True)