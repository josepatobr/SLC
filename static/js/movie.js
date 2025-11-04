const movieId = { movie_id };
const video = document.getElementById('Video');

video.addEventListener('play', () => {
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