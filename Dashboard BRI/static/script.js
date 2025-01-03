document.addEventListener('DOMContentLoaded', function() { // Adiciona o listener para 'DOMContentLoaded'
    document.getElementById('btn-import').addEventListener('click', function() {
        document.getElementById('file-input').click();
    });

    document.getElementById('upload-form').addEventListener('submit', function(e) {
        e.preventDefault(); // Previne o comportamento padrão de submit do formulário

        const formData = new FormData(this); 

        // Depuração: Verificar o conteúdo do FormData
        console.log("FormData entries:");
        for (const pair of formData.entries()) {
            console.log(pair[0] + ', ' + pair[1]);
        }

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na requisição: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            console.log('Dados importados com sucesso:', data);
            if (data.success) {
                // Só gera os gráficos DEPOIS que os dados forem recebidos com sucesso
                generateGraph('grafico1Canvas', data.data.previsaoTotalEntrantes, 'mes', 'valor', 'Previsão Total de Entrantes');
                console.log("grafico1Canvas:", document.getElementById('grafico1Canvas'));
                generateGraph('grafico2Canvas', data.data.entrantes, 'mes', 'valor', 'Entrantes');
                console.log("grafico2Canvas:", document.getElementById('grafico2Canvas'));
                generateGraph('grafico3Canvas', data.data.totalAnoVsAno, 'ano', 'total', 'Total Ano vs Ano');
                console.log("grafico3Canvas:", document.getElementById('grafico3Canvas'));
                generateGraph('grafico4Canvas', data.data.comparativoAnoVsAno, 'ano', 'diferenca_percentual', 'Comparativo Ano vs Ano');
                console.log("grafico4Canvas:", document.getElementById('grafico4Canvas'));
                generateGraph('grafico5Canvas', data.data.previsaoPorCategoria, 'mes', 'previsao', 'Previsão por Categoria');
                console.log("grafico5Canvas:", document.getElementById('grafico5Canvas'));
                generateGraph('grafico6Canvas', data.data.totalProximoMes, 'total', 'total', 'Total de Previsão para o Próximo Mês');
                console.log("grafico6Canvas:", document.getElementById('grafico6Canvas'));
                generateGraph('grafico7Canvas', data.data.proximosEventos, 'data_evento', 'evento', 'Próximos Eventos');
                console.log("grafico7Canvas:", document.getElementById('grafico7Canvas'));
                generateGraph('grafico8Canvas', data.data.dadosDiarizados, 'data', 'total', 'Dados Diarizados de Entrantes Total');
                console.log("grafico8Canvas:", document.getElementById('grafico8Canvas'));
            }
        })
        .catch(error => {
            console.error("Erro ao enviar o arquivo:", error);
        });
    });

    document.getElementById('file-input').addEventListener('change', function(event) {
        const file = event.target.files[0];

        if (file) {
            document.getElementById('upload-form').submit(); // Submete o formulário
        }
    });

    // Funções de export (não implementadas, mas os listeners estão aqui)
    document.getElementById('btn-export-grafico1').addEventListener('click', () => exportChart('grafico1Canvas'));
    document.getElementById('btn-export-grafico2').addEventListener('click', () => exportChart('grafico2Canvas'));
    document.getElementById('btn-export-grafico3').addEventListener('click', () => exportChart('grafico3Canvas'));
    document.getElementById('btn-export-grafico4').addEventListener('click', () => exportChart('grafico4Canvas'));
    document.getElementById('btn-export-grafico5').addEventListener('click', () => exportChart('grafico5Canvas'));
    document.getElementById('btn-export-grafico6').addEventListener('click', () => exportChart('grafico6Canvas'));
    document.getElementById('btn-export-grafico7').addEventListener('click', () => exportChart('grafico7Canvas'));
    document.getElementById('btn-export-grafico8').addEventListener('click', () => exportChart('grafico8Canvas'));
});