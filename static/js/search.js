function showAll() {
    document.getElementById("compounds-section").style.display = "grid";
    document.getElementById("reactions-section").style.display = "grid";
}

function showCompounds() {
    document.getElementById("compounds-section").style.display = "grid";
    document.getElementById("reactions-section").style.display = "none";
}

function showReactions() {
    document.getElementById("compounds-section").style.display = "none";
    document.getElementById("reactions-section").style.display = "grid";
}