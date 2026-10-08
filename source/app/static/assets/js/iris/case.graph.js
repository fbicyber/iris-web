
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
var cy;
var graph3d;
var nodePositions = {}; // store node positions
var cyResizeHandler = null;
var resize3DHandler = null;
var is3DMode = false;
var lastGraphData = null;

function redrawAll(data) {
  lastGraphData = data;

  if (data.nodes.length == 0) {
      $('#card_main_load').show();
      $(is3DMode ? '#graph-container-3d' : '#graph-container').text('No events in graph');
      hide_loader();
      return true;
  }

  if (is3DMode) {
    render3DView(data);
    return;
  }

  render2DView(data);
}

function render2DView(data) {
  var container = document.getElementById("graph-container");
  container.innerHTML = '';
  container.style.width = (window.innerWidth - 400) + "px";
  container.style.height = (window.innerHeight - 250) + "px";

  if (typeof cytoscape === 'function') {
    drawWithCytoscape(container, data);
    return;
  }

  drawWithVis(container, data);
}

function render3DView(data) {
  var container = document.getElementById("graph-container-3d");
  container.style.width = (window.innerWidth - 400) + "px";
  container.style.height = (window.innerHeight - 250) + "px";
  drawWith3D(container, data);
}

/*
 * Toggles between the cytoscape 2D view and the three.js/WebGL 3D view.
 * Both views are fed from the same graph data pulled from get_case_graph(),
 * so cytoscape itself is untouched and stays a normal, upgradeable dependency.
 */
function toggle3DView() {
  is3DMode = !is3DMode;

  var container2d = document.getElementById('graph-container');
  var container3d = document.getElementById('graph-container-3d');
  var btnLabel = document.querySelector('#btn_toggle_3d .menu-title');

  if (is3DMode) {
    container2d.style.display = 'none';
    container3d.style.display = 'block';
    btnLabel.textContent = 'Show in 2D';
  } else {
    container3d.style.display = 'none';
    container2d.style.display = 'block';
    btnLabel.textContent = 'Show in 3D';
  }

  if (lastGraphData) {
    redrawAll(lastGraphData);
  }
}

function rgbToHex(rgbString) {
    const regex = /rgb\s*\((\d{1,3}),\s*(\d{1,3}),\s*(\d{1,3})\)/;
    const result = regex.exec(rgbString);

    if (result) {
        const r = parseInt(result[1], 10);
        const g = parseInt(result[2], 10);
        const b = parseInt(result[3], 10);

        return "#" + (1 << 24 | r << 16 | g << 8 | b).toString(16).slice(1);
    } else {
        throw new Error('Invalid RGB string');
    }
}


function drawWithCytoscape(container, data) {
  nodePositions = JSON.parse(localStorage.getItem('nodePositions')) || {};

  var elements = [];
  data.nodes.forEach((node) => {
    elements.push({
      data: {
        id: String(node.id),
        label: node.label || '',
        title: node.title || '',
        image: node.image || '',
        type: node.type || '',
        fontColor: node.font && String(node.font).indexOf('white') !== -1 ? 'white' : '#1f2d3d'
      }
    });
  });

  data.edges.forEach((edge, index) => {
    console.log(edge.color);
    elements.push({
      data: {
        id: 'e_' + index + '_' + String(edge.from) + '_' + String(edge.to),
        source: String(edge.from),
        target: String(edge.to),
        title: edge.title || '',
        dashed: edge.dashes ? 1 : 0,
        color: edge.color ? edge.color : '#2b7ce9',
        type: edge.type || '',
        eid: edge.eid || '',
        display: (edge.type == 'link') ? 'element' : 'none',
        expanded: false,
      }
    });
  });

  if (cy) {
    cy.destroy();
  }

  var docStyle = window.getComputedStyle(document.body);
  var card = document.querySelector(".card");
  var cardStyle = window.getComputedStyle(card);

  var cardBackground = rgbToHex(cardStyle.getPropertyValue('background-color'));
  var docBackground = rgbToHex(docStyle.getPropertyValue('background'));
  var docColor = rgbToHex(docStyle.getPropertyValue('color'));

  cy = cytoscape({
    container: container,
    elements: elements,
    style: [
      {
        selector: 'node',
        style: {
          'label': 'data(label)',
          'color': docColor,
          'font-size': 12,
          'text-wrap': 'wrap',
          'text-max-width': 120,
          'text-valign': 'bottom',
          'text-margin-y': 14,
          'background-color': 'transparent',
          'background-opacity': 0,
          'background-image': 'data(image)',
          'background-fit': 'cover',
          'background-clip': 'none',
          'width': 36,
          'height': 36,
          'border-width': 0,
          'z-index': 0.5,
          'z-index-compare': 'manual',
        }
      },
      {
        selector: 'edge',
        style: {
          'curve-style': 'bezier',
          'control-point-step-size': 4,
          'control-point-weight': 0.5,
          'target-distance-from-node': '2px',
          'source-distance-from-node': '2px',
          'edge-distances': 'intersection',
          'line-color': 'data(color)',
          'target-arrow-color': 'data(color)',
          'target-arrow-shape': 'triangle',
          'width': 2,
          'line-style': 'solid',
          'opacity': 0.35,
          'font-size': 10,
          'color': docColor,
          'text-opacity': 1,
          'text-background-color': docBackground,
          'text-background-opacity': 1,
          'text-background-shape': 'round-rectangle',
          'text-background-padding': '5px',
          'text-border-color': 'data(color)',
          'text-border-opacity': 1,
          'text-border-width': 2,
          'z-index': 0.3,
          'z-index-compare': 'manual',
          'display': 'data(display)',
        }
      },
      {
        selector: 'edge[dashed = 1]',
        style: {
          'line-style': 'dashed'
        }
      },
      {
        selector: 'edge.cy-highlight',
        style: {
          'control-point-step-size': 24,
          'control-point-weight': 0.8,
          'transition-duration': '0.5s',
          'curve-style': 'bezier',
          'line-color': 'data(color)',
          'target-arrow-color': 'data(color)',
          'width': 3,
          'opacity': 0.7,
          'z-index': 0.3,
        }
      },
      {
        selector: 'node.cy-highlight-1',
        style: {
          'opacity': 1,
          'background-color': '#2b7ce9',
          'background-opacity': 0.5,
          'background-fill': 'radial-gradient',
          'background-gradient-stop-positions': '0% 50%',
          'background-gradient-stop-colors': '#2b7ce9 ' + cardBackground,
        }
      },
      {
        selector: 'node.cy-highlight',
        style: {
          'opacity': 1,
          'font-weight': 'bold',
          'background-color': '#2b7ce9',
          'background-opacity': 0.8,
          'background-fill': 'radial-gradient',
          'background-gradient-stop-colors': '#2b7ce9 ' + cardBackground,
          'background-gradient-stop-positions': '15% 50%',
          'z-index': 0.4,
        }
      },
      {
        selector: '.cy-dim',
        style: {
          'opacity': 0.15
        }
      }
    ],
    wheelSensitivity: 0.2
  });

  var cxMenuOptions = {
    evtType: 'cxttap',
    menuItems: [
      {
        id: 'edit-ioc',
        content: "Edit IOC...",
        selector: 'node[type = "ioc"]',
        onClickFunction: function(evt) {
          var target = evt.target || evt.cyTarget;
          console.log('ioc ' + target.data('id').slice(1));
          edit_ioc(target.data('id').slice(1));
        },
      },
      {
        id: 'edit-asset',
        content: "Edit asset...",
        selector: 'node[type = "asset"]',
        onClickFunction: function(evt) {
          var target = evt.target || evt.cyTarget;
          console.log('asset' + target.data('id').slice(1));
          asset_details(target.data('id').slice(1));
        },
      },
      {
        id: 'edit-event',
        content: "Edit event...",
        selector: 'edge[type = "event"]',
        onClickFunction: function(evt) {
          var target = evt.target || evt.cyTarget;
          edit_event(target.data('eid'));
        },
      },
      {
        id: 'events',
        content: 'Events >',
        selector: 'edge[type = "link"]',
        submenu: []
      },
      {
        id: 'expand-events',
        content: 'Expand edges',
        selector: 'edge[type = "link"][!expanded]',
        tooltipText: 'Show all events between these two nodes as edges.',
        onClickFunction: function(evt) {
          var target = evt.target || evt.cyTarget;
          target.parallelEdges('edge[type = "event"]').forEach(function(edge) {
            edge.data('display', 'element');
          });
          target.data('expanded', true);
        }
      },
      {
        id: 'collapse-events',
        content: 'Collapse edges',
        selector: 'edge[type = "event"], edge[?expanded]',
        tooltipText: 'Show only one edge between these two nodes.',
        onClickFunction: function(evt) {
          var target = evt.target || evt.cyTarget;
          target.parallelEdges('edge[type = "event"]').forEach(function(edge) {
            edge.data('display', 'none');
          });
          target.parallelEdges('edge[type = "link"]').forEach(function(edge) {
            edge.data('display', 'element');
            edge.data('expanded', false);
          });
        }
      },
    ],
    menuItemClasses: ['dropdown-item'],
    contextMenuClasses: ['dropdown-menu', 'shadow'],
    submenuIndicator: {},
  };

  var cxMenu = cy.contextMenus(cxMenuOptions);

  var nodesWithSavedPos = [];
  cy.nodes().forEach(function(node) {
    var savedPos = nodePositions[node.id()];
    if (savedPos) {
      node.position(savedPos);
      node.lock();
      nodesWithSavedPos.push(node);
    }
  });

  cy.elements('edge[type = "event"]').forEach(function(edge) {
    linkEdge = edge.parallelEdges('edge[type = "link"]');
    if (linkEdge.length == 0) {
      cy.add({
        group: 'edges',
        data: {
          id: 'e_' + 'link' + '_' + String(edge.source().id()) + '_' + String(edge.target().id()),
          title: `Link between ${edge.source().data('label')} and ${edge.target().data('label')}`,
          color: '#2b7ce9',
          type: 'link',
          source: edge.source().id(),
          target: edge.target().id(),
        },
      })
    }
  })

  cy.layout({
    name: 'cose',
    animate: false,
    fit: true,
    padding: 100,
    randomize: false
  }).run();

  nodesWithSavedPos.forEach(function(node) {
    node.unlock();
  });
  cy.fit(cy.elements(), 100);

  cy.on('dragfree', 'node', function(evt) {
    var node = evt.target;
    nodePositions[node.id()] = node.position();
    localStorage.setItem('nodePositions', JSON.stringify(nodePositions));
  });

  cy.on('mouseover', 'node, edge', function(evt) {
    var title = evt.target.data('title');
    if (title) {
      if (evt.target.isEdge()) {
        evt.target.style('label', title);
        evt.target.style('line-color', rgbToHex(docStyle.getPropertyValue('color')));
        evt.target.style('opacity', 1);
        evt.target.style('text-margin-y', evt.position.y - evt.target.midpoint().y - 10);
        evt.target.style('text-margin-x', evt.position.x - evt.target.midpoint().x);
        evt.target.style('target-arrow-color', rgbToHex(docStyle.getPropertyValue('color'))),
        evt.target.style('z-index', 1);
      }
    }
  });

    cy.on('mousemove', 'edge', function(evt) {
      evt.target.style('text-margin-y', evt.position.y - evt.target.midpoint().y - 10);
      evt.target.style('text-margin-x', evt.position.x - evt.target.midpoint().x);
    });

    function sortByEventTitle(a, b) {
        return ('' + a.data('title')).localeCompare(b.data('title'));
    }

    cy.on('cxttap', 'edge[type = "link"]', function(evt) {
      cxMenu.removeMenuItem('events')
      cxMenu.insertBeforeMenuItem({
        id: 'events',
        content: 'Events >',
        selector: 'edge[type = "link"]',
        submenu: []
      }, 'expand-events');
      var link = evt.target;
      link.parallelEdges('edge[type = "event"]').sort(sortByEventTitle).forEach(function(edge) {
        console.log(edge.data('title'));
        cxMenu.appendMenuItem(
          {
            id: edge.data('eid'),
            content: edge.data('title'),
            onClickFunction: function() { edit_event(edge.data('eid')) }
          },
          'events'
        );
      })
    });


  cy.on('mouseout', 'node, edge', function(evt) {
    container.title = '';
    evt.target.removeStyle();
  });

  function clearCyHighlight() {
    cy.elements().removeClass('cy-highlight cy-highlight-1 cy-dim');
  }

  cy.on('tap', 'node', function(evt) {
    var selectedNode = evt.target;
    clearCyHighlight();

    cy.elements().addClass('cy-dim');
    selectedNode.removeClass('cy-dim').addClass('cy-highlight');

    var connectedEdges = selectedNode.connectedEdges();
    connectedEdges.removeClass('cy-dim').addClass('cy-highlight');
    connectedEdges.connectedNodes().removeClass('cy-dim').addClass('cy-highlight-1');
  });

  cy.on('tap', function(evt) {
    if (evt.target === cy) {
      clearCyHighlight();
    }
  });

  if (cyResizeHandler) {
    window.removeEventListener('resize', cyResizeHandler);
  }

  cyResizeHandler = function() {
    container.style.width = (window.innerWidth - 400) + "px";
    container.style.height = (window.innerHeight - 250) + "px";
    if (cy) {
      cy.resize();
      cy.fit(cy.elements(), 100);
    }
  };

  window.addEventListener('resize', cyResizeHandler);
}

/* Fallback only - real nodes carry their own icon image (same ones cytoscape uses),
 * which is what actually distinguishes a compromised (red icon) asset from the rest. */
var NODE_FALLBACK_3D_COLOR = '#6c757d';
var SELECTION_3D_COLOR = '#2b7ce9';
var currentGraphData3D = null;
var context3DMenuEl = null;
var node3DTextureLoader = null;
var node3DTextureCache = {};

function loadNode3DIconTexture(url, onLoad) {
  if (node3DTextureCache[url]) {
    onLoad(node3DTextureCache[url]);
    return;
  }
  if (!node3DTextureLoader) {
    node3DTextureLoader = new THREE.TextureLoader();
  }
  node3DTextureLoader.load(url, function(texture) {
    node3DTextureCache[url] = texture;
    onLoad(texture);
  });
}

/* Node ids are always prefixed ('a' = asset, 'b' = ioc, per case_graphs_routes.py) -
 * fall back to that prefix since standalone (event-less) nodes don't get a 'type' field. */
function get3DNodeType(node) {
  if (node.type) {
    return node.type;
  }
  var prefix = String(node.id).charAt(0);
  if (prefix === 'a') {
    return 'asset';
  }
  if (prefix === 'b') {
    return 'ioc';
  }
  return '';
}

/* Collapses parallel "event" edges between the same two nodes into a single
 * link, mirroring the default (collapsed) state of the cytoscape view. */
function buildGraphDataFor3D(data) {
  var nodes = data.nodes.map(function(node) {
    return {
      id: String(node.id),
      label: node.label || '',
      type: get3DNodeType(node),
      image: node.image || '',
      __state: 'none',
    };
  });

  var linkByKey = {};
  data.edges.forEach(function(edge) {
    var source = String(edge.from);
    var target = String(edge.to);
    var key = [source, target].sort().join('__');

    if (!linkByKey[key]) {
      linkByKey[key] = {
        source: source,
        target: target,
        color: edge.color || '#2b7ce9',
        titles: [],
      };
    }
    if (edge.title) {
      linkByKey[key].titles.push(edge.title);
    }
  });

  var links = Object.keys(linkByKey).map(function(key) {
    var link = linkByKey[key];
    return {
      source: link.source,
      target: link.target,
      color: link.color,
      title: link.titles.join(', '),
      __state: 'none',
    };
  });

  return { nodes: nodes, links: links };
}

/* Node spheres have radius ~7.3 (cbrt(nodeVal=6) * default nodeRelSize=4), so the
 * ring is drawn well outside that so it isn't depth-occluded by the sphere. */
function create3DHaloSprite(color, opacity) {
  var canvas = document.createElement('canvas');
  canvas.width = 128;
  canvas.height = 128;
  var ctx = canvas.getContext('2d');
  ctx.beginPath();
  ctx.arc(64, 64, 54, 0, Math.PI * 2);
  ctx.lineWidth = 12;
  ctx.strokeStyle = color;
  ctx.stroke();

  var sprite = new THREE.Sprite(new THREE.SpriteMaterial({
    map: new THREE.CanvasTexture(canvas),
    transparent: true,
    depthWrite: false,
    depthTest: false,
    opacity: opacity,
  }));
  sprite.scale.set(26, 26, 1);
  return sprite;
}

function hide3DContextMenu() {
  if (context3DMenuEl) {
    context3DMenuEl.remove();
    context3DMenuEl = null;
  }
}

/* Mirrors the cytoscape context menu: right click a node to get a single
 * "Edit asset/IOC..." action, instead of editing directly on left click. */
function show3DContextMenu(node, event) {
  event.preventDefault();
  hide3DContextMenu();

  var menuLabel = null;
  var menuAction = null;
  if (node.type === 'asset') {
    menuLabel = 'Edit asset...';
    menuAction = function() { asset_details(node.id.slice(1)); };
  } else if (node.type === 'ioc') {
    menuLabel = 'Edit IOC...';
    menuAction = function() { edit_ioc(node.id.slice(1)); };
  }
  if (!menuLabel) {
    return;
  }

  var menu = document.createElement('div');
  menu.className = 'dropdown-menu shadow show';
  menu.style.position = 'fixed';
  menu.style.left = event.clientX + 'px';
  menu.style.top = event.clientY + 'px';
  menu.style.zIndex = 10000;

  var item = document.createElement('a');
  item.className = 'dropdown-item';
  item.href = '#';
  item.textContent = menuLabel;
  item.onclick = function(e) {
    e.preventDefault();
    hide3DContextMenu();
    menuAction();
  };
  menu.appendChild(item);

  document.body.appendChild(menu);
  context3DMenuEl = menu;

  setTimeout(function() {
    document.addEventListener('click', hide3DContextMenu, { once: true });
  }, 0);
}

/* Selects a node like cytoscape's tap handler: highlights the node and its
 * connected edges/neighbors, but only bolds the label of the clicked node. */
function selectNode3D(node) {
  hide3DContextMenu();
  if (!currentGraphData3D) {
    return;
  }

  var neighborIds = {};
  currentGraphData3D.links.forEach(function(link) {
    var sourceId = (link.source && typeof link.source === 'object') ? link.source.id : link.source;
    var targetId = (link.target && typeof link.target === 'object') ? link.target.id : link.target;
    if (sourceId === node.id || targetId === node.id) {
      link.__state = 'highlighted';
      neighborIds[sourceId === node.id ? targetId : sourceId] = true;
    } else {
      link.__state = 'none';
    }
  });

  currentGraphData3D.nodes.forEach(function(n) {
    if (n.id === node.id) {
      n.__state = 'selected';
    } else if (neighborIds[n.id]) {
      n.__state = 'neighbor';
    } else {
      n.__state = 'none';
    }
  });

  graph3d.refresh();
}

function clear3DSelection() {
  if (!currentGraphData3D) {
    return;
  }
  currentGraphData3D.nodes.forEach(function(n) { n.__state = 'none'; });
  currentGraphData3D.links.forEach(function(l) { l.__state = 'none'; });
  graph3d.refresh();
}

function drawWith3D(container, data) {
  var docStyle = window.getComputedStyle(document.body);
  var docBackground = rgbToHex(docStyle.getPropertyValue('background'));
  var docColor = rgbToHex(docStyle.getPropertyValue('color'));
  var graphData = buildGraphDataFor3D(data);
  currentGraphData3D = graphData;

  if (!graph3d) {
    graph3d = ForceGraph3D()(container)
      .nodeId('id')
      .nodeVal(6)
      .nodeThreeObject(function(node) {
        var group = new THREE.Group();
        if (node.__state === 'selected' || node.__state === 'neighbor') {
          group.add(create3DHaloSprite(SELECTION_3D_COLOR, node.__state === 'selected' ? 1 : 0.5));
        }

        var iconMaterial = new THREE.SpriteMaterial({
          transparent: true,
          depthWrite: false,
          color: NODE_FALLBACK_3D_COLOR,
        });
        var iconSprite = new THREE.Sprite(iconMaterial);
        iconSprite.scale.set(14, 14, 1);
        group.add(iconSprite);

        if (node.image) {
          loadNode3DIconTexture(node.image, function(texture) {
            iconMaterial.map = texture;
            iconMaterial.color.set('#ffffff');
            iconMaterial.needsUpdate = true;
          });
        }

        var label = new SpriteText(node.label);
        label.color = docColor;
        label.textHeight = 3.5;
        label.fontWeight = node.__state === 'selected' ? 'bold' : 'normal';
        label.position.set(0, -15, 0);
        group.add(label);
        return group;
      })
      .nodeThreeObjectExtend(false)
      .linkColor(function(link) { return link.__state === 'highlighted' ? SELECTION_3D_COLOR : link.color; })
      .linkWidth(function(link) { return link.__state === 'highlighted' ? 2 : 0.5; })
      .linkLabel('title')
      .linkOpacity(0.4)
      .linkDirectionalArrowLength(3.5)
      .linkDirectionalArrowRelPos(1)
      .onNodeClick(selectNode3D)
      .onNodeRightClick(show3DContextMenu)
      .onBackgroundClick(function() {
        hide3DContextMenu();
        clear3DSelection();
      });
  }

  graph3d
    .backgroundColor(docBackground)
    .width(container.clientWidth)
    .height(container.clientHeight)
    .graphData(graphData);

  if (resize3DHandler) {
    window.removeEventListener('resize', resize3DHandler);
  }

  resize3DHandler = function() {
    container.style.width = (window.innerWidth - 400) + "px";
    container.style.height = (window.innerHeight - 250) + "px";
    graph3d.width(container.clientWidth).height(container.clientHeight);
  };

  window.addEventListener('resize', resize3DHandler);
}

function drawWithVis(container, data) {
  if (cyResizeHandler) {
    window.removeEventListener('resize', cyResizeHandler);
    cyResizeHandler = null;
  }

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
        enabled: false
    }
  };

  nodePositions = JSON.parse(localStorage.getItem('nodePositions')) || {};

  data.nodes.forEach(node => {
    if (nodePositions[node.id]) {
        node.x = nodePositions[node.id].x;
        node.y = nodePositions[node.id].y;
    }
  });

  network = new vis.Network(container, data, options);

  network.once('afterDrawing', function () {
    network.fit({ animation: false, padding: 100 });
  });

  network.on("stabilizationIterationsDone", function () {
      network.setOptions({ physics: false });
  });

  network.on("dragEnd", function (params) {
      if (params.nodes.length > 0) {
          params.nodes.forEach(nodeId => {
              var position = network.getPositions([nodeId])[nodeId];
              nodePositions[nodeId] = position;
          });
          localStorage.setItem('nodePositions', JSON.stringify(nodePositions));
      }
  });
}

/* Page is ready, fetch the assets of the case */
$(document).ready(function(){
    $('.modal').on('hidden.bs.modal', function () {
        get_case_graph();
    })
    get_case_graph();
});

