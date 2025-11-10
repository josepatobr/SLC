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
        window.location.href = 'home/';
    })
    .catch(err => {
    console.error("Erro ao enviar token:", err);
    });
}
    
//sistema de trocas

function changeOption() {
    const authModeSelect = document.getElementById("opcao");
    const defaultAuthMode = "senha-email";
    const authModeMap = {
        "senha-email": "email-password-section",
        "codigo-email": "email-code-section",
        "codigo-sms": "sms-code-section"
    };
    
    if (!authModeSelect) return;

    const selectedValue = authModeSelect.value || defaultAuthMode;
    const targetElement = document.getElementById(authModeMap[selectedValue]);
        if (!targetElement) return;

    for (const mode in authModeMap) {
        const element = document.getElementById(authModeMap[mode]);
        if (!element) continue;

        if (mode === selectedValue) {
            element.classList.replace("hidden", "block")
        } else {
            element.classList.replace("block", "hidden")
        }
    }
}
authModeSelect.addEventListener("change", changeOption);


//sistema de enviar dados pra api
const enviarBtn = document.getElementById("EnviarDados");
function EnviarDados(endpoint, payload) {

    fetch(`http://localhost:8000/api/auth/${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => {
        if (!res.ok) throw new Error("Erro na resposta da API");
        return res.json();
    })
    .then(data => {
        localStorage.setItem("token", data.token);
        console.log("Login bem-sucedido:", data);
        window.location.href = "home/";
    })
    .catch(err => {
        console.error("Erro ao enviar:", err);
        alert("Email ou senha inválidos.");
    });
}


//botao enviar

enviarBtn.addEventListener("click", () => {
    const modo = document.getElementById("opcao").value;
    const email = getValue("login-email");
    const senha = getValue("login-password");
    const telefone = getValue("code-telefone");
    const getValue = (id) => document.getElementById(id)?.value?.trim();

    const validarCampo = (valor, mensagem) => {
        if (!valor) {
            alert(mensagem);
            return false;
        }
        return true;
    };

    switch (modo) {
        case "codigo-email":
            if (!validarCampo(email, "Digite seu email.")) return;
                EnviarDados("enviar-codigo/", { email });
                mostrarPopup("email");
        break;

        case "senha-email":
            if (!validarCampo(email, "Digite seu email.")) return;
            if (!validarCampo(senha, "Digite sua senha.")) return;
                EnviarDados("login-email/", { email, senha });
            break;

         case "codigo-sms":
            if (!validarCampo(telefone, "Digite seu telefone.")) return;
                EnviarDados("enviar-codigo/", { telefone });
                mostrarPopup("sms");
            break;
        default:
            alert("Selecione um modo válido.");
}});


//PopUp

function mostrarPopup(tipo) {
const popup = document.getElementById("popup-codigo");
const titulo = document.getElementById("popup-titulo");

  if (popup) {
    titulo.textContent = tipo === "sms" ? "Digite o código recebido por SMS" : "Digite o código recebido por Email";
    popup.classList.remove("hidden");
    popup.classList.add("block");
  }
}

//sistema de confirmar codigo
confirmarCodigo.addEventListener("click", () => {
    const modo = document.getElementById("opcao").value;
    const codigo = document.getElementById("codigo").value?.trim();

    if (!codigo || codigo.length !== 6) {
        alert("Digite um código válido de 6 dígitos.");
        return;
    }

    let payload = {};
    let endpoint = "";

    if (modo === "codigo-email") {
        const email = document.getElementById("login-email").value?.trim();
        if (!email) return alert("Email não encontrado.");
            payload = { email, codigo };
            endpoint = "login-email-codigo/";
        } 
        else if (modo === "codigo-sms") {
            const telefone = document.getElementById("code-telefone").value?.trim();
        
            if (!telefone) return alert("Telefone não encontrado.");
            payload = { telefone, codigo };
            endpoint = "login-sms/";
        } 
        else {
            alert("Modo inválido.");
        return;
    }

        fetch(`http://localhost:8000/api/auth/${endpoint}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        })
        .then(res => {
            if (!res.ok) throw new Error("Código inválido ou expirado.");
            return res.json();
        })
        .then(data => {
            console.log("Login confirmado:", data);
            popup.classList.add("hidden");
            popup.classList.remove("block");

        if (data.access && data.refresh) {
            localStorage.setItem("access", data.access);
            localStorage.setItem("refresh", data.refresh);
            window.location.href = "home/";
        } else {
            alert("Código inválido ou expirado.");
        }
    })
        .catch(err => {
            console.error("Erro ao confirmar código:", err);
            alert("Erro ao verificar o código.");
        });
});

fecharPopup.addEventListener("click", () => {
    popup.classList.add("hidden");
    popup.classList.remove("block");
});

