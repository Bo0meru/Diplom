document.addEventListener('DOMContentLoaded', function () {
	const passwordInput = document.getElementById('id_password_register')
	const confirmPasswordInput = document.getElementById(
		'id_confirm_password_register'
	)
	const requirementsList = document.getElementById('password-requirements')
	const lengthCheck = document.getElementById('length-check')
	const uppercaseCheck = document.getElementById('uppercase-check')
	const lowercaseCheck = document.getElementById('lowercase-check')
	const numberCheck = document.getElementById('number-check')
	const specialCheck = document.getElementById('special-check')
	const matchCheck = document.getElementById('password-match-check')

	const validatePassword = password => {
		// Проверки
		const lengthValid = password.length >= 8
		const uppercaseValid = /[A-Z]/.test(password)
		const lowercaseValid = /[a-z]/.test(password)
		const numberValid = /\d/.test(password)
		const specialValid = /[!@#$%^&*(),.?":{}|<>]/.test(password)

		// Обновление состояния требований
		updateRequirement(lengthCheck, lengthValid)
		updateRequirement(uppercaseCheck, uppercaseValid)
		updateRequirement(lowercaseCheck, lowercaseValid)
		updateRequirement(numberCheck, numberValid)
		updateRequirement(specialCheck, specialValid)

		return (
			lengthValid &&
			uppercaseValid &&
			lowercaseValid &&
			numberValid &&
			specialValid
		)
	}

	const validateMatch = (password, confirmPassword) => {
		const isMatching = password === confirmPassword
		updateRequirement(matchCheck, isMatching)
		return isMatching
	}

	const updateRequirement = (element, isValid) => {
		if (isValid) {
			element.classList.add('valid')
			element.classList.remove('invalid')
		} else {
			element.classList.add('invalid')
			element.classList.remove('valid')
		}
	}

	// Слушатели ввода
	passwordInput.addEventListener('input', function () {
		const isValid = validatePassword(passwordInput.value)
		if (confirmPasswordInput.value) {
			validateMatch(passwordInput.value, confirmPasswordInput.value)
		}
		requirementsList.style.display = isValid ? 'none' : 'block'
	})

	confirmPasswordInput.addEventListener('input', function () {
		validateMatch(passwordInput.value, confirmPasswordInput.value)
	})
})
