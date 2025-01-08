document.addEventListener('DOMContentLoaded', function () {
	const form = document.getElementById('edit-question-form')
	const editableText = document.getElementById('question-text')
	const hiddenInput = document.getElementById('hidden-question-text')

	form.addEventListener('submit', function () {
		// Перед отправкой формы обновляем скрытое поле
		hiddenInput.value = editableText.innerText.trim()
	})
})
