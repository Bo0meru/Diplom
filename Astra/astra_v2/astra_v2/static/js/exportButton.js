// Обработчик нажатия на кнопку "Выгрузить вопросы"
const exportButton = document.getElementById('export-button')
exportButton.addEventListener('click', () => {
	const exportedQuestions = Array.from(
		document.querySelectorAll('#export-list .question-item')
	).map(item => item.dataset.id)

	if (exportedQuestions.length === 0) {
		alert('Нет вопросов для выгрузки!')
		return
	}

	// Отправляем запрос на сервер
	fetch('/dashboard/export-questions/', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({ questions: exportedQuestions }),
	})
		.then(response => {
			if (!response.ok) {
				throw new Error('Ошибка сервера')
			}
			return response.blob() // Получаем файл в виде Blob
		})
		.then(blob => {
			const url = window.URL.createObjectURL(blob)
			const a = document.createElement('a')
			a.style.display = 'none'
			a.href = url
			a.download = 'exported_questions.docx' // Имя файла
			document.body.appendChild(a)
			a.click()
			window.URL.revokeObjectURL(url) // Освобождаем память
		})
		.catch(error => {
			console.error('Ошибка выгрузки:', error)
			alert('Ошибка при выгрузке вопросов.')
		})
})
