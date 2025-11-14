const video = document.getElementById('Video');

if (video) {
    const movieId = video.dataset.movieId; 
    
    let tempoAssistido = 0;
    let intervalo = null; 

    function stopCounting() {
        if (intervalo) {
            clearInterval(intervalo);
            intervalo = null;
        }
    }

    function incrementWatchCount() {
        const hasWatched = localStorage.getItem(`watched_${movieId}`);
        

        const csrfToken = video.dataset.csrfToken;
        const counterUrl = video.dataset.counterUrl;

        if (!movieId) {
             console.error("Erro: movie.id não encontrado no dataset.");
             return;
        }

        if (!hasWatched) {
        fetch(counterUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken, 
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        })
            .then(res => {
                if (!res.ok) {
                    throw new Error(`Erro HTTP ${res.status}: Falha ao atualizar contador.`);
                }
                return res.json();
            })
            .then(data => {
                localStorage.setItem(`watched_${movieId}`, true);
                console.log('Contador atualizado:', data.watch_count);
            })
            .catch(err => {
                console.error('Erro no contador do backend:', err.message);
            });
        }
    }


    // --- LISTENERS ---
    video.addEventListener('play', () => {
        if (video.currentTime === 0) {
             tempoAssistido = 0;
        }

        if (!intervalo) {
            intervalo = setInterval(() => {
                tempoAssistido += 1;
            }, 1000);
        }
        
        incrementWatchCount();
    });

    video.addEventListener('pause', () => {
        stopCounting();
        console.log(`Assistido até agora: ${tempoAssistido} segundos`);
    });

    video.addEventListener('ended', () => {
        stopCounting();
        console.log(`Vídeo completo assistido: ${tempoAssistido} segundos`);

    });

    video.addEventListener('seeking', stopCounting); 
} else {
    console.error("Elemento de vídeo com ID 'Video' não encontrado.");
}




// sistema de estrela 
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('ratingForm');
    
    const messageElement = document.getElementById('ratingMessage'); 

    if (form) {
        const radioButtons = form.querySelectorAll('input[name="nota"]');

        radioButtons.forEach(radio => {
            radio.addEventListener('change', function() {
                submitRating(form, messageElement); 
            });
        });
    }
});

function submitRating(formElement, messageElement) {
    const url = formElement.action;
    const csrfToken = formElement.querySelector('[name="csrfmiddlewaretoken"]').value;
    const selectedNote = formElement.querySelector('input[name="nota"]:checked').value;
    
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', csrfToken);
    formData.append('nota', selectedNote);
    
    messageElement.textContent = 'Enviando avaliação...';
    messageElement.classList.remove('text-red-500'); 
    messageElement.classList.add('text-yellow-400');
    
    fetch(url, {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Falha no servidor ao processar a nota.');
        }
        return response.json(); 
    })
    .then(data => {
        console.log('Avaliação salva com sucesso!', data);
        messageElement.textContent = 'Nota ' + selectedNote + ' registrada! 🎉';
        messageElement.classList.remove('text-yellow-400');
        messageElement.classList.add('text-green-500');
    })
    .catch(error => {
        console.error('Erro:', error);
        messageElement.textContent = 'Erro ao salvar: ' + error.message;
        messageElement.classList.remove('text-yellow-400');
        messageElement.classList.add('text-red-500');
    });
}