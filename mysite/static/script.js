fetch('https://technopustakblog.pythonanywhere.com/api/comment/1')
    .then(res => res.json())
    .then((api) => {
        window.myapi = api;
        window.myobjl = Object.keys(api).length;
}).catch(err => console.error(err));
var myDiv = document.getElementById("commments");
    myDiv.scrollTop = myDiv.scrollHeight;
i = window.myobjl;
function myFunction() {
    while(true){
        if(myDiv.offsetHeight + myDiv.scrollTop >= document.getElementById("commments").scrollHeight){
            console.log('lol')
            var btn = document.createElement("div");
            let list = Array.from(myapi[i]);
            let data = `Posted by ${list[0]}:-<br>${list[3]}<br><br>`;
            btn.innerHTML = data;
            i-=1;
            document.getElementById("comments").appendChild(btn);
        }
    }
}