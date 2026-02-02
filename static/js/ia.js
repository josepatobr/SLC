const IA = document.getElementById('chat-form')
const inputMensagem = document.getElementById('chat-input'); 
const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    if (IA && inputMensagem){
        IA.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const mensagem = inputMensagem.value;
        if (!mensagem.trim()) return;
        
        fetch("api/chat/", {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken, 
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'question': mensagem
                })
            })
            .then(res => {
                if (!res.ok) {
                    throw new Error(`Erro HTTP ${res.status}: Falha ao mandar mensagem pra IA.`);
                }
                return res.json();
            })
            .then(data => {
                console.log('Resposta da IA:', data);
                const chatLog = document.getElementById('chat-container');
                chatLog.innerHTML += `<p><b>IA:</b> ${data.question}</p>`;
                inputMensagem.value = '';
            })
            .catch(err => {
                console.error('Erro no sistema:', err.message);
            });
        }
    )}
    




