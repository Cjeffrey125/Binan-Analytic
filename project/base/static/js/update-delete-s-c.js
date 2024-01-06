document.addEventListener("DOMContentLoaded", function () {
    const editButtons = document.querySelectorAll('.edit-button');
    const updateForm = document.getElementById('updateForm');
    const editSchoolName = document.getElementById('editSchoolName');
    const editSchoolId = document.getElementById('editSchoolId');
    const editSchoolInput = document.getElementById('editSchoolInput');

    editButtons.forEach(editButton => {
        editButton.addEventListener('click', function () {
            const schoolId = this.getAttribute('data-school-id');
            const schoolName = this.parentNode.parentNode.querySelector('.school-text').innerText;

            updateForm.action = `/Update_School_List/${schoolId}/`;
            editSchoolName.innerText = schoolName;
            editSchoolId.innerText = schoolId;
            editSchoolInput.value = schoolName;
        });
    });

    var buttons = document.querySelectorAll('.update-course-button');

    buttons.forEach(function (button) {
        button.addEventListener('click', function () {
            var dropdown = this.closest('.course-container').querySelector('.dropdown-content');
            dropdown.style.display = (dropdown.style.display === 'block') ? 'none' : 'block';
        });
    });

    var deleteButtons = document.querySelectorAll('.delete-course-button');
    var itemIdInput = document.getElementById('courseIdInput');
    var itemTypeInput = document.getElementById('itemTypeInput');
    var deleteItemForm = document.getElementById('deleteCourseForm');
    var deleteCourseConfirmationContainer = document.getElementById('deleteCourseConfirmationContainer');

    if (deleteItemUrl) {
        deleteItemForm.action = deleteItemUrl.replace('dummy', 'course').replace('0', 43);
    }

    deleteButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            var itemId = button.getAttribute('data-course-id');
            itemIdInput.value = itemId;

            var itemType = 'course';
            itemTypeInput.value = itemType;

            if (deleteItemUrl) {
                deleteItemForm.action = deleteItemUrl.replace('dummy', itemType).replace('0', itemId);
            }
            
            deleteCourseConfirmationContainer.style.display = 'flex';
            deleteCourseConfirmationContainer.style.position = 'fixed';
            deleteCourseConfirmationContainer.style.top = '50%';
            deleteCourseConfirmationContainer.style.left = '50%';
            deleteCourseConfirmationContainer.style.transform = 'translate(-50%, -50%)';
        });
    });

    document.getElementById('deleteCourseNoButton').addEventListener('click', function () {
        deleteCourseConfirmationContainer.style.display = 'none';
    });
});

document.addEventListener('DOMContentLoaded', function () {
    var updateLinks = document.querySelectorAll('.update-course-link');
    var editCourseInput = document.getElementById('editCourseInput');
    var editCourseIdInput = document.getElementById('editCourseIdInput');
    var editAcronymInput = document.getElementById('editAcronymInput');
    var editAcronymIdInput = document.getElementById('editAcronymIdInput');
    var updateCourseForm = document.getElementById('updateCourseForm');
    var updateCourseConfirmationContainer = document.getElementById('updateCourseConfirmationContainer');

    updateLinks.forEach(function (link) {
        link.addEventListener('click', function (event) {
            event.preventDefault();

            var courseId = link.getAttribute('data-course-id');
            var courseName = link.parentNode.parentNode.querySelector('.course-name').innerText;
            var courseAcronym = link.parentNode.parentNode.querySelector('.course-acronym').innerText;

            updateCourseForm.action = `/Update_Course_List/${courseId}/`;
            editCourseIdInput.value = courseId;
            editCourseInput.value = courseName;
            editAcronymIdInput.value = courseId;
            editAcronymInput.value = courseAcronym;

            updateCourseConfirmationContainer.style.display = 'flex';
            updateCourseConfirmationContainer.style.position = 'fixed';
            updateCourseConfirmationContainer.style.top = '50%';
            updateCourseConfirmationContainer.style.left = '50%';
            updateCourseConfirmationContainer.style.transform = 'translate(-50%, -50%)';
        });
    });

    document.getElementById('updateNoButton').addEventListener('click', function () {
        updateCourseConfirmationContainer.style.display = 'none';
    });
});



document.querySelectorAll('.delete-button').forEach(function(button) {
    button.addEventListener('click', function () {
        const itemType = this.dataset.itemType;
        const itemId = this.dataset.itemId;
        const itemName = document.querySelector(`.school-text[data-school-id="${itemId}"]`).innerText;

        const modalContainer = document.getElementById('deleteSchoolConfirmationContainer');
        modalContainer.style.display = 'flex';

        const modalText = modalContainer.querySelector('.school-text');
        modalText.innerText = `Are you sure you want to delete ${itemName}?`;

        const deleteForm = document.getElementById('deleteForm');
        deleteForm.action = `/delete_item/${itemType}/${itemId}/`;
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