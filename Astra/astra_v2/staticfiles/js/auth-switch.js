document.addEventListener('DOMContentLoaded', function () {
	console.log('JS подключен')

	const btnLogin = document.getElementById('login')
	const btnRegister = document.getElementById('register')
	const loginForm = document.getElementById('login-form')
	const registerForm = document.getElementById('register-form')

	btnLogin.addEventListener('change', function () {
		if (btnLogin.checked) {
			loginForm.style.display = 'block'
			registerForm.style.display = 'none'
		}
	})

	btnRegister.addEventListener('change', function () {
		if (btnRegister.checked) {
			loginForm.style.display = 'none'
			registerForm.style.display = 'block'
		}
	})
})
