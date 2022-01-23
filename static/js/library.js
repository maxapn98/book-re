let editMode = false;

window.addEventListener("DOMContentLoaded", function() {
    let editToggler = document.getElementById("editToggler");
    let viewButtons = document.getElementsByClassName("card-button");
    let editButtons = document.getElementsByClassName("card-edit-button");

    editToggler.addEventListener("click", function(){
        editMode = !editMode;

        if (editMode === true) {
            for (let i = 0; i < viewButtons.length; i++){
                viewButtons[i].classList.add("d-none");
            }

            for(let i = 0; i < editButtons.length; i++){
                editButtons[i].classList.remove("d-none");
            }
        } else {
            for(let i = 0; i < editButtons.length; i++){
                editButtons[i].classList.add("d-none");
            }

            for (let i = 0; i < viewButtons.length; i++){
                viewButtons[i].classList.remove("d-none");
            }
        }
    });
});