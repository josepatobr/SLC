function showMessage(msg, isSuccess = false) {
  erroMsg.textContent = msg;
  erroMsg.style.color = isSuccess ? "green" : "red";
}

function resetButton(btn) {
  btn.disabled = false;
  btn.textContent = "Cadastrar"; }


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
  .then(res => {
  if (!res.ok) {
    throw new Error("Falha na autenticação com Google. Tente novamente.");
  }
  return res.json();
  })
  .then(data => {
      console.log("Resposta do backend:", data);
      localStorage.setItem("access", data.access);
      localStorage.setItem("refresh", data.refresh);
      window.location.href = 'home/';
    })
  .catch(err => {
    console.error("Erro ao enviar token:", err);
    showMessage(err.message || "Erro de conexão ao tentar login com Google."); 
  });
}


// sistema de cadastro
const username = document.getElementById("username");
const full_name = document.getElementById("full_name")
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
      full_name.value.trim() === "" ||
      username.value.trim() === "" ||
      email.value.trim() === "" ||
      password.value.trim() === ""
    ) {
      showMessage("Preencha todos os campos!");
      return;
    }

const emailValido = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value);
  if (!emailValido) {
      showMessage("Digite um e-mail válido!");
    return;
}
  
  if (password.value.trim().length < 8) {
    showMessage("A senha deve ter no mínimo 8 caracteres.");
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
      full_name: full_name.value,
      email: email.value,
      telefone: telefone.value,
      password: password.value,
    }),
})
  .then((response) => response.json())
  .then((data) => {
      resetButton(botao); 
        
  if (data.success) {
    showMessage("Cadastro realizado com sucesso!", true);
    form.reset();
    setTimeout(() => {
      window.location.href = "/home/";
    }, 1500);
    } else {
      showMessage(data.message || "Erro ao cadastrar.");
    }
})
  .catch((error) => {
  resetButton(botao);
  showMessage("Erro de conexão. Tente novamente.");
    console.error("Erro ao enviar:", error);
});
});