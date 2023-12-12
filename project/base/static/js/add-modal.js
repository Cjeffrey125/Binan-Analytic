
document.getElementById('addButton').addEventListener('click', function () {
    document.getElementById('schoolFormContainer').style.display = 'flex';
    initializeInputBox();
});


document.addEventListener("DOMContentLoaded", function() {
    var dateOfBirthSelect = document.getElementById("id_date_of_birth");
    dateOfBirthSelect.addEventListener("change", function() {
        dateOfBirthSelect.classList.remove("placeholder");
    }); 
});