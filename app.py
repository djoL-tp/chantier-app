<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CHANTIER V17.1 CLEAN</title>

<style>
body{
font-family: Arial;
margin:0;
background:#0f172a;
color:white;
}

header{
background:#111827;
padding:15px;
text-align:center;
font-size:20px;
font-weight:bold;
}

.container{
padding:15px;
}

.card{
background:#1f2937;
padding:15px;
border-radius:12px;
margin-bottom:15px;
}

input, textarea, button{
width:100%;
padding:10px;
margin-top:8px;
border-radius:8px;
border:none;
font-size:14px;
}

button{
background:#2563eb;
color:white;
font-weight:bold;
cursor:pointer;
}

button.red{
background:#dc2626;
}

.row{
display:flex;
gap:10px;
}

.row button{
flex:1;
}

.item{
background:#111827;
padding:10px;
border-radius:10px;
margin-top:10px;
}
</style>
</head>

<body>

<header>🚧 CHANTIER V17.1 CLEAN</header>

<div class="container">

<!-- ENGINS -->
<div class="card">
<h3>🚜 Engins</h3>
<input id="enginInput" placeholder="Nom engin + heures">
<button onclick="addEngin()">Ajouter</button>
<div id="enginList"></div>
</div>

<!-- NOTES -->
<div class="card">
<h3>📝 Notes chantier</h3>
<textarea id="note" placeholder="Infos chantier..."></textarea>
<button onclick="saveNote()">Sauvegarder</button>
</div>

<!-- PHOTOS -->
<div class="card">
<h3>📸 Photos chantier</h3>
<input type="file" id="photoInput" accept="image/*" multiple>
<button onclick="savePhotos()">Enregistrer photos</button>
<div id="photoList"></div>
</div>

<!-- SIGNATURE -->
<div class="card">
<h3>✍️ Signature ouvrier</h3>

<canvas id="canvas" width="300" height="120"
style="background:white;border-radius:8px;"></canvas>

<div class="row">
<button onclick="clearCanvas()">Effacer</button>
<button onclick="saveSig()">Sauver</button>
</div>

<img id="sigImg" style="margin-top:10px;max-width:100%;">
</div>

<!-- GESTION HISTORIQUE -->
<div class="card">
<h3>🧹 Gestion historique</h3>

<button class="red" onclick="clearAll()">Tout supprimer</button>

<div class="row">
<button onclick="clearEngins()">Engins</button>
<button onclick="clearNote()">Note</button>
</div>

<div class="row">
<button onclick="clearPhotos()">Photos</button>
<button onclick="clearSignature()">Signature</button>
</div>

</div>

</div>

<script>

let engins = JSON.parse(localStorage.getItem("engins") || "[]");


// ================= ENGINS =================
function renderEngins(){
document.getElementById("enginList").innerHTML =
engins.map((e,i)=>`
<div class="item">
${e}
<button class="red" onclick="deleteEngin(${i})">Supprimer</button>
</div>
`).join("");
}

function addEngin(){
let val = document.getElementById("enginInput").value;
if(!val) return;

engins.push(val);
localStorage.setItem("engins", JSON.stringify(engins));
document.getElementById("enginInput").value="";
renderEngins();
}

function deleteEngin(i){
engins.splice(i,1);
localStorage.setItem("engins", JSON.stringify(engins));
renderEngins();
}

renderEngins();


// ================= NOTES =================
document.getElementById("note").value =
localStorage.getItem("note") || "";

function saveNote(){
localStorage.setItem("note",
document.getElementById("note").value);
alert("Note sauvegardée");
}


// ================= PHOTOS =================
function savePhotos(){
let input = document.getElementById("photoInput");
let stored = JSON.parse(localStorage.getItem("photos") || "[]");

for(let f of input.files){
let reader = new FileReader();

reader.onload = function(e){
stored.push(e.target.result);
localStorage.setItem("photos", JSON.stringify(stored));
renderPhotos();
};

reader.readAsDataURL(f);
}
}

function renderPhotos(){
let photos = JSON.parse(localStorage.getItem("photos") || "[]");

document.getElementById("photoList").innerHTML =
photos.map(p=>`
<img src="${p}"
style="width:100%;margin-top:10px;border-radius:10px;">
`).join("");
}

renderPhotos();


// ================= SIGNATURE =================
let canvas = document.getElementById("canvas");
let ctx = canvas.getContext("2d");
let drawing = false;

canvas.addEventListener("mousedown", ()=>drawing=true);
canvas.addEventListener("mouseup", ()=>drawing=false);
canvas.addEventListener("mousemove", draw);

canvas.addEventListener("touchstart", ()=>drawing=true);
canvas.addEventListener("touchend", ()=>drawing=false);
canvas.addEventListener("touchmove", drawTouch);

function draw(e){
if(!drawing) return;
ctx.fillStyle="black";
ctx.beginPath();
ctx.arc(e.offsetX, e.offsetY, 2, 0, Math.PI*2);
ctx.fill();
}

function drawTouch(e){
let t = e.touches[0];
let rect = canvas.getBoundingClientRect();

ctx.fillStyle="black";
ctx.beginPath();
ctx.arc(
t.clientX - rect.left,
t.clientY - rect.top,
2,0,Math.PI*2
);
ctx.fill();
}

function clearCanvas(){
ctx.clearRect(0,0,canvas.width,canvas.height);
}

function saveSig(){
let data = canvas.toDataURL();
localStorage.setItem("signature", data);
document.getElementById("sigImg").src = data;
}

if(localStorage.getItem("signature")){
document.getElementById("sigImg").src =
localStorage.getItem("signature");
}


// ================= SUPPRESSION =================
function clearAll(){
if(!confirm("Supprimer TOUT le chantier ?")) return;

clearEngins();
clearNote();
clearPhotos();
clearSignature();

alert("Tout l'historique a été supprimé");
}

function clearEngins(){
localStorage.removeItem("engins");
engins = [];
renderEngins();
}

function clearNote(){
localStorage.removeItem("note");
document.getElementById("note").value = "";
}

function clearPhotos(){
localStorage.removeItem("photos");
document.getElementById("photoList").innerHTML = "";
}

function clearSignature(){
localStorage.removeItem("signature");
ctx.clearRect(0,0,canvas.width,canvas.height);
document.getElementById("sigImg").src = "";
}

</script>

</body>
</html>