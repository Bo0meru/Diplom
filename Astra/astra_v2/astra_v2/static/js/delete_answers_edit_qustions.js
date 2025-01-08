document.addEventListener('DOMContentLoaded', function () {
	const deleteButtons = document.querySelectorAll('.btn-delete-answer')
	const deletedAnswersInput = document.getElementById('deleted-answers')

	deleteButtons.forEach(button => {
		button.addEventListener('click', function () {
			const answerId = this.dataset.answerId
			const answerElement = document.getElementById(`answer-${answerId}`)
			if (answerElement) answerElement.remove() // Удаление с интерфейса

			const deletedAnswers = deletedAnswersInput.value
				.split(',')
				.filter(Boolean)
			if (!deletedAnswers.includes(answerId)) {
				deletedAnswers.push(answerId)
			}
			deletedAnswersInput.value = deletedAnswers.join(',')
		})
	})

	const addAnswerBtn = document.getElementById('add-answer-btn')
	const answerContainer = document.querySelector('.answer-container')

	addAnswerBtn.addEventListener('click', function () {
		const newAnswer = document.createElement('div')
		newAnswer.classList.add('answer-item')
		newAnswer.innerHTML = `
            <input type="text" name="new_answers[]" class="answer-text" placeholder="Введите ответ" required>
            <label class="correct-label">
                <input type="checkbox" name="new_correct_answers[]">
                Верный
            </label>
            <button type="button" class="btn-delete-answer">Удалить</button>
        `
		answerContainer.appendChild(newAnswer)

		const deleteBtn = newAnswer.querySelector('.btn-delete-answer')
		deleteBtn.addEventListener('click', function () {
			newAnswer.remove()
		})
	})
})
