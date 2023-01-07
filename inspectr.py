# user can input a job number and get all relevent stats

#!/usr/bin/python3
import cgi

r = cgi.FieldStorage()
html = 'Content-type: text/html\r\n\r\n'

script = '''<script>
        function sPpy(ele){if (event.key === 'Enter'){sRpy()}};
        function sRpy(){ //for processing a single button click
            var xhttp = new XMLHttpRequest();
            xhttp.open("POST", "../cgi-bin/reportr.py", true);
            xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            var soID = document.getElementById("idField");
            xhttp.send("soID=" + soID.value);
            xhttp.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    actYN(this.responseText)
                }
            }
        }
        function actYN(r){
            var div = document.getElementById("receive");
            while(div.firstChild){div.removeChild(div.firstChild);}
            div.insertAdjacentHTML("beforeend", r);
        }</script>'''

style = '''<style>@font-face{
          font-family: Futura;
          src: url("../futuramc.TTF");
        }
        body{
          background-color: #032B3E;
        }
        h1, p{
          color: red;
        }
        h2, h3{
          font-family: Futura;
          display: inline;
        }
        div{
          font-family: Futura;
          padding-bottom: 3vw;
          color: #E2CAB5;
          background-color: #032B3E;
          font-size: 5vw;
        }
        button{
          color: #E2CAB5;
          font-family:Futura;
          font-size: 4vw;
          margin: 2vw;
          background-color: #032B3E;
          border-color: #E2CEB5;
        }
        button:hover{
          background-color: #C0A893;
        }
        input[type=number]{
          width: 20%;
          height: 4vw;
        }
        </style>'''

body = '''<div id="ask"><input id="idField" type="number" onkeydown="sPpy(this)"><button id="report" onclick="sRpy()">
Report</button></div><div id="receive"></div>'''

html += script + style + body

print(html)
