function makeDraggableAndResizable(el) {
    let isResizing = false;

    el.addEventListener("mousedown", mousedown);

    function mousedown(e) {
        if (!isResizing && !e.target.classList.contains("resizer")) {
            window.addEventListener("mousemove", mousemove);
            window.addEventListener("mouseup", mouseup);

            let prevX = e.clientX;
            let prevY = e.clientY;

            function mousemove(e) {
                let newX = prevX - e.clientX;
                let newY = prevY - e.clientY;

                const rect = el.getBoundingClientRect();

                el.style.left = rect.left - newX + "px";
                el.style.top = rect.top - newY + "px";

                prevX = e.clientX;
                prevY = e.clientY;
            }

            function mouseup() {
                window.removeEventListener("mousemove", mousemove);
                window.removeEventListener("mouseup", mouseup);
            }
        }
    }

    const resizers = el.querySelectorAll(".resizer");
    let currentResizer;

    for (let resizer of resizers) {
        resizer.addEventListener("mousedown", mousedown);

        function mousedown(e) {
            currentResizer = e.target;
            isResizing = true;

            let prevX = e.clientX;
            let prevY = e.clientY;

            window.addEventListener("mousemove", mousemove);
            window.addEventListener("mouseup", mouseup);

            function mousemove(e) {
                const rect = el.getBoundingClientRect();

                if (currentResizer.classList.contains("se")) {
                    el.style.width = rect.width - (prevX - e.clientX) + "px";
                    el.style.height = rect.height - (prevY - e.clientY) + "px";
                } else if (currentResizer.classList.contains("sw")) {
                    el.style.width = rect.width + (prevX - e.clientX) + "px";
                    el.style.height = rect.height - (prevY - e.clientY) + "px";
                    el.style.left = rect.left - (prevX - e.clientX) + "px";
                } else if (currentResizer.classList.contains("ne")) {
                    el.style.width = rect.width - (prevX - e.clientX) + "px";
                    el.style.height = rect.height + (prevY - e.clientY) + "px";
                    el.style.top = rect.top - (prevY - e.clientY) + "px";
                } else if (currentResizer.classList.contains("nw")) {
                    el.style.width = rect.width + (prevX - e.clientX) + "px";
                    el.style.height = rect.height + (prevY - e.clientY) + "px";
                    el.style.top = rect.top - (prevY - e.clientY) + "px";
                    el.style.left = rect.left - (prevX - e.clientX) + "px";
                }

                prevX = e.clientX;
                prevY = e.clientY;
            }

            function mouseup() {
                window.removeEventListener("mousemove", mousemove);
                window.removeEventListener("mouseup", mouseup);
                isResizing = false;
            }
        }
    }
}

function addDraggableTextInput() {
   
    let newItem = document.createElement("div");
    newItem.className = "item";

    let resizerNE = document.createElement("div");
    resizerNE.className = "resizer ne";
    let resizerNW = document.createElement("div");
    resizerNW.className = "resizer nw";
    let resizerSE = document.createElement("div");
    resizerSE.className = "resizer se";
    let resizerSW = document.createElement("div");
    resizerSW.className = "resizer sw";

    let inputField = document.createElement("input");
    inputField.type = "text";
    inputField.className = "form-field";
    inputField.placeholder = "Text Field";

  
    newItem.appendChild(resizerNE);
    newItem.appendChild(resizerNW);
    newItem.appendChild(resizerSE);
    newItem.appendChild(resizerSW);
    newItem.appendChild(inputField);


    container.appendChild(newItem);

    makeDraggableAndResizable(newItem);
}

// Get references to the container and the "Add Element" button
let container = document.getElementById("container");
let addButton = document.getElementById("addButton");

// Add an event listener to the "Add Element" button
addButton.addEventListener("click", addDraggableTextInput);
