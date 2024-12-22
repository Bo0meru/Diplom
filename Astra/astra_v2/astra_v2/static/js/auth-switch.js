document.addEventListener('DOMContentLoaded', function () {
	console.log('JS подключен')

	const btnLogin = document.getElementById('login')
	const btnRegister = document.getElementById('register')
	const loginForm = document.getElementById('login-form')
	const registerForm = document.getElementById('register-form')

	function showLoginForm() {
		loginForm.style.display = 'block'
		registerForm.style.display = 'none'
	}

	function showRegisterForm() {
		loginForm.style.display = 'none'
		registerForm.style.display = 'block'
	}

	btnLogin.addEventListener('change', function () {
		if (btnLogin.checked) {
			showLoginForm()
		}
	})

	btnRegister.addEventListener('change', function () {
		if (btnRegister.checked) {
			showRegisterForm()
		}
	})

	// Инициализация: показываем одну форму по умолчанию
	if (btnLogin.checked) {
		showLoginForm()
	} else if (btnRegister.checked) {
		showRegisterForm()
	}
})
