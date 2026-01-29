

function checkout() {
    const btn = document.getElementById('checkout-button'); 
    const originalText = btn.innerHTML;

    btn.disabled = true;
    btn.innerHTML = `
        <svg class="animate-spin h-5 w-5 mr-3 inline-block" viewBox="0 0 24 24"></svg>
        Processando...
    `;

    fetch("create-checkout-session/", {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => {
        if (!response.ok) throw new Error('Falha na resposta do servidor');
        return response.json();
    })
    .then(session => {
        if (session.url) {
            window.location.href = session.url;
        } else {
            throw new Error('URL de checkout não encontrada');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Ocorreu um erro ao processar seu pagamento. Tente novamente.');
        
        btn.disabled = false;
        btn.innerHTML = originalText;
    });
}
