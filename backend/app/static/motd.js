const button = document.getElementById('load-more');
const archiv_motds = document.getElementsByClassName('motd-section')

window.addEventListener('load', (event) => {
    hide_more_elements();
});  

function hide_more_elements(){
    for (var i = 5; i < 28; i++){
        archiv_motds[i].style.display = 'none';
    }
}


button.onclick = () => {
    for (var i = 27; i > 5; i--){
        archiv_motds[i].style.display = 'block';
    }
    button.style.display = 'none';
};

