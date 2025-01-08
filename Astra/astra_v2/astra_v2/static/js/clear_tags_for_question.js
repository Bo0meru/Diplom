document.addEventListener('DOMContentLoaded', function () {
	const clearrTagsButton = document.getElementById('clearr-tags')
	const tagCheckboxes = document.querySelectorAll(
		".tags-grid .tag-item input[type='checkbox']"
	)

	if (clearrTagsButton) {
		clearrTagsButton.addEventListener('click', function () {
			tagCheckboxes.forEach(checkbox => {
				checkbox.checked = false // Снимаем отметку с каждого чекбокса
			})
		})
	}
})
