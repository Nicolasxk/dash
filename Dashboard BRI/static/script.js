document.getElementById('btn-import').addEventListener('click', function(event) {
    event.preventDefault(); 
    document.getElementById('file-input').click(); 
});

document.getElementById('file-input').addEventListener('change', function(event) {
    const file = event.target.files[0];

    if (file) {
        const formData = new FormData();
        formData.append('file', file);

        fetch('/', { // Faz a requisição para /upload
            method: 'POST',
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na requisição: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            console.log('Dados importados com sucesso:', data);

            // Só gera os gráficos DEPOIS que os dados forem recebidos com sucesso
            generateGraph('grafico1Canvas', data.previsaoTotalEntrantes, 'mes', 'valor', 'Previsão Total de Entrantes');
            generateGraph('grafico2Canvas', data.entrantes, 'mes', 'valor', 'Entrantes');
            generateGraph('grafico3Canvas', data.totalAnoVsAno, 'ano', 'total', 'Total Ano vs Ano');
            generateGraph('grafico4Canvas', data.comparativoAnoVsAno, 'ano', 'diferenca_percentual', 'Comparativo Ano vs Ano');
            generateGraph('grafico5Canvas', data.previsaoPorCategoria, 'mes', 'previsao', 'Previsão por Categoria');
            generateGraph('grafico6Canvas', data.totalProximoMes, 'total', 'total', 'Total de Previsão para o Próximo Mês');
            generateGraph('grafico7Canvas', data.proximosEventos, 'data_evento', 'evento', 'Próximos Eventos');
            generateGraph('grafico8Canvas', data.dadosDiarizados, 'data', 'total', 'Dados Diarizados de Entrantes Total');
        })
        .catch(error => {
            console.error("Erro ao enviar o arquivo:", error);
        });
    }
});

function generateGraph(canvasId, data, labelKey, valueKey, title) {
    if (!document.getElementById(canvasId)) {
        console.error(`Canvas element with id ${canvasId} not found.`);
        return;
    }

    const ctx = document.getElementById(canvasId).getContext('2d');

    if (!data || data.length === 0) {
        console.warn(`No data provided for ${canvasId}.`);
        ctx.font = '20px Arial';
        ctx.fillStyle = 'red';
        ctx.textAlign = 'center';
        ctx.fillText('Sem dados para este gráfico', ctx.canvas.width / 2, ctx.canvas.height / 2);
        return;
    }

    if (canvasId === 'grafico6Canvas') {
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [title],
                datasets: [{
                    label: title,
                    data: [data.total],
                    backgroundColor: 'rgba(0, 123, 255, 0.5)',
                    borderColor: 'rgba(0, 123, 255, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    } else if (canvasId === 'grafico7Canvas') {
        if (Array.isArray(data) && data.every(item => 'data_evento' in item && 'evento' in item)) {
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.map(item => {
                        const date = new Date(item.data_evento);
                        return isNaN(date.getTime()) ? '' : `${date.getDate()}/${date.getMonth() + 1}/${date.getFullYear()}`;
                    }),
                    datasets: [{
                        label: title,
                        data: data.map(item => 1),
                        backgroundColor: 'rgba(0, 123, 255, 0.5)',
                        borderColor: 'rgba(0, 123, 255, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    }
                }
            });
        } else {
            console.error('Dados inválidos para o gráfico de Próximos Eventos.');
        }
    } else {
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(item => item[labelKey]),
                datasets: [{
                    label: title,
                    data: data.map(item => item[valueKey]),
                    backgroundColor: 'rgba(0, 123, 255, 0.5)',
                    borderColor: 'rgba(0, 123, 255, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }
}

// Funções de export (não implementadas, mas os listeners estão aqui)
document.getElementById('btn-export-grafico1').addEventListener('click', () => exportChart('grafico1Canvas'));
document.getElementById('btn-export-grafico2').addEventListener('click', () => exportChart('grafico2Canvas'));
document.getElementById('btn-export-grafico3').addEventListener('click', () => exportChart('grafico3Canvas'));
document.getElementById('btn-export-grafico4').addEventListener('click', () => exportChart('grafico4Canvas'));
document.getElementById('btn-export-grafico5').addEventListener('click', () => exportChart('grafico5Canvas'));
document.getElementById('btn-export-grafico6').addEventListener('click', () => exportChart('grafico6Canvas'));
document.getElementById('btn-export-grafico7').addEventListener('click', () => exportChart('grafico7Canvas'));
document.getElementById('btn-export-grafico8').addEventListener('click', () => exportChart('grafico8Canvas'));