document.querySelectorAll('.delete-button').forEach(function(button) {
    button.addEventListener('click', function () {
        const schoolId = this.dataset.schoolId;
        const schoolName = document.querySelector(`.school-text[data-school-id="${schoolId}"]`).innerText;

        const modalContainer = document.getElementById('deleteSchoolConfirmationContainer');
        modalContainer.style.display = 'flex';

        const modalText = modalContainer.querySelector('.school-text');
        modalText.innerText = `Are you sure you want to delete ${schoolName}?`;

        const deleteForm = document.getElementById('deleteForm');
        deleteForm.action = `/Delete_List/${schoolId}/`;
       
    });
});

document.getElementById('deleteNoButton').addEventListener('click', function () {
    document.getElementById('deleteSchoolConfirmationContainer').style.display = 'none';
});

document.getElementById('deleteYesButton').addEventListener('click', function () {
    const deleteForm = document.getElementById('deleteForm');
    deleteForm.submit();
});

document.querySelectorAll('.edit-button').forEach(function (editButton) {
    editButton.addEventListener('click', function () {
        var schoolId = this.getAttribute('data-school-id');
        var textSpan = document.querySelector('.school-text[data-school-id="' + schoolId + '"]');
        var updateContainer = document.getElementById('updateSchoolConfirmationContainer');
        var schoolInput = document.getElementById('editSchoolInput');

        if (textSpan && updateContainer && schoolInput) {
            schoolInput.value = textSpan.textContent;
            updateContainer.style.display = 'flex';
            updateContainer.style.position = 'fixed';
            updateContainer.style.top = '50%';
            updateContainer.style.left = '50%';
            updateContainer.style.transform = 'translate(-50%, -50%)';
        }
    });
});

document.getElementById('updateYesButton').addEventListener('click', function () {
    var schoolId = document.querySelector('.school-text').getAttribute('data-school-id');
    var textSpan = document.querySelector('.school-text[data-school-id="' + schoolId + '"]');
    var schoolInput = document.getElementById('schoolInput');

    if (textSpan && schoolInput) {
        textSpan.textContent = schoolInput.value;
    }
    document.getElementById('updateSchoolConfirmationContainer').style.display = 'none';
});

document.getElementById('updateNoButton').addEventListener('click', function () {
    document.getElementById('updateSchoolConfirmationContainer').style.display = 'none';
});


document.getElementById('goBackButton').addEventListener('click', function () {
    window.location.href = "{% url 'sc_list' %}";
});
