document.addEventListener('DOMContentLoaded', function () {
	const searchBar = document.getElementById('search-bar')
	const questionItems = document.querySelectorAll('.question-item')

	searchBar.addEventListener('input', function () {
		const query = searchBar.value.toLowerCase()
		questionItems.forEach(item => {
			const questionText = item.querySelector('p').textContent.toLowerCase()
			if (questionText.includes(query)) {
				item.style.display = 'block'
			} else {
				item.style.display = 'none'
			}
		})
	})
})
