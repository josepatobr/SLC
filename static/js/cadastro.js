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
    


  const username = document.getElementById("username");
  const email = document.getElementById("email");
  const telefone = document.getElementById("telefone");
  const password = document.getElementById("password");
  const form = document.getElementById("form-cadastro");
  const erroMsg = document.getElementById("erro-msg");
  const botao = document.querySelector("button[type='submit']");
  const togglePassword = document.getElementById("toggle-password");

  togglePassword.addEventListener("click", function () {
    if (password.type === "password") {
      password.type = "text";
      togglePassword.textContent = "🙈";
    } else {
      password.type = "password";
      togglePassword.textContent = "👁️";
    }
  });

  form.addEventListener("submit", function (event) {
    event.preventDefault();

    if (
      username.value.trim() === "" ||
      email.value.trim() === "" ||
      password.value.trim() === ""
    ) {
      erroMsg.textContent = "Preencha todos os campos!";
      erroMsg.style.color = "red";
      return;
    }

    const emailValido = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value);
    if (!emailValido) {
      erroMsg.textContent = "Digite um e-mail válido!";
      erroMsg.style.color = "red";
      return;
    }

    botao.disabled = true;
    botao.textContent = "Enviando...";

    fetch("/api/auth/cadastro/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: username.value,
        email: email.value,
        telefone: telefone.value,
        password: password.value,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        botao.disabled = false;
        botao.textContent = "Cadastrar";

        if (data.success) {
          erroMsg.textContent = "Cadastro realizado com sucesso!";
          erroMsg.style.color = "green";
          form.reset();
          setTimeout(() => {
            window.location.href = "/home/";
          }, 1500);
        } else {
          erroMsg.textContent = data.message || "Erro ao cadastrar.";
          erroMsg.style.color = "red";
        }
      })
      .catch((error) => {
        botao.disabled = false;
        botao.textContent = "Cadastrar";
        erroMsg.textContent = "Erro de conexão. Tente novamente.";
        erroMsg.style.color = "red";
        console.error("Erro ao enviar:", error);
      });
  });