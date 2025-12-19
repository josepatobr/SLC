const authModeSelect = document.getElementById("opcao");
const enviarBtn = document.getElementById("EnviarDados");
const confirmarCodigo = document.getElementById("confirmarCodigo");
const fecharPopup = document.getElementById("fecharPopup"); 
const popup = document.getElementById("popup-codigo"); 

// 2. FUNÇÕES UTILITÁRIAS
function setAuthTokens(data) {
    if (data.access) {
        localStorage.setItem("access", data.access);
    }
    if (data.refresh) { 
        localStorage.setItem("refresh", data.refresh);
    }
    localStorage.removeItem("token"); 
}

function redirectToHome() {
    window.location.href = "home/";
}


//sistema de login com o google
function handleCredentialResponse(response){
    const jwt = response.credential;
    console.log("Token jwt recebido", jwt);

    fetch('http://localhost:8000/api/auth/login-google/',{ 
    method: 'POST',
    headers: {
        'Content-Type':'application/json'
    },
    body: JSON.stringify({ token:jwt})
    })
    .then(res=>res.json())
    .then(data => {
        console.log("Resposta do backend:", data);
        localStorage.setItem("access", data.access);
        localStorage.setItem("refresh", data.refresh);
        localStorage.setItem("user_email", data.usuario);
        window.location.href = '/home/';
    })
    .catch(err => {
    console.error("Erro ao enviar token:", err);
    });
}
    
//sistema de trocas
function changeOption() {
    if (!authModeSelect) return;

    const authModeMap = {
        "senha-email": "email-password-section",
        "codigo-email": "email-code-section",
        "codigo-sms": "sms-code-section"
    };

    const selectedValue = authModeSelect.value || "senha-email";
    
    for (const mode in authModeMap) {
        const element = document.getElementById(authModeMap[mode]);
        if (!element) continue;

        if (mode === selectedValue) {
            element.classList.remove("hidden");
            element.classList.add("block");
        } else {
            element.classList.remove("block");
            element.classList.add("hidden");
        }
    }
}

if (authModeSelect) {
    authModeSelect.addEventListener("change", changeOption);
}


//sistema de enviar dados pra api
function EnviarDados(endpoint, payload) {
    fetch(`http://localhost:8000/api/auth/${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(async res => {
        if (!res.ok) {
            let errorDetail = "Erro desconhecido na autenticação.";
            try {
                const errorData = await res.json();
                errorDetail = errorData.detail || errorData.error || errorDetail; 
            } catch (e) {
                errorDetail = `Erro HTTP: ${res.status}.`; 
            }
            throw new Error(errorDetail);
        }
        return res.json();
    })
    .then(data => {
        console.log("Resposta do Backend:", data);

        setAuthTokens(data);

        if (data.access) {
            console.log("Login bem-sucedido. Redirecionando...");
            redirectToHome();
        } else {
            alert("Sucesso, mas sem tokens recebidos. Falha na autenticação.");
        }
    })
    .catch(err => {
        console.error("Erro ao enviar:", err);
        alert(err.message || "Erro de conexão com o servidor. Tente novamente."); 
    });
}

//botao enviar
const getValue = (id) => document.getElementById(id)?.value?.trim() || "";

const validarCampo = (valor, mensagem) => {
    if (!valor) {
        alert(mensagem);
        return false;
    }
    return true;
};

if (enviarBtn) {
    enviarBtn.addEventListener("click", () => {
        const modo = getValue("opcao"); 
        const email = getValue("login-email");
        const senha = getValue("login-password");
        const telefone = getValue("code-telefone");
    
        switch (modo) {
            case "codigo-email":
                if (!validarCampo(email, "Digite seu email.")) return;
                fetchAndHandleCodeSend("enviar-codigo/", { email }, "email"); 
                break;

            case "senha-email":
                if (!validarCampo(email, "Digite seu email.")) return;
                if (!validarCampo(senha, "Digite sua senha.")) return;
                EnviarDados("login-email/", { email, senha }); 
                break;

            case "codigo-sms":
                if (!validarCampo(telefone, "Digite seu telefone.")) return;
                fetchAndHandleCodeSend("enviar-codigo/", { telefone }, "sms");
                break;
                
            default:
                alert("Selecione um modo válido.");
        }
    });
}

function fetchAndHandleCodeSend(endpoint, payload, tipo) {
    fetch(`http://localhost:8000/api/auth/${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => {
        if (!res.ok) throw new Error("Erro ao enviar código. Verifique os dados e tente novamente.");
        return res.json();
    })
    .then(() => {
        mostrarPopup(tipo); 
        console.log(`Pedido de código enviado com sucesso para ${tipo}.`);
    })
    .catch(err => {
        console.error("Erro ao enviar código:", err);
        alert(err.message || "Falha na comunicação com o servidor.");
    });
}

//PopUp

function mostrarPopup(tipo) {
    const popup = document.getElementById("popup-codigo");
    const titulo = document.getElementById("popup-titulo");

    if (popup && titulo) {
        titulo.textContent = tipo === "sms" 
            ? "Digite o código recebido por SMS" 
            : "Digite o código recebido por Email";
        
        popup.classList.remove("hidden");
        popup.classList.add("block");
    } else {
        console.error("Erro: Elementos 'popup-codigo' ou 'popup-titulo' não encontrados no DOM.");
    }
}

//sistema de confirmar codigo

if (confirmarCodigo) {
    confirmarCodigo.addEventListener("click", () => {
        const modo = getValue("opcao"); 
        const codigo = getValue("codigo");
        
        if (!codigo || codigo.length !== 6) {
            alert("Digite um código válido de 6 dígitos.");
            return;
        }

        let payload = { codigo };
        let endpoint = "";
        let identificador = ""; 

        if (modo === "codigo-email") {
            identificador = getValue("login-email");
            if (!identificador) return alert("Email não encontrado. Tente enviar o código novamente.");
            payload.email = identificador;
            endpoint = "login-email-codigo/";
        } else if (modo === "codigo-sms") {
            identificador = getValue("code-telefone");
            if (!identificador) return alert("Telefone não encontrado. Tente enviar o código novamente.");
            payload.telefone = identificador;
            endpoint = "login-sms/";
        } else {
            alert("Modo inválido. Feche o popup e selecione o modo novamente.");
            return;
        }

        fetch(`http://localhost:8000/api/auth/${endpoint}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        })
        .then(async res => {
            if (!res.ok) {
                let errorDetail = "Código inválido ou expirado.";
                try {
                    const errorData = await res.json();
                    errorDetail = errorData.detail || errorData.error || errorDetail;
                } catch (e) {
                }
                throw new Error(errorDetail);
            }
            return res.json();
        })
        .then(data => {
            console.log("Login confirmado:", data);
            
            if (popup) {
                popup.classList.add("hidden");
                popup.classList.remove("block");
            }

            setAuthTokens(data); 

            if (data.access) {
                window.location.href = "home/";
            } else {
                alert("Autenticação bem-sucedida, mas sem tokens recebidos. Tente o login manual.");
            }
        })
        .catch(err => {
            console.error("Erro ao confirmar código:", err);
            alert(err.message || "Erro de conexão ao verificar o código.");
        });
    });
}

if (fecharPopup && popup) {
    fecharPopup.addEventListener("click", () => {
        popup.classList.add("hidden");
        popup.classList.remove("block");
    });
}