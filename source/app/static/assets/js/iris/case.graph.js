
function get_case_graph() {
  get_request_api('graph/getdata')
  .done((data) => {
      if (data.status == 'success') {
          redrawAll(data.data);
          hide_loader();
      } else {
          $('#submit_new_asset').text('Save again');
          swal("Oh no !", data.message, "error");
      }
  });
}

var network;
var nodePositions = {}; // store node positions

function redrawAll(data) {
  if (data.nodes.length == 0) {
      $('#card_main_load').show();
      $('#graph-container').text('No events in graph');
      hide_loader();
      return true;
  }
  var container = document.getElementById("graph-container");
  var options = {
    edges: {
      smooth: {
        enabled: true,
        type: 'continuous',
        roundness: 0.5
      }
    },
    layout: {
      randomSeed: 2, 
      improvedLayout: true
    },
    interaction: {
      hideEdgesOnDrag: false
    },
    width: (window.innerWidth - 400) + "px",
    height: (window.innerHeight - 250) + "px",
    physics: {
        enabled: false // disable physics to preserve manual positions
    }
  };

  // restore node positions from localStorage
  nodePositions = JSON.parse(localStorage.getItem('nodePositions')) || {}; 
  
  data.nodes.forEach(node => {
    if (nodePositions[node.id]) {
        node.x = nodePositions[node.id].x; 
        node.y = nodePositions[node.id].y; 
    }
  });

  nodes = data.nodes;
  edges = data.edges;

  network = new vis.Network(container, data, options);

  network.once('afterDrawing', function () {
    network.fit({ animation: false, padding: 100 });
  });

  network.on("stabilizationIterationsDone", function () {
      network.setOptions({ physics: false });
  });

  // save node positions when nodes are dragged/moved
  network.on("dragEnd", function (params) {
      if (params.nodes.length > 0) {
          params.nodes.forEach(nodeId => {
              var position = network.getPositions([nodeId])[nodeId];
              nodePositions[nodeId] = position; 
          });

          // save positions to localStorage
          localStorage.setItem('nodePositions', JSON.stringify(nodePositions)); 
      }
  });
}


/* Page is ready, fetch the assets of the case */
$(document).ready(function(){
    get_case_graph();
});

