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
            window.location.href = '/home/';
        })
        .catch(err => {
        console.error("Erro ao enviar token:", err);
      });
    }
    
    
    const select = document.getElementById("opcao");
    const emailCodeSection = document.getElementById("email-code-section");
    const smsCodeSection = document.getElementById("sms-code-section");
    const emailPasswordSection = document.getElementById("email-password-section");

    function atualizarSecao() {
        const value = select.value;

        emailCodeSection.classList.add("hidden");
        smsCodeSection.classList.add("hidden");
        emailPasswordSection.classList.add("hidden");

        if (value === "codigo-email") {
        emailCodeSection.classList.remove("hidden");
        } else if (value === "codigo-sms") {
        smsCodeSection.classList.remove("hidden");
        } else if (value === "senha-email") {
        emailPasswordSection.classList.remove("hidden");
        }
    }

    select.addEventListener("change", atualizarSecao);
    window.addEventListener("DOMContentLoaded", atualizarSecao);

    // sistema de enviar dados
    const enviarBtn = document.getElementById("enviar");
    const popup = document.getElementById("popup-codigo");
    const fecharPopup = document.getElementById("fechar-popup");
    const confirmarCodigo = document.getElementById("confirmar-codigo");

   
    function enviarCodigo(endpoint, payload) {
    fetch(`http://localhost:8000/api/auth/${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        console.log("Código enviado:", data);
        popup.style.display = "block";
    })
    .catch(err => {
        console.error("Erro ao enviar:", err);
        alert("Erro ao enviar o código.");
    });
}

// botao enviar
    enviarBtn.addEventListener("click", () => {
    const modo = document.getElementById("opcao").value;

    if (modo === "codigo-email") {
        const email = document.getElementById("email").value;
        if (!email) {
            alert("Digite seu email.");
        return;
        }
    enviarCodigo("enviar-codigo/", { email });

    } else if (modo === "codigo-sms") {
        const telefone = document.getElementById("telefone").value;
        if (!telefone) {
            alert("Digite seu telefone.");
        return;
        }
    enviarCodigo("enviar-codigo/", { telefone });

    } else {
        alert("Selecione um modo válido.");
    }
});

// sistema de enviar
    confirmarCodigo.addEventListener("click", () => {
        const modo = document.getElementById("opcao").value;
        const codigo = document.getElementById("codigo-digitado").value;

        let payload = {};
        let endpoint = "";

        if (modo === "codigo-email") {
            const email = document.getElementById("email").value;
            payload = { email, codigo };
            endpoint = "login-email-codigo/";

        } else if (modo === "codigo-sms") {
            const telefone = document.getElementById("telefone").value;
            payload = { telefone, codigo };
            endpoint = "login-sms/";
        }

    fetch(`http://localhost:8000/api/auth/${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        console.log("Login confirmado:", data);
        popup.style.display = "none";

        if (data.access && data.refresh) {
            localStorage.setItem("access", data.access);
            localStorage.setItem("refresh", data.refresh);
            window.location.href = "/home/";
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
        popup.style.display = "none";
    });

