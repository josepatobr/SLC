const IA = document.getElementById('chat-form')
const inputMensagem = document.getElementById('chat-input'); 
const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    if (IA && inputMensagem){
        IA.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const mensagem = inputMensagem.value;
        if (!mensagem.trim()) return;
        
        fetch("/chat/", {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken, 
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'message': mensagem
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
                chatLog.innerHTML += `<p><b>IA:</b> ${data.message}</p>`;
                inputMensagem.value = '';
            })
            .catch(err => {
                console.error('Erro no sistema:', err.message);
            });
        }
    )}
    



const form = document.getElementById('chat-form');
const btn = document.getElementById('submit-btn');
const loading = document.getElementById('loading');

    form.onsubmit = function() {
        btn.disabled = true;
        btn.innerText = "Aguarde...";
        loading.classList.remove('hidden');
    };


