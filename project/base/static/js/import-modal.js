document.addEventListener('DOMContentLoaded', function () {
    var modalContainer = document.getElementById('ImportFormContainer');
    var importButton = document.getElementById('importButton');
    var closeButton = document.getElementById('closeButton');
    var form = document.querySelector('#ImportFormContainer form');

    importButton.addEventListener('click', function () {
        modalContainer.style.display = 'block';
    });

    closeButton.addEventListener('click', function () {
        modalContainer.style.display = 'none';
    });

    form.addEventListener('submit', function (event) {
        event.preventDefault();

        // Get the file input element
        var fileInput = document.getElementById('id_file');

        // Check if a file is selected
        if (fileInput.files.length > 0) {
            var file = fileInput.files[0];

            // Now you can do something with the file data
            console.log('File Name:', file.name);
            console.log('File Size:', file.size);
            console.log('File Type:', file.type);

            // You may want to send the file to the server using fetch or XMLHttpRequest
            // Example using fetch:
            /*
            fetch('/your/upload/endpoint', {
                method: 'POST',
                body: file
            })
            .then(response => response.json())
            .then(data => {
                console.log('File uploaded successfully:', data);
            })
            .catch(error => {
                console.error('Error uploading file:', error);
            });
            */
        } else {
            console.log('No file selected.');
        }

        // Close the modal or perform additional actions if needed
        modalContainer.style.display = 'none';
    });

    window.addEventListener('click', function (event) {
        if (event.target === modalContainer) {
            modalContainer.style.display = 'none';
        }
    });
});
