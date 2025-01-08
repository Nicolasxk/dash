console.log("script.js carregado!");

    function generateGraph(canvasId, data, xLabel, yLabel, title) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas element with id '${canvasId}' not found.`);
            return;
        }
        const ctx = canvas.getContext('2d');

        if (!ctx) {
            console.error("Could not get 2D context for canvas");
             return;
        }
        if (!data || data.length === 0) {
            console.log(`No data to generate graph for canvas '${canvasId}'.`);
          new Chart(ctx, {
            type: 'line',
            data:{
                labels: [],
                datasets: []
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
            }
        });
          return;
        }

        let labels = [];
        let values = [];
        if(xLabel === 'mes' || xLabel === 'ano' || xLabel === 'data' ){
            labels = data.map(item => item[xLabel]);
             values = data.map(item => item[yLabel]);
        }else{
             values = data.map(item => item[yLabel]);
             labels = data.map((item, index) => `Label ${index+1}`);
        }

       new Chart(ctx, {
           type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: title,
                    data: values,
                    fill: false,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                 responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: xLabel
                        },
                    },
                    y: {
                        title: {
                            display: true,
                            text: yLabel
                        },
                    }
                }
            }
        });
    }
    function exportChart(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Canvas with ID '${canvasId}' not found.`);
        return;
    }
    const imgData = canvas.toDataURL('image/png');

    const link = document.createElement('a');
    link.href = imgData;
    link.download = `${canvasId}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

    document.addEventListener('DOMContentLoaded', function() {
            const uploadForm = document.getElementById('upload-form');
            const fileInput = document.getElementById('file-input');
             const importButton = document.getElementById('btn-import');
            importButton.addEventListener('click', function(){
                const fileInput = document.getElementById('file-input');
                fileInput.click();
            });

            uploadForm.onsubmit = function() {
            if (!fileInput.files.length) {
                alert('Por favor, selecione um arquivo para enviar.');
                return false;
            }
            };
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            const loader = document.createElement('div');
            loader.classList.add('loader');
            document.body.appendChild(loader);

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
             if (data.error){
                 console.error("Erro ao enviar o arquivo:", data.error);
                   alert(data.error);
                 return;
            }

            generateGraph('grafico1Canvas', data.previsao_total, 'mes', 'valor', 'Previsão Total de Entrantes');
            generateGraph('grafico2Canvas', [], 'mes', 'valor', 'Entrantes');
            generateGraph('grafico3Canvas', data.total_ano_vs_ano, 'ano', 'total', 'Total Ano vs Ano');
            generateGraph('grafico4Canvas', data.comparativo_ano_vs_ano, 'ano', 'diferenca_percentual', 'Comparativo Ano vs Ano');
            generateGraph('grafico5Canvas', data.previsao_por_categoria, 'mes', 'previsao', 'Previsão por Categoria');
             generateGraph('grafico6Canvas', [data.total_proximo_mes], 'total', 'total', 'Total de Previsão para o Próximo Mês');
            generateGraph('grafico7Canvas', [], 'data_evento', 'evento', 'Próximos Eventos');
             generateGraph('grafico8Canvas', [], 'data', 'total', 'Dados Diarizados de Entrantes Total');
        })
          .catch(error => {
           console.error("Erro ao enviar o arquivo:", error);
           alert("Erro ao processar o arquivo"+ error);
         }).finally(() => {
              document.body.removeChild(loader);
        });
    });
   document.getElementById('file-input').addEventListener('change', function(event) {
         // Não faz nada aqui.
     });

});