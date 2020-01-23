

var nameToUri;
var currentDlists;

function updatePlaylists(){
    // get a better user delineation method
    // user = window.prompt("what is your username")
    user = "Danny";
    // testing
    if (!user.includes("Danny")){
        user = "Danny";
    }
    
    var rule = "onclick=\"this.style.color = this.style.color == \'red\' ? \'black\' : \'red\'\" style=\"cursor: pointer\"";
    var url= "http://127.0.0.1:5000/list_playlists";
    url = url + "?user=" + user;
    var xmlhttp = new XMLHttpRequest();

    xmlhttp.onreadystatechange = function() {
    
        if (this.readyState == 4 && this.status == 200) {
            plists = JSON.parse(xmlhttp.responseText);
            document.getElementById('theList').innerHTML = "";
            for (let i = 0; i < plists.length; i++) {
                document.getElementById('theList').innerHTML += ('<li ' + rule +  '>' + plists[i]["name"] + '</li>');
            }
            nameToUri = listToMap(plists);
        }
    };

    xmlhttp.open("GET", url, true);
    xmlhttp.send();
}   

function getDrainlists(){
    user = "Danny";
    var url= "http://127.0.0.1:5000/list_drains";
    url = url + "?user=" + user;
    var rule = "onclick=\"showStructure(this.innerHTML)\" style=\"cursor: pointer\"";
    // todo update to actually send the request, you fool!
    var xmlhttp = new XMLHttpRequest();

    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            plists = JSON.parse(xmlhttp.responseText);
            currentDlists = plists;
            document.getElementById('drainList').innerHTML = "";
            for (let i = 0; i < plists.length; i++) {
                document.getElementById('drainList').innerHTML += ('<li ' + rule +  '>' + plists[i]["Name"] + '</li>');
            }

        }
    };

    xmlhttp.open("GET", url, true);
    xmlhttp.send();


    var url= "http://127.0.0.1:5000/list_playlists";
    url = url + "?user=" + user;
    var req2 = new XMLHttpRequest();

    req2.onreadystatechange = function() {
    
        if (this.readyState == 4 && this.status == 200) {
            plists = JSON.parse(req2.responseText);
            nameToUri = listToMap(plists);
        }
    };

    req2.open("GET", url, true);
    req2.send();
}

function listToMap(lst){
    m = new Map();
    for (var i = 0; i < lst.length; i++) {
        m[lst[i]["name"]] = lst[i]["uri"];
    }
    return m
}

function showStructure(item){
    for (var i = 0; i < currentDlists.length; i++) {
        if (item === currentDlists[i].Name){
            displayStructure(currentDlists[i]);
        }
    }  
}

function displayStructure(item){
    card = document.getElementById("structure")
    card.innerHTML = "<p></p>"

    p = card.children[0]
    p.innerHTML = "<div id=\"sinkName\"> Name: "+ item.Name + "</div>"
    card.innerHTML += "Sources:"
    card.innerHTML += "<ul id=\"strucList\" class= \"w3-ul\"></ul>"
    ul = document.getElementById("strucList")
    
    for (var i = 0; i < item.Sources.length; i++) {
        ul.innerHTML += "<li> <div> " + item.Sources[i].Name + "<i class=\"fa fa-close\" style=\"margin-left: 5px\" onclick=\"deleteSource(this)\"></i>  </div> </li>"
    }
    card.innerHTML += "<br><i class=\"fa fa-plus\" style = \"font-size : xx-large;\" onclick=\"addSource(this)\"</i>"
       
}
function addSource(item){
    var name = prompt("enter Playlist Name: ")
    uri = nameToUri[name]
    sinkUri = nameToUri[document.getElementById("sinkName").innerHTML.split("Name: ")[1].trim()]

    var url= "http://127.0.0.1:5000/add_source";
    url = url + "?user=" + user;
    url = url + "&listURI=" + uri;
    url = url + "&sinkURI=" + sinkUri;
    var req2 = new XMLHttpRequest();

    req2.onreadystatechange = function() {
    
        if (this.readyState == 4 && this.status == 200) {
            confirm("source: " + name + "has been added")

        }
    };
    
    req2.open("GET", url, true);
    req2.send();

    // todo here do add source logic

}
function deleteSource(item){
    name = item.parentElement.innerHTML.split("<")[0].trim();
    uri = nameToUri[name]
    sinkUri = nameToUri[document.getElementById("sinkName").innerHTML.split("Name: ")[1].trim()]
    
    var url= "http://127.0.0.1:5000/remove_source";
    url = url + "?user=" + user;
    url = url + "&listURI=" + uri;
    url = url + "&sinkURI=" + sinkUri;
    var req2 = new XMLHttpRequest();

    req2.onreadystatechange = function() {
    
        if (this.readyState == 4 && this.status == 200) {
            confirm("source: " + name + "has been removed")

        }
    };
    req2.open("GET", url, true);
    req2.send();
    // using the name / URI delete the source, 
    

}

function search(searchString){
// todo this is garbage, but makes it look decent
    window.scrollTo(0,146);
    searchString = searchString.toUpperCase();
    var ul = document.getElementById("theList");
    var li = ul.getElementsByTagName("li");

    for (var i = 0; i < li.length; i++) {
        if (li[i].textContent.toUpperCase().includes(searchString)){
            li[i].style.display = "";
        }
        else {
        li[i].style.display = "none";
        }
    }
}

function collectHighlighted(){
    var arr = [];
    var ul = document.getElementById("theList");
    var li = ul.getElementsByTagName("li");

    for (var i = 0; i < li.length; i++) {
        if (li[i].style.color === "red"){
            arr.push(nameToUri[li[i].textContent]);
        }
    }

    var name = document.getElementById("sourcedName").value;
    console.log(arr);
    console.log(name);
    
    for (var i = 0; i < li.length; i++) {
        li[i].style.color = "black";
    }
    
    document.getElementById("sourcedName").value = "";
    createNewDrain(name, arr);
    }
    
function createNewDrain(name, sources){
    
    user = "Danny";
    var url= "http://127.0.0.1:5000/new_drain";
    var xmlhttp = new XMLHttpRequest();

    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            confirm("created new Drain with name " + name + " and Sources: " + sources);
        }
    };

    xmlhttp.open("POST", url, true);
    xmlhttp.setRequestHeader('Content-Type', 'application/json');
    xmlhttp.send(JSON.stringify({"user": user, "drainlist":name, "sources":sources}));
    // xmlhttp.send();
}

function refresh(){
  
    user = "Danny";
    var url= "http://127.0.0.1:5000/refresh";
    url = url + "?user=" + user;
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("GET", url, true);
    xmlhttp.send();

}
