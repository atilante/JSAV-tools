"use strict";

// Creates an example binary tree visualisation

function createBinaryTreeAV() {
  let jsav = new JSAV("container");
  // let arr = jsav.ds.array([10, 13, 99, 25]);

  var bt = jsav.ds.binarytree();
  jsav.step();
  bt.root("ki"); // set the value of the root
  bt.layout(); // ..update layout
  jsav.step(); // add new step

  bt.root().css({"background-color": "yellow"}); //highlight root
  bt.root().left("3"); // set left child
  bt.layout(); //..layout
  jsav.step();

  var right = bt.root().right("4"); // set right, store reference
  bt.layout();
  jsav.step();

  right.left("4L"); // set left child of 4
  bt.layout();
  jsav.step();

  bt.root().left().left("3L").parent().right("3R"); // chaining, set left and right of 3
  bt.layout();
  jsav.step();
  var node = bt.newNode("4R");
  node.css( { "color": "red",
              "top": right.css("top"), "left": parseInt(right.css("left"), 10) + 60});
  jsav.step();

  right.right(node);
  bt.layout();

  jsav.recorded(); // done recording changes, will rewind

}

function createBinaryHeapAV() {
  let jsav = new JSAV("container");
  // let arr = jsav.ds.array([10, 13, 99, 25]);

  const initialArray = [98, 16, 97, 66, 81, 54, 71, 55, 94, 13];
  var arr = jsav.ds.array(initialArray, {indexed: true});

  /*             _____root____
                /             \
             [1]              [2]
           /    \            /   \
          /      \          /     \
       [3]        [4]     [5]      [6]
      /   \      /   \
    [7]   [8]  [9]                       */


  var bt = jsav.ds.binarytree();
  var btRef = [];
  bt.root(initialArray[0]); // set the value of the root
  btRef[0] = bt.root();

  var i = 0;
  const arrayLen = initialArray.length;
  for (i = 0; i < Math.floor(arrayLen / 2); i++) {
    console.log(i);
    var left_i = i * 2 + 1;
    var right_i = left_i + 1;
    if (left_i < arrayLen) {
      btRef[left_i] = btRef[i].left(initialArray[left_i]);
    }
    if (right_i < arrayLen) {
      btRef[right_i] = btRef[i].right(initialArray[right_i]);
    }

  }
  bt.layout();
  jsav.step(); // add new step


  arr.css([4, 9], {"background-color": "yellow"});
  btRef[4].css({"background-color": "yellow"});
  btRef[9].css({"background-color": "yellow"});

  jsav.step(); // add new step

  var x = [btRef[9].value(), btRef[4].value()];
  btRef[4].value(x[0]);
  btRef[9].value(x[1]);
  arr.swap(4, 9);
  jsav.step();

  btRef[4].css({"background-color": "white"});
  btRef[9].css({"background-color": "white"});
  arr.css([4, 9], {"background-color": "white"});
  jsav.step();

  // bt.root().css({"background-color": "yellow"}); //highlight root
  // bt.root().left("3"); // set left child
  // bt.layout(); //..layout
  // jsav.step();
  //
  // var right = bt.root().right("4"); // set right, store reference
  // bt.layout();
  // jsav.step();
  //
  // right.left("4L"); // set left child of 4
  // bt.layout();
  // jsav.step();
  //
  // bt.root().left().left("3L").parent().right("3R"); // chaining, set left and right of 3
  // bt.layout();
  // jsav.step();
  // var node = bt.newNode("4R");
  // node.css( { "color": "red",
  //             "top": right.css("top"), "left": parseInt(right.css("left"), 10) + 60});
  // jsav.step();
  //
  // right.right(node);
  // bt.layout();

  jsav.recorded(); // done recording changes, will rewind

}

function createGraphAV() {
  var jsav = new JSAV("container"),
    g, a, b, c, d, e;
  var initGraph = function() {
    g = jsav.ds.graph({width: 500, height: 200, layout: "manual", directed: true});
     a = g.addNode("A", {"left": 0, "top": 80})
        b = g.addNode("B", {"left": 120})
        c = g.addNode("C", {"left": 120, "top": 160})
        d = g.addNode("D", {"left": 260})
        e = g.addNode("E", {"left": 260, "top": 160});
    g.addEdge(a, b, {weight: 20});
    g.addEdge(a, c, {weight: 10});
    g.addEdge(a, d, {weight: 2});
    g.addEdge(b, d, {weight: 7});
    g.addEdge(c, b, {weight: 11});
    g.addEdge(c, e, {weight: 35});
    g.addEdge(d, e, {weight: 14});
   };
  initGraph();
  g.layout();
  jsav.displayInit();
  a.css({top: "+=20px"});
  g.layout();
  jsav.recorded();
  g.mouseenter(function() { this.highlight({record: false}); })
   .mouseleave(function() { this.unhighlight({record: false}); });
}

$(document).ready(createBinaryHeapAV);
// $(document).ready(createBinaryTreeAV);
// $(document).ready(createGraphAV);
