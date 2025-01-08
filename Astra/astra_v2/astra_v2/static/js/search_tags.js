document.addEventListener('DOMContentLoaded', function () {
	const searchBar = document.getElementById('tags-search-bar')
	const tagsGrid = document.querySelectorAll('.tags-grid .tag-item')

	if (searchBar) {
		searchBar.addEventListener('input', function () {
			const searchQuery = this.value.toLowerCase()

			tagsGrid.forEach(tag => {
				const tagText = tag.textContent.toLowerCase()
				if (tagText.includes(searchQuery)) {
					tag.style.display = 'flex' // Показываем совпавшие элементы
				} else {
					tag.style.display = 'none' // Скрываем остальные
				}
			})
		})
	}
})
