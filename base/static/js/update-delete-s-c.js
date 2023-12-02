document.querySelectorAll('.delete-button').forEach(function(button) {
    button.addEventListener('click', function () {
        const container = this.closest('.container-box');
        const schoolId = container.querySelector('.school-text').dataset.schoolId;
        const schoolName = container.querySelector('.school-text').innerText;

        document.getElementById('deleteConfirmationContainer').style.display = 'flex';
        document.querySelector('#deleteConfirmationContainer .school-text').innerText = `Are you sure you want to delete ${schoolName}?`;

        document.getElementById('deleteConfirmationContainer').dataset.schoolId = schoolId;

        initializeInputBox();
    });
});

document.getElementById('deleteNoButton').addEventListener('click', function () {
    document.getElementById('deleteConfirmationContainer').style.display = 'none';
});

document.getElementById('deleteYesButton').addEventListener('click', function () {
    const schoolId = document.getElementById('deleteConfirmationContainer').dataset.schoolId;

    
    fetch(`/Delete_School_List/${schoolId}/`, {
        method: 'GET',
    })
    .then(response => {
        if (response.ok) {
           
            location.reload();
        } else {
            
            console.error(`Failed to delete school with ID ${schoolId}`);
        }
    })
    .catch(error => {
       
        console.error('Network error:', error);
    })
    .finally(() => {
       
        document.getElementById('deleteConfirmationContainer').style.display = 'none';
    });
});


document.querySelector('.edit-button').addEventListener('click', function () {
    var updateContainer = document.getElementById('updateConfirmationContainer');

    if (updateContainer.style.display === 'none' || updateContainer.style.display === '') {
        updateContainer.style.display = 'flex';
        // Add styles to center the modal
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
        var schoolInput = document.getElementById('schoolInput');

        if (textSpan && updateContainer && schoolInput) {
            schoolInput.value = textSpan.textContent;
            updateContainer.style.display = 'flex';
            // Add styles to center the modal
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

document.getElementById('updateNoButton').addEventListener('click', function () {
    document.getElementById('updateConfirmationContainer').style.display = 'none';
});



document.getElementById('goBackButton').addEventListener('click', function () {
    window.location.href = "{% url 'sc_list' %}";
});