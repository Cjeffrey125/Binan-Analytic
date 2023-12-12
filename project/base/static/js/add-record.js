function toggleSection(sectionId) {
    var sectionToToggle = document.getElementById(sectionId);
    var otherSections = document.querySelectorAll('.form-section');

    otherSections.forEach(function (section) {
        if (section.id !== sectionId) {
            section.style.display = 'none';
        }
    });

    if (sectionToToggle.style.display === 'none') {
        sectionToToggle.style.display = 'block';
    } else {
        sectionToToggle.style.display = 'block';
    }
}

