document.getElementById('openSchoolForm').addEventListener('click', function () {
    document.getElementById('schoolFormContainer').style.display = 'flex';
    initializeInputBox();
});

document.getElementById('closeSchoolForm').addEventListener('click', function () {
    document.getElementById('schoolFormContainer').style.display = 'none';
});

document.getElementById('openCourseForm').addEventListener('click', function () {
    let courseFormContainer = document.getElementById('courseFormContainer');
    courseFormContainer.classList.remove('hidden');
    courseFormContainer.classList.add('flex');
    initializeInputBox();
});

document.getElementById('closeCourseForm').addEventListener('click', function () {
    document.getElementById('courseFormContainer').classList.add('hidden');
    document.getElementById('courseFormContainer').classList.remove('flex');
});

document.getElementById('schoolFormContainer').addEventListener('click', function (e) {
    if (e.target.id === 'schoolFormContainer' || e.target.id === 'closeSchoolForm') {
        document.getElementById('schoolFormContainer').style.display = 'none';
    }
});

document.getElementById('courseFormContainer').addEventListener('click', function (e) {
    if (e.target.id === 'courseFormContainer' || e.target.id === 'closeCourseForm') {
        document.getElementById('courseFormContainer').classList.add('hidden');
        document.getElementById('courseFormContainer').classList.remove('flex');
    }
});


var input = document.querySelector(".input-box");
var countContainer = document.createElement("span");
countContainer.classList.add("tag");
input.appendChild(countContainer);

var totalCountContainer = document.createElement("span");
totalCountContainer.classList.add("total-count");
input.appendChild(totalCountContainer);

var totalOptions = parseInt(input.dataset.totalOptions) || 0;
var displayLimit = 2;

document.querySelector(".input-box").addEventListener("click", function() {
    var list = document.getElementById("toggleList");
    if (list.style.display === "none" || list.style.display === "") {
        list.style.display = "block";
    } else {
        list.style.display = "none";
    }
});

function initializeInputBox() {
    var input = document.querySelector(".input-box");
    input.innerHTML = "Select a school ";
    countContainer.textContent = "";
    totalCountContainer.textContent = `Total: 0/${totalOptions}`;
}

input.addEventListener("click", function () {
    this.classList.toggle("open");
    let list = this.nextElementSibling;
    list.classList.toggle("open");
    if (list.classList.contains("open")) {
        list.style.maxHeight = "150px"; 
        list.style.boxShadow =
            "0 1px 2px 0 rgba(0, 0, 0, 0.15),0 1px 3px 1px rgba(0, 0, 0, 0.1)";
    } else {
        list.style.maxHeight = null;
        list.style.boxShadow = null;
    }
});


var checkboxes = document.querySelectorAll(".checkbox");
checkboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", () => {
        updateSelectedOptions();
    });
});

function updateSelectedOptions() {
    var selectedOptions = [];
    checkboxes.forEach((checkbox) => {
        if (checkbox.checked) {
            let optionId = checkbox.id.substring(2);
            let optionName = checkbox.nextElementSibling.querySelector(".name").innerHTML;
            selectedOptions.push({ id: optionId, name: optionName });
        }
    });

    var selectedContainer = document.querySelector(".input-box");
    selectedContainer.innerHTML = "";

    if (selectedOptions.length === 0) {
        selectedContainer.innerHTML = "Select a school";
    } else {
        for (let i = 0; i < Math.min(selectedOptions.length, displayLimit); i++) {
            addSelectedTag(selectedOptions[i].id, selectedOptions[i].name);
            if (i < Math.min(selectedOptions.length, displayLimit) - 1) {
                selectedContainer.innerHTML += ", ";
            }
        }

        if (selectedOptions.length > displayLimit) {
            countContainer.textContent = `+${selectedOptions.length - displayLimit}`;
            selectedContainer.appendChild(countContainer);
        } else {
            countContainer.textContent = "";
        }
    }

    totalCountContainer.textContent = `Total: ${selectedOptions.length}/${totalOptions}`;
}

function addSelectedTag(optionId, optionName) {
    var selectedContainer = document.querySelector(".input-box");
    var selectedTag = document.createElement("div");
    selectedTag.classList.add("tag");
    selectedTag.innerHTML = `${optionName}`;
    selectedContainer.appendChild(selectedTag);
}

function updateCheckbox(optionId) {
    checkboxes.forEach((checkbox) => {
        if (checkbox.id === "id" + optionId) {
            checkbox.checked = false;
        }
    });
}

function addSelectedSchools() {
var selectedSchools = document.querySelectorAll('input[name="schools"]:checked');
var schoolIds = [];

selectedSchools.forEach(function(school) {
    schoolIds.push(school.value);
});


var schoolIdsInput = document.getElementById('id_school_ids');
schoolIdsInput.value = JSON.stringify(schoolIds);
}