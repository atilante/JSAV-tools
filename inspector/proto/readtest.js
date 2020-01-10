// Read a file from the disk and parse it as JSON

"use strict";

function readJsavRecordings() {
  console.log("readJsavRecordings() begins!")
  const file = document.getElementById("jsavRecordingFile").files[0];
  if (file) {
    var reader = new FileReader();
    reader.onload = function(event_) {
      console.log("readJsavRecordings:onload(): event_:" + event_)
      document.getElementById("fileData").innerHTML = event_.target.result;
      var parsed = JSON.parse(event_.target.result);
      console.log(parsed);
    }
    reader.onerror = function(event_) {
      console.error("An error ocurred reading the file" , event_);
    }
    reader.readAsText(file, "UTF-8");
  }
}

$(document).ready(function(){
  console.log("document loaded");
   $("#jsavRecordingFileOk").click(readJsavRecordings);
  //$("#jsavRecordingFileOk").click(function() { console.log("jee!") });
  console.log("listener added loaded");
});



// document.getElementById("jsavRecordingFile").addEventListener("change",
//   readJsavRecordings());
