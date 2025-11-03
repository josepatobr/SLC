document.getElementById('Video').addEventListener('play', () => {
    fetch("{% url 'CounterView' movie.id %}", {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    });
});