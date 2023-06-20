// Selecionar os elementos relevantes
const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");
const loginToggle = document.getElementById("loginToggle");
const registerToggle = document.getElementById("registerToggle");

// Adicionar os eventos de clique nos botões de alternância
loginToggle.addEventListener("click", () => {
  toggleForm(loginForm, registerForm);
});

registerToggle.addEventListener("click", () => {
  toggleForm(registerForm, loginForm);
});

// Função para alternar entre os formulários
function toggleForm(showForm, hideForm) {
  // Verificar se o formulário já está ativo
  if (showForm.classList.contains("active")) {
    return;
  }

  // Adicionar classes para controlar as animações
  showForm.classList.add("active", "in");
  hideForm.classList.remove("active", "in");
  hideForm.classList.add("out");

  // Esperar pela conclusão da animação antes de ocultar o formulário antigo
  setTimeout(() => {
    hideForm.classList.remove("out");
    hideForm.style.display = "none";
  }, 300); // Tempo de duração da animação em milissegundos

  // Exibir o novo formulário
  showForm.style.display = "block";
}

// Função para alternar a visibilidade da senha
function togglePasswordVisibility() {
  const passwordInput = document.getElementById(this.dataset.target);
  const passwordToggleIcon = this.querySelector('.password-toggle-icon');

  if (passwordInput.type === 'password') {
    passwordInput.type = 'text';
    passwordToggleIcon.classList.add('visible');
  } else {
    passwordInput.type = 'password';
    passwordToggleIcon.classList.remove('visible');
  }
}

// Associar evento de clique aos elementos de alternância de senha
const passwordToggleElements = document.querySelectorAll('.password-toggle');
passwordToggleElements.forEach(function (passwordToggleElement) {
  passwordToggleElement.addEventListener('click', togglePasswordVisibility.bind(passwordToggleElement));
});
