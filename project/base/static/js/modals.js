
document.getElementById('openSchoolForm').addEventListener('click', function () {
    document.getElementById('schoolFormContainer').style.display = 'flex';
    initializeInputBox();
});


/*function ng applicant_list*/

document.addEventListener("DOMContentLoaded", function() {
    var dateOfBirthSelect = document.getElementById("id_date_of_birth");
    dateOfBirthSelect.addEventListener("change", function() {
        dateOfBirthSelect.classList.remove("placeholder");
    });
});