// Read a file from the disk and parse it as JSON

// Wrap everything inside an anonymous function where variable $ is an alias
// for global variable jQuery. This is done to create a local scope for
// functions and variables so that they will not intervene with other libraries.
(function ($) {

  "use strict";
  // Assumption: the following global variables are set:
  // JSAV, jQuery

  // Exercise recording file parsed as an object
  // See JSAV_inspector_file_format.txt.
  var exercise = null;

  // JSAV slideshow of an exercise recording
  var jsav = null;

  // Supported exercise types
  const supportedTypes = ['buildheap', 'dijkstra', 'quicksort'];

  // Type of current exercise
  var exerciseType = null;

  // Index of current submission, begins from 0.
  var currentSubmission = 0;

  var submissionsById = [];

  // Bind event handlers
  $(document).ready(function(){
    $("#jsavRecordingFileOk").click(readJsavRecordings);
    $("#previousSubmission").click(handleSubmissionSelect);
    $("#nextSubmission").click(handleSubmissionSelect);
    $("#submissionNumber").change(handleSubmissionSelect);
    $("#submissionId").change(handleSubmissionSelect);
    $(document).keydown(handleKeyPress);
  });

  // Validates an exercise file and writes feedback into the #fileInfo box.
  //
  // Parameters:
  //   exerciseData: an exercise object
  //
  // Returns:
  //   (boolean): whether the file has submissions that can be inspected

  function isValidJsavInspectorFile(exerciseData) {
    const r = exerciseData;

    // Validate file version
    if (r.application !== "JSAV Inspector" || r.version !== 1) {
        $("#fileInfo").html("This is not a JSAV Inspector version 1 file.");
        $("#fileInfo").addClass("error");
        return false;
    }

    // Validate exercise type
    const t = r.metadata.type;
    var recognised = false;
    for (var x of supportedTypes) {
      if (r.metadata.type === x) {
        recognised = true;
        exerciseType = x;
        break;
      }
    }
    if (recognised == false) {
      $("#fileInfo").html("Unknown exercise type: ' '");
      $("#fileInfo").addClass("error");
      return false;
    }

    // Success
    var successText = /* "File loaded successfully.\n" + */
      "Course   : " + r.metadata.course_code + " " + r.metadata.course_name +
      "\n" +
      "Year     : " + r.metadata.year + "\n" +
      "Exercise : " + r.metadata.longname + " (id: " + r.metadata.id + ")\n";
    $("#fileInfo").html(successText);
    $("#fileInfo").removeClass("error");

    return true;
  }

  // Initialises submission selector
  function initSubmissionSelector(exerciseData) {
    const s = exerciseData.submissions;
    $("#previousSubmission").attr("disabled", true);
    if (s.length < 2) {
      $("#nextSubmission").attr("disabled", true);
    }
    else {
      $("#nextSubmission").attr("disabled", false);
    }
    if (s.length < 1) {
      $("#submissionNumber").attr("value", "0");
    }
    else {
      $("#submissionNumber").attr("value", "1");
    }
    $("#submissionNumber").attr("disabled", false);
    $("#submissionId").attr("disabled", false);
    $("#submissionCount").html(s.length);
    $("#submissionInfo").html("");

    currentSubmission = 0;
    openSubmission(currentSubmission);
  }

  // Reads a JSON file written by the A+ JSAV submission downloader,
  // then calls initSubmissionSelector()
  function readJsavRecordings() {
    const file = document.getElementById("jsavRecordingFile").files[0];
    if (file) {
      var reader = new FileReader();
      reader.onload = function(event_) {
        exercise = JSON.parse(event_.target.result);
        if (isValidJsavInspectorFile(exercise)) {
          initSubmissionSelector(exercise);
          createSubmissionIdIndex();
        }
      }
      reader.onerror = function(event_) {
        $("#fileInfo").html("An error occurred reading the file: " + event_);
        $("#fileInfo").addClass("error");
      }
      reader.readAsText(file, "UTF-8");
    }
  }

  // Creates an index (dictionary, hash table) from submission id to relative
  // number of submission in the file. This enables fast search by submission
  // id.
  function createSubmissionIdIndex() {
    let byId = {};
    for (let i = 0; i < exercise.submissions.length; i++) {
      let s = exercise.submissions[i];
      byId[s.id] = i;
    }
    exercise.submissions.byId = byId;
  }

  // Click handler for previous / next / go to submission
  // Parameters:
  //   ev: browser event
  function handleSubmissionSelect(ev) {
    const id = ev.target.id
    if (id === "previousSubmission" && currentSubmission > 0) {
      currentSubmission--;
      $("#submissionNumber").attr("value", currentSubmission + 1);
      $("#previousSubmission").attr("disabled", (currentSubmission === 0));
      $("#nextSubmission").attr("disabled", false);
      openSubmission(currentSubmission);
    }
    else if (id === "nextSubmission" &&
       currentSubmission < exercise.submissions.length - 1) {
       currentSubmission++;
       $("#submissionNumber").attr("value", currentSubmission + 1);
       $("#previousSubmission").attr("disabled", false);
       $("#nextSubmission").attr("disabled",
         (currentSubmission === exercise.submissions.length - 1));
       openSubmission(currentSubmission);
    }
    else if (id === "submissionNumber") {
      const parsed = parseInt(ev.target.value, 10);
      const isNan = isNaN(parsed);
      const isInt = /^\d+$/.test(ev.target.value);
      var inRange = false;
      if (!isNan) {
        inRange = (parsed > 0 && parsed <= exercise.submissions.length);
        if (inRange) {
          currentSubmission = parsed - 1;
          $("#previousSubmission").attr("disabled", (currentSubmission === 0));
          $("#nextSubmission").attr("disabled",
            (currentSubmission === exercise.submissions.length - 1));
        }
      }
      if (isNan || !isInt || !inRange) {
        // Reset input
        $("#submissionNumber").attr("value", currentSubmission + 1);
      }
      if (!isNan && inRange) {
        openSubmission(currentSubmission);
      }
    }
    else if (id === "submissionId") {
      const parsed = parseInt(ev.target.value, 10);
      const exerciseIndex = exercise.submissions.byId[parsed];
      if (exerciseIndex === undefined) {
        // Reset input
        $("#submissionId").attr("value",
          exercise.submissions[currentSubmission].id)
      }
      else {
        currentSubmission = exerciseIndex;
        $("#submissionNumber").attr("value", currentSubmission + 1);
        $("#previousSubmission").attr("disabled", (currentSubmission === 0));
        $("#nextSubmission").attr("disabled",
          (currentSubmission === exercise.submissions.length - 1));
        openSubmission(exerciseIndex);
      }
    }
  }

  // Keyboard press handler
  // Parameters:
  //   ev: browser event
  function handleKeyPress(ev) {
    // näppis, nuoli oikealle: $('.jsavforward').click();
    // näppis, nuoli vasemmalle: $('.jsavbackward').click();
    // näppis, home: $('.jsavbegin').click();
    // näppis, end: $('.jsavend').click();
    // näppis, page up: $('#previousSubmission').click(handleSubmissionSelect);
    // näppis, page down: $('#nextSubmission').click(handleSubmissionSelect);

    // key: ArrowUp, ArrowDown, ArrowLeft, ArrowRight, PageUp, Page
    const k = event.which;

    if (k === 37) { // Left
      $('.jsavbackward').click();
    }
    else if (k === 39) { // Right
      $('.jsavforward').click();
    }
    else if (k === 38) { // Up
      ev.preventDefault();
      $('#previousSubmission').click();
    }
    else if (k === 40) { // Down
      ev.preventDefault();
      $('#nextSubmission').click();
    }
    else if (k === 36) { // Home
      $('.jsavbegin').click();
    }
    else if (k === 35) { // End
      $('.jsavend').click();
    }
  }

  // Updates #submissionInfo and the JSAV visualisation
  //
  // Parameters:
  //   index: index of the submission [0 ... exercise.submissions.length - 1]
  function openSubmission(index) {
    const s = exercise.submissions[index];
    const score = parseInt(s.points / s.max_points * 100);
    $("#submissionId").attr("value", s.id)
    $("#submissionInfo").html(" score: " + s.points + "/" + s.max_points +
      " (" + score + "%)");

    if (exerciseType === 'buildheap') {
      createBuildHeapAV(s.recording)
    }
    currentSubmission = index;
  }

  function parseBuildHeapRecording(recording) {
    const steps = recording.length;
    const arraySize = recording[0].ind.length;

    for (var step of recording) {
      var s = '[';
      for (var i = 0; i < arraySize; i++) {
        s += ' ' + step.ind[i].v;
      }
      s += ']'
      console.log(s)
    }
  }

  function createBuildHeapAV(recording) {
    // Parse the input of the exercise from the first step
    const arraySize = recording[0].ind.length;
    var inputArray = [];
    for (var i = 0; i < arraySize; i++) {
      inputArray[i] = recording[0].ind[i].v;
    }

    // Clear JSAV controls and canvas. Otherwise the controls
    // will appear multiple times.
    $('.jsavcontrols').html('');
    $('#avcanvas').html('');

    // Begin creating a new visualisation. It will be shown inside
    // <div id="container">.
    jsav = new JSAV("container");

    // Create a visualisation of an array with integer indices
    var arr = jsav.ds.array(inputArray, {indexed: true});

    // Create a visualisation of a binary tree. The following graphic shows
    // a complete binary tree with 10 nodes having indices 0...9.
    //               _____root____
    //              /             \
    //           [1]              [2]
    //         /    \            /   \
    //        /      \          /     \
    //     [3]        [4]     [5]      [6]
    //    /   \      /   \
    //  [7]   [8]  [9]
    var bt = jsav.ds.binarytree();

    var btRef = []; // stores references to each node of the binary tree
    bt.root(inputArray[0]); // set the value of the root
    btRef[0] = bt.root();

    // Add nodes to the binary tree visualisation: create iteratively children
    // for nodes corresponding array indices 0 ... (arraySize / 2). The rest of
    // the nodes are leaf nodes according to the theory of binary heap.
    for (var i = 0; i < Math.floor(arraySize / 2); i++) {
      var left_i = i * 2 + 1;
      var right_i = left_i + 1;
      if (left_i < arraySize) {
        btRef[left_i] = btRef[i].left(inputArray[left_i]);
      }
      if (right_i < arraySize) {
        btRef[right_i] = btRef[i].right(inputArray[right_i]);
      }
    }

    bt.layout();        // Compute graphical layout of the binary tree.
    jsav.displayInit(); // Set this step as the first step of the visualisation.

    // Create visualisation steps for swaps.
    const steps = recording.length;
    var prev_swap_i = [];  // indices of previous swap

    for (var i = 1; i < steps; i++) {
      // Detect a swap
      var swap_i = [];       // indices of current swap
      var swapCount = 0;
      for (var j = 0; j < arraySize; j++) {
        if (recording[i].ind[j].v !== recording[i-1].ind[j].v) {
          swap_i[swapCount++] = j;
        }
      }
      if (swapCount === 2) {
        // Add pair of steps for each swap.
        // First highlight elements that will be swapped.
        jsav.step();

        arr.addClass(swap_i, 'playerhighlight');
        btRef[swap_i[0]].addClass('playerhighlight');
        btRef[swap_i[1]].addClass('playerhighlight');

        // Then move elements and remove highlight.
        jsav.step();
        var pair = [btRef[swap_i[0]].value(), btRef[swap_i[1]].value()];
        btRef[swap_i[0]].value(pair[1]);
        btRef[swap_i[1]].value(pair[0]);
        arr.value(swap_i[0], pair[1]);
        arr.value(swap_i[1], pair[0]);

        arr.removeClass(swap_i, 'playerhighlight');
        btRef[swap_i[0]].removeClass('playerhighlight');
        btRef[swap_i[1]].removeClass('playerhighlight');

        prev_swap_i[0] = swap_i[0];
        prev_swap_i[1] = swap_i[1];
      }
    }

    jsav.recorded(); // done recording changes, will rewind

    // Set maximum speed for animations to enable fast viewing
    $(document).trigger("jsav-speed-change", 1);
  }

}(jQuery)); // End of local wrapper
