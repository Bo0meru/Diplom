document.addEventListener('DOMContentLoaded', function () {
	const form = document.getElementById('edit-question-form')
	const answerTexts = document.querySelectorAll('.answer-text')

	form.addEventListener('submit', function () {
		answerTexts.forEach(answerText => {
			const answerId = answerText.getAttribute('data-answer-id')
			const hiddenInput = document.getElementById(
				`hidden-answer-text-${answerId}`
			)
			hiddenInput.value = answerText.innerText.trim()
		})
	})
})
