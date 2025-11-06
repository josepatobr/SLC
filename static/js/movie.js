const movieId = video.dataset.movieId;
const video = document.getElementById('Video');

let tempoAssistido = 0;
let intervalo;


video.addEventListener('play', () => {
    intervalo = setInterval(() => {
        tempoAssistido += 1;
    }, 1000);

    const hasWatched = localStorage.getItem(`watched_${movieId}`);
    if (!hasWatched) {
        fetch("{% url 'CounterView' movie.id %}", {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        })
        .then(res => res.json())
        .then(data => {
            localStorage.setItem(`watched_${movieId}`, true);
            console.log('Contador atualizado:', data.watch_count);
        });
    }
});

video.addEventListener('pause', () => {
    clearInterval(intervalo);
    console.log(`Assistido até agora: ${tempoAssistido} segundos`);
});

video.addEventListener('ended', () => {
    clearInterval(intervalo);
    console.log(`Vídeo completo assistido: ${tempoAssistido} segundos`);
});