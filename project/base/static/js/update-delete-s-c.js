document.querySelectorAll('.delete-button').forEach(function(button) {
    button.addEventListener('click', function () {
        const container = this.closest('.container-box');
        const schoolId = container.querySelector('.school-text').dataset.schoolId;
        const schoolName = container.querySelector('.school-text').innerText;

        const modalContainer = document.getElementById('deleteConfirmationContainer');
        modalContainer.style.display = 'flex';

        const modalText = modalContainer.querySelector('.school-text');
        modalText.innerText = `Are you sure you want to delete ${schoolName}?`;

        const deleteForm = document.getElementById('deleteForm');
        deleteForm.action = `/Delete_List/${schoolId}/`;
        deleteForm.querySelector('[name="delete_type"]').value = 'school';
        deleteForm.dataset.schoolId = schoolId;

        initializeInputBox();
    });
});

document.getElementById('deleteNoButton').addEventListener('click', function () {
    document.getElementById('deleteConfirmationContainer').style.display = 'none';
});

document.getElementById('deleteYesButton').addEventListener('click', function () {
    const deleteForm = document.getElementById('deleteForm');
    deleteForm.submit();
});



document.querySelector('.edit-button').addEventListener('click', function () {
    var updateContainer = document.getElementById('updateConfirmationContainer');

    if (updateContainer.style.display === 'none' || updateContainer.style.display === '') {
        updateContainer.style.display = 'flex';
        updateContainer.style.position = 'fixed';
        updateContainer.style.top = '50%';
        updateContainer.style.left = '50%';
        updateContainer.style.transform = 'translate(-50%, -50%)';
    } else {
        updateContainer.style.display = 'none';
    }
});

document.querySelectorAll('.edit-button').forEach(function (editButton) {
    editButton.addEventListener('click', function () {
        var schoolId = this.getAttribute('data-school-id');
        var textSpan = document.querySelector('.school-text[data-school-id="' + schoolId + '"]');
        var updateContainer = document.getElementById('updateConfirmationContainer');
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
    document.getElementById('updateConfirmationContainer').style.display = 'none';
});

document.getElementById('updateNoButton').addEventListener('click', function (event) {
    event.preventDefault(); 
    console.log('No button clicked');
    document.getElementById('updateConfirmationContainer').style.display = 'none';
    return false;
});





document.getElementById('goBackButton').addEventListener('click', function () {
    window.location.href = "{% url 'sc_list' %}";
});