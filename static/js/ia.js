document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('chat-form');
    const inputMensagem = document.getElementById('chat-input');
    const chatContainer = document.getElementById('chat-container');
    const loading = document.getElementById('loading');
    const btn = document.getElementById('submit-btn');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const mensagem = inputMensagem.value.trim();
            if (!mensagem) return;

            btn.disabled = true;
            btn.innerText = "Aguarde...";
            loading.classList.remove('hidden');

            const placeholder = chatContainer.querySelector('.flex-col.items-center');
            if (placeholder) placeholder.remove();

            try {
                const response = await fetch("/api/ia/chat/", {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ 'question': mensagem })
                });

                if (!response.ok) throw new Error('Erro na API');

                const data = await response.json();

                const htmlResposta = `
                    <div class="space-y-4 mb-6">
                        <div class="flex items-center gap-2">
                            <span class="h-2 w-2 bg-blue-500 rounded-full animate-pulse"></span>
                            <h3 class="text-gray-400 uppercase tracking-widest text-xs font-bold">Resposta da Assistente</h3>
                        </div>
                        <div class="bg-gray-700/50 rounded-lg p-4 border border-gray-600 text-gray-200 leading-relaxed">
                            ${data.response.replace(/\n/g, '<br>')}
                        </div>
                    </div>
                `;

                loading.insertAdjacentHTML('beforebegin', htmlResposta);
                
                inputMensagem.value = '';
                chatContainer.scrollTop = chatContainer.scrollHeight;

            } catch (err) {
                console.error('Erro:', err);
                alert('Erro ao consultar a IA.');
            } finally {
                btn.disabled = false;
                btn.innerText = "Enviar";
                loading.classList.add('hidden');
            }
        });
    }
});

