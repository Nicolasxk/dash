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
        type: 'bar',
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
      labels = data.map(item => {
          if (item && item[xLabel] !== undefined) {
              return item[xLabel];
          } else {
              console.error(`Propriedade ${xLabel} não encontrada em um dos objetos`);
              return null;
          }
      }).filter(item => item !== null);

       values = data.map(item => {
            if(item && item[yLabel] !== undefined) {
                return item[yLabel];
           } else {
               console.error(`Propriedade ${yLabel} não encontrada em um dos objetos`);
               return null;
           }
       }).filter(item => item !== null);
    } else {
        values = data.map(item => {
            if(item && item[yLabel] !== undefined){
                return item[yLabel];
            }else{
                console.error(`Propriedade ${yLabel} não encontrada em um dos objetos`);
                return null
            }
        }).filter(item => item !== null);
        labels = data.map((item, index) => `Label ${index+1}`);
    }

   new Chart(ctx, {
       type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: values,
                fill: true,
                borderColor: 'rgb(208, 231, 2)',
                brackgroundColor: 'rgb(230, 255, 8)',
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

        uploadForm.onsubmit = function() {
        if (!fileInput.files.length) {
            alert('Por favor, selecione um arquivo para enviar.');
            fileInput.click()
            return false;
        }

        };
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        console.log("Evento submit disparado")
        console.log('fileInput', fileInput);

          if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
            console.error("Nenhum arquivo selecionado ou o input está incorreto");
            alert("Nenhum arquivo selecionado ou o input está incorreto");
            return;
        }
        
         const formData = new FormData(uploadForm);
           console.log("FormData:", formData.get('file'));
        const loader = document.createElement('div');
        loader.classList.add('loader');
        document.body.appendChild(loader);
        console.log("Antes da requisição da API")
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
        console.log("Dados da API:",data);

        // Gráfico 1: Previsão Total de Entrantes
        if(data && data.previsao_total) {
            generateGraph('grafico1Canvas', data.previsao_total, 'mes', 'valor', 'Previsão Total de Entrantes');
         } else {
             console.error("Erro ao gerar gráfico 1, dados de previsão total inválidos:", data);
         }
        // Gráfico 2: Entrantes (dados estáticos, pois você mencionou que esses valores não estão no backend)
        generateGraph('grafico2Canvas', [{mes:"Janeiro",valor: 10}, {mes:"Fevereiro",valor: 20}, {mes:"Março",valor: 30}], 'mes', 'valor', 'Entrantes');

         // Gráfico 3: Total Ano vs Ano
         if (data && data.total_ano_vs_ano) {
           generateGraph('grafico3Canvas', data.total_ano_vs_ano, 'ano', 'total', 'Total Ano vs Ano');
         } else {
            console.error("Erro ao gerar gráfico 3, dados de total ano vs ano inválidos:", data);
          }

        // Gráfico 4: Comparativo Ano vs Ano
        if (data && data.comparativo_ano_vs_ano) {
            generateGraph('grafico4Canvas', data.comparativo_ano_vs_ano, 'ano', 'diferenca_percentual', 'Comparativo Ano vs Ano');
          } else {
            console.error("Erro ao gerar gráfico 4, dados de comparativo ano vs ano inválidos:", data);
         }

        // Gráfico 5: Previsão por Categoria
         if (data && data.previsao_por_categoria) {
           generateGraph('grafico5Canvas', data.previsao_por_categoria, 'mes', 'previsao', 'Previsão por Categoria');
          }else {
             console.error("Erro ao gerar gráfico 5, dados de previsão por categoria inválidos:", data);
         }

        // Gráfico 6: Total de Previsão para o Próximo Mês
        if(data && data.total_proximo_mes){
          //formatei os dados para que tenha um label e um valor para ser renderizado corretamente
          generateGraph('grafico6Canvas',[{label:"Total",total: data.total_proximo_mes.total}], 'label', 'total', 'Total de Previsão para o Próximo Mês');
        }else {
            console.error("Erro ao gerar gráfico 6, dados de total próximo mês inválidos:", data);
        }
        // Gráfico 7: Próximos Eventos (dados estáticos, pois você mencionou que esses valores não estão no backend)
        generateGraph('grafico7Canvas', [], 'data_evento', 'evento', 'Próximos Eventos');
        // Gráfico 8: Dados Diarizados de Entrantes Total (dados estáticos, pois você mencionou que esses valores não estão no backend)
         generateGraph('grafico8Canvas', [], 'data', 'total', 'Dados Diarizados de Entrantes Total');
    })
      .catch(error => {
       console.error("Erro ao enviar o arquivo:", error);
       alert("Erro ao processar o arquivo"+ error);
     }).finally(() => {
          document.body.removeChild(loader);
    });
});
});