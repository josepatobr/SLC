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