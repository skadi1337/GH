import Map from './node_modules/ol/Map.js';
import TileLayer from './node_modules/ol/layer/Tile.js';
import View from './node_modules/ol/View.js';
import VectorLayer from './node_modules/ol/layer/Vector.js'
import Vector from './node_modules/ol/source/Vector.js'
import * as olSphere from './node_modules/ol/sphere.js';
import DragBox from './node_modules/ol/interaction/DragBox.js'
import { altKeyOnly } from './node_modules/ol/events/condition.js'
import Polygon from './node_modules/ol/geom/Polygon.js'
import Feature from './node_modules/ol/Feature.js';
import Style from './node_modules/ol/style/Style.js';
import Stroke from './node_modules/ol/style/Stroke.js';
import Fill from './node_modules/ol/style/Fill.js';
import {fromLonLat, get as getProj} from './node_modules/ol/proj.js'
import { getTopRight, getBottomLeft } from './node_modules/ol/extent.js'
import { useGeographic, toLonLat } from './node_modules/ol/proj.js';
import XYZ from './node_modules/ol/source/XYZ.js';


useGeographic();

var sources = {

    "Bing Maps": "http://ecn.t0.tiles.virtualearth.net/tiles/r{quad}.jpeg?g=129&mkt=en&stl=H",
    "Bing Maps Satellite": "http://ecn.t0.tiles.virtualearth.net/tiles/a{quad}.jpeg?g=129&mkt=en&stl=H",
    "Bing Maps Hybrid": "http://ecn.t0.tiles.virtualearth.net/tiles/h{quad}.jpeg?g=129&mkt=en&stl=H",
  
    "div-1": "",
  
    "Google Maps": "https://mt0.google.com/vt/lyrs=m&x={x}&s=&y={y}&z={z}",
    "Google Maps Satellite": "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
    "Google Maps Hybrid": "https://mt0.google.com/vt/lyrs=h&x={x}&s=&y={y}&z={z}",
    "Google Maps Terrain": "https://mt0.google.com/vt/lyrs=p&x={x}&s=&y={y}&z={z}",
  
    "div-2": "",
  
    "Open Street Maps": "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
    "Open Cycle Maps": "http://a.tile.opencyclemap.org/cycle/{z}/{x}/{y}.png",
    "Open PT Transport": "http://openptmap.org/tiles/{z}/{x}/{y}.png",
  
    "div-3": "",
  
    "ESRI World Imagery": "http://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    "Wikimedia Maps": "https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png",
    "NASA GIBS": "https://map1.vis.earthdata.nasa.gov/wmts-webmerc/MODIS_Terra_CorrectedReflectance_TrueColor/default/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg",
  
    "div-4": "",
  
    "Carto Light": "http://cartodb-basemaps-c.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png",
    "Stamen Toner B&W": "http://a.tile.stamen.com/toner/{z}/{x}/{y}.png",
  
};

var models = 
{

    'model_v1_512.pth': 'model_v1_512.pth',
    'fine_tuned_model_v1.pth': 'fine_tuned_model_v1.pth'
}


var eventSource = null;

var ModelProgressPolygon = null;

const mapProviderSelect = document.getElementById('mapProvider');
const mapProviderSelect2 = document.getElementById('mapProvider2');
const mapProviderDownloadSelect = document.getElementById('mapProviderDownload');
const targetZoomInput = document.getElementById('targetZoom');
const downloadButton = document.getElementById("downloadButton");
const cancelDownloadButton = document.getElementById("cancelDownloadButton");
const progressBarFillDownload = document.getElementById('progress-bar-fill-download');
const progressTextDownload = document.getElementById('progress-text-download');
const progressBarFillModel = document.getElementById('progress-bar-fill-model');
const progressTextModel = document.getElementById('progress-text-model');

const settingsSidebar = document.getElementById('SettingsSidebar');
const downloadSidebar = document.getElementById('downloadSidebar');

const showGridButton = document.getElementById('showGridButton');
const hideGridButton = document.getElementById('hideGridButton');

const gridLabel = document.getElementById('GridLabel');
const gridErrorLabel = document.getElementById('GridErrorLabel');

const modelSelect = document.getElementById('modelSelect');

const toggleModelProgress = document.getElementById('toggleModelProgress');

const lonLatInput = document.getElementById('LonLatInput');
const lonLatSearch = document.getElementById('LonLatSearch');
const geoInput = document.getElementById('geoInput');
const geoSearch = document.getElementById('geoSearch');

const clearContoursButton = document.getElementById('clearContoursButton');
const contourColorSelect = document.getElementById('contourColorSelect');
const coordinatesLabel = document.getElementById('coordinatesLabel');
const downloadToLocalDeviceButton = document.getElementById('downloadToLocalDeviceButton');

var cancelLocalDownload = false;

var selected_extent = null;


const googleSatelliteSource = new XYZ({
    url: 'https://mt0.google.com/vt?lyrs=m&x={x}&s=&y={y}&z={z}', // http://mt0.google.com/vt/lyrs=y&hl=en&x={x}&y={y}&z={z}&s=Ga
    attributions: [
        '© Google'
    ],
    crossOrigin: 'Anonymous'
});

const googleSatelliteLayer = new TileLayer({
    source: googleSatelliteSource
});


var highlightLayer = new VectorLayer({
    source: new Vector(),
    style: new Style({
        stroke: new Stroke({
            color: 'red',
            width: 2
        }),
        fill: new Fill({
            color: 'rgba(255, 0, 0, 0)'
        })
    })
});

var GridLayer = new VectorLayer({
    source: new Vector(),
    style: new Style({
        stroke: new Stroke({
            color: 'black',
            width: 1
        }),
        fill: new Fill({
            color: 'rgba(0, 0, 0, 0)'
        })
    }),
    visible: false
});

var ContourLayer = new VectorLayer({
    source: new Vector(),
    style: new Style({
        stroke: new Stroke({
            color: contourColorSelect.value,
            width: 1
        }),
        fill: new Fill({
            color: 'rgba(0, 0, 0, 0)'
        })
    }),
    visible: false
});

var ModelProgressLayer = new VectorLayer({
    source: new Vector(),
    style: new Style({
        stroke: new Stroke({
            color: 'black',
            width: 1
        }),
        fill: new Fill({
            color: 'rgba(0, 0, 0, 0)'
        })
    }),
    visible: true
});

const view = new View({
    center: [0, 0],
    zoom: 2,
});


const map2 = new Map({
    target: 'aerialMap',
    layers: [googleSatelliteLayer],
    view: view,
});


var selection2 = new DragBox({
    condition: altKeyOnly,
});


map2.addInteraction(selection2);
map2.addLayer(highlightLayer);
map2.addLayer(GridLayer);
map2.addLayer(ContourLayer);
map2.addLayer(ModelProgressLayer);


view.on('change:center', showCoordinates);


selection2.on('boxend', function (event) {
    var geometry = selection2.getGeometry();
    var extent = geometry.getExtent();

    var bottomLeft = toLonLat(getBottomLeft(extent));
    var topRight = toLonLat(getTopRight(extent));


    selected_extent = []
    selected_extent.push(bottomLeft[0]);
    selected_extent.push(bottomLeft[1]);
    selected_extent.push(topRight[0]);
    selected_extent.push(topRight[1]);

    var feature = new Feature({
        geometry: new Polygon([
            [
                [bottomLeft[0], bottomLeft[1]],
                [bottomLeft[0], topRight[1]],
                [topRight[0], topRight[1]],
                [topRight[0], bottomLeft[1]],
                [bottomLeft[0], bottomLeft[1]]
            ]
        ])
    });

    highlightLayer.getSource().clear();
    highlightLayer.getSource().addFeature(feature);

});

showCoordinates();
function showCoordinates()
{
    var center = view.getCenter();
    coordinatesLabel.innerHTML = '- Map center coodinates: ' + center[1].toFixed(7) + ', ' + center[0].toFixed(7);
}

setUpModelSelect();
function setUpModelSelect()
{
    for (const model in models) 
    {
          const option = document.createElement('option');
          if (model.startsWith("div"))
          {
            option.disabled = true;
            option.innerHTML = "---";
          }
          else
          {
            option.value = models[model];
            option.textContent = model;
      
            if (model.startsWith("model_v1_512.pth"))
            {
              option.selected = true;
            }
          }
          
        modelSelect.appendChild(option);
    }
} 

setUpMapProvidersDownloadSelect();
function setUpMapProvidersDownloadSelect()
{
    for (const provider in sources) 
    {
          const option = document.createElement('option');
          if (provider.startsWith("div"))
          {
            option.disabled = true;
            option.innerHTML = "---";
          }
          else
          {
            option.value = sources[provider];
            option.textContent = provider;
      
            if (provider.startsWith("Google Maps Satellite"))
            {
              option.selected = true;
            }
          }
          
        mapProviderDownloadSelect.appendChild(option);
    }
}

setUpMapProvidersSelect();
function setUpMapProvidersSelect()
{
    for (const provider in sources) 
    {
          const option = document.createElement('option');
          if (provider.startsWith("div"))
          {
            option.disabled = true;
            option.innerHTML = "---";
          }
          else
          {
            option.value = sources[provider];
            option.textContent = provider;
      
            if (provider.endsWith("Google Maps"))
            {
              option.selected = true;
            }
          }
          
        mapProviderSelect.appendChild(option);
    }
}
setUpMapProvidersSelect2();
function setUpMapProvidersSelect2()
{
    for (const provider in sources) 
    {
          const option = document.createElement('option');
          if (provider.startsWith("div"))
          {
            option.disabled = true;
            option.innerHTML = "---";
          }
          else
          {
            option.value = sources[provider];
            option.textContent = provider;
      
            if (provider.endsWith("Google Maps"))
            {
              option.selected = true;
            }
          }
          
        mapProviderSelect2.appendChild(option);
    }
}




function changeMapProvider() {
    googleSatelliteLayer.setSource(new XYZ({
        url: mapProviderSelect.value,
        crossOrigin: 'Anonymous'
        }))

    mapProviderSelect2.value = mapProviderSelect.value;
}

function changeMapProvider2() {
    googleSatelliteLayer.setSource(new XYZ({
        url: mapProviderSelect2.value,
        crossOrigin: 'Anonymous'
        }))

    mapProviderSelect.value = mapProviderSelect2.value;
}

mapProviderSelect.addEventListener('change', changeMapProvider);
mapProviderSelect2.addEventListener('change', changeMapProvider2);
  


function long2tile(lon,zoom) {
    return (Math.floor((lon+180)/360*Math.pow(2,zoom)));
}

function lat2tile(lat,zoom)  {
    return (Math.floor((1-Math.log(Math.tan(lat*Math.PI/180) + 1/Math.cos(lat*Math.PI/180))/Math.PI)/2 *Math.pow(2,zoom)));
}

function tile2long(x,z) {
    return (x/Math.pow(2,z)*360-180);
}

function tile2lat(y,z) {
    var n=Math.PI-2*Math.PI*y/Math.pow(2,z);
    return (180/Math.PI*Math.atan(0.5*(Math.exp(n)-Math.exp(-n))));
}


/// --------    GRID PREVIEW -------- ///////

function showGrid()
{
    gridErrorLabel.textContent = "";
    if (!selected_extent)
    {
        return;
    }

    GridLayer.getSource().clear();
    GridLayer.setVisible(true);
   
    var x0 = selected_extent[0];
    var y0 = selected_extent[1];
    var x1 = selected_extent[2];
    var y1 = selected_extent[3];

    // Y - широта, lat
    // X - долгота, long
    // На гугл карте всегда идет y,x
    var z = parseFloat(targetZoomInput.value);

    var xMin = long2tile(x0, z);
    var yMin = lat2tile(y0, z) + 1;

    var xMax = long2tile(x1, z);
    var yMax = lat2tile(y1, z) + 1;

    // console.log(xMin);
    // console.log(yMin);
    // console.log(xMax);
    // console.log(yMax);

    var xDelta = Math.ceil(Math.abs(xMax - xMin) + 1);
    if (xDelta % 2 !== 0) {
        xDelta += 1;
      }
    var yDelta = Math.ceil(Math.abs(yMax - yMin) + 1);
    if (yDelta % 2 !== 0) {
        yDelta += 1;
      }
    var totalTiles = xDelta * yDelta;

    // bot left
    var p1 = []
    p1.push(x0)
    p1.push(y0)

    //top left
    var p2 = []
    p2.push(x0)
    p2.push(y1)

    //bot right
    var p3 = []
    p3.push(x1)
    p3.push(y0)

    var xd = Math.round(olSphere.getDistance(p1, p2) / 1000);
    var yd = Math.round(olSphere.getDistance(p1, p3) / 1000);
    var totalArea = xd * yd;

    //gridLabel.innerHTML = "Total tiles: " + String(totalTiles) + " (" + String(xDelta) + "x" + String(yDelta) + ").<br>Total area (km^2): " + String(totalArea) + " (" + String(yd) + "x" + String(xd)+").";

    const MAX_RENDER_TILES = 65 * 65;

    if (totalTiles > MAX_RENDER_TILES)
    {
        var xCount = 0;
        var yCount = 0;
        for (var yi = yMin; yi >= yMax; yi--)
        {
            for (var xi = xMin; xi <= xMax; xi++)
            {
                if (xCount >= 65)
                {
                    break;
                }
    
                drawGridRect(xi, yi, z);
                xCount += 1;
            }
    
            if (yCount >= 65)
            {
                break;
            }
            yCount += 1;
            xCount = 0;
        }
        gridErrorLabel.innerHTML = "Warning: Too much tiles to render.";
    }
    else
    {
        for (var yi = yMin; yi >= yMax; yi--)
        {
            for (var xi = xMin; xi <= xMax; xi++)
            {
                drawGridRect(xi, yi, z);
            }
        }
    }
    
}

function drawGridRect(x, y, z)
{
    var x0 = tile2long(x, z);
    var y0 = tile2lat(y, z);

    var x1 = tile2long(x + 1, z);
    var y1 = tile2lat(y - 1, z);


    var feature = new Feature({
        geometry: new Polygon([
            [
                [x0, y0],
                [x0, y1],
                [x1, y1],
                [x1, y0],
                [x0, y0]
            ]
        ])
    });

    GridLayer.getSource().addFeature(feature);
}

function drawGridRectContours(x, y, z, points, newstyle)
{

    var x0 = tile2long(x, z);
    var y0 = tile2lat(y + 1, z);

    var x1 = tile2long(x + 1, z);
    var y1 = tile2lat(y, z);


    //console.log('tile: ' , x0, y0, x1, y1)

    if (points[0].length > 0)
    {
        points.forEach(element => {
            var coordinates = element.map(function(point) {
                var px = x0 + (point[0] / 256) * (x1 - x0);
                var py = y1 + (point[1] / 256) * (y0 - y1);
                //console.log(point[0], point[1])
                return [px, py];
            });
    
                coordinates.push(coordinates[0]);
    
                var feature = new Feature({
                    geometry: new Polygon([coordinates]),
                });
                
                feature.setStyle(newstyle);
                ContourLayer.getSource().addFeature(feature);
        });
    }

    ModelProgressLayer.getSource().clear();
    
    if (ModelProgressPolygon == null)
    {
        ModelProgressPolygon = [[x0, y0],[x0, y1],[x1, y1],[x1, y1],[x1, y1],[x1, y0], [x0, y0]];
    }
    else
    {
        if (ModelProgressPolygon[0][1] == y0)
        {
            ModelProgressPolygon[2][0] = x1;
            ModelProgressPolygon[3][0] = x1;
            ModelProgressPolygon[4][0] = x1;
            ModelProgressPolygon[4][0] = x1;
            ModelProgressPolygon[5][0] = x1;
        }
        else if (ModelProgressPolygon[0][0] == x0)
        {
            ModelProgressPolygon[1][1] = y1;
            ModelProgressPolygon[3][0] = x1;
            ModelProgressPolygon[3][1] = ModelProgressPolygon[2][1];
            ModelProgressPolygon[4][1] = ModelProgressPolygon[2][1];
            ModelProgressPolygon[2][0] = x1;
            ModelProgressPolygon[2][1] = y1;
            
        }
        else if (ModelProgressPolygon[2][0] == x0)
        {
            ModelProgressPolygon[2][0] = x1;
            ModelProgressPolygon[3][0] = x1;
        }
        else 
        {
            //console.log('???')
        }
    }

    var feature = new Feature({
        geometry: new Polygon([ModelProgressPolygon])
    });

    ModelProgressLayer.getSource().addFeature(feature);

    
    
    // var feature = new Feature({
    //     geometry: new Polygon([
    //         [
    //             [x0, y0],
    //             [x0, y1],
    //             [x1, y1],
    //             [x1, y0],
    //             [x0, y0]
    //         ]
    //     ])
    // });

    // ContourLayer.getSource().addFeature(feature);
}

/// xxxxxxxx    GRID PREVIEW xxxxxxxx ///////



/// --------    DOWNLOAD -------- ///////


const downloadToLocalDevice = async () => {
    
    if (!selected_extent) {
        return;
    }
    
    settingsSidebar.style.display = 'none';
    downloadSidebar.style.display = '';
    hideGrid();
    cancelLocalDownload = false;
    //ContourLayer.getSource().clear();
    ContourLayer.setVisible(true);
    ModelProgressLayer.getSource().clear();
    
    var pattern = mapProviderDownloadSelect.value;
    
    var x0 = selected_extent[0];
    var y0 = selected_extent[1];
    var x1 = selected_extent[2];
    var y1 = selected_extent[3];
  
    var z = parseFloat(targetZoomInput.value);
    var grid = googleSatelliteLayer.getSource().tileGrid;
  
    var xMin = long2tile(x0, z);
    var yMin = lat2tile(y0, z);
  
    var xMax = long2tile(x1, z);
    var yMax = lat2tile(y1, z);

    var xDelta = Math.ceil(Math.abs(xMax - xMin) + 1);
    if (xDelta % 2 !== 0) {
        xDelta += 1;
      }
    var yDelta = Math.ceil(Math.abs(yMax - yMin) + 1);
    if (yDelta % 2 !== 0) {
        yDelta += 1;
      }
    var totalTiles = xDelta * yDelta;
    
  
    const canvas = document.createElement('canvas');
    canvas.width = 512;
    canvas.height = 512;
    const ctx = canvas.getContext('2d');

    var i = 0;
  
  
    const downloadImage = (url) => {
      return new Promise((resolve, reject) => {
        const img = new Image();
        img.crossOrigin = 'anonymous'; // Enable CORS if necessary
        img.onload = () => resolve(img);
        img.onerror = (error) => reject(error);
        img.src = url;
      });
    };
  
    
      for (let yi = yMin; yi > yMax - 1; yi -= 2) {
        for (let xi = xMin; xi < xMax + 1; xi += 2) {

            if (cancelLocalDownload)
            {
                return;
            }

          // Top-left tile of the 2x2 square
          const url = pattern.replace('{x}', xi.toString()).replace('{y}', yi.toString()).replace('{z}', z.toString());
          const img = await downloadImage(url);
          
  
          // Tile above the top-left tile
          const url2 = pattern.replace('{x}', xi.toString()).replace('{y}', (yi - 1).toString()).replace('{z}', z.toString());
          const img2 = await downloadImage(url2);
          
  
          // Diagonal tile of the top-left tile
          const url3 = pattern.replace('{x}', (xi + 1).toString()).replace('{y}', (yi - 1).toString()).replace('{z}', z.toString());
          const img3 = await downloadImage(url3);
          
  
          // Tile to the right of the top-left tile
          const url4 = pattern.replace('{x}', (xi + 1).toString()).replace('{y}', yi.toString()).replace('{z}', z.toString());
          const img4 = await downloadImage(url4);

          ctx.drawImage(img2, 0, 0, 256, 256);
          ctx.drawImage(img, 0, 256, 256, 256);
          ctx.drawImage(img4, 256, 256, 256, 256);
          ctx.drawImage(img3, 256, 0, 256, 256);


          // Download the composed image
            const composedImage = canvas.toDataURL('image/png');
            const link = document.createElement('a');
            link.href = composedImage;
            link.download = String(xi) + ',' + String(yi) + ',' + String(z) + '.png';
            link.click();


            i += 4;
            updateProgressBarDownload(i, totalTiles);
        }
    }

    CancelDownload();
};

async function SetupDownload() {
    if (!selected_extent) {
      return;
    }
  
    settingsSidebar.style.display = 'none';
    downloadSidebar.style.display = '';
    hideGrid();
    //ContourLayer.getSource().clear();
    ContourLayer.setVisible(true);
    ModelProgressLayer.getSource().clear();
   
    

  
    var x0 = selected_extent[0];
    var y0 = selected_extent[1];
    var x1 = selected_extent[2];
    var y1 = selected_extent[3];
  
    var z = parseFloat(targetZoomInput.value);
    var grid = googleSatelliteLayer.getSource().tileGrid;
  
    var xMin = long2tile(x0, z);
    var yMin = lat2tile(y0, z);
  
    var xMax = long2tile(x1, z);
    var yMax = lat2tile(y1, z);

    var xDelta = Math.ceil(Math.abs(xMax - xMin) + 1);
    if (xDelta % 2 !== 0) {
        xDelta += 1;
      }
    var yDelta = Math.ceil(Math.abs(yMax - yMin) + 1);
    if (yDelta % 2 !== 0) {
        yDelta += 1;
      }
    var totalTiles = xDelta * yDelta;

    updateProgressBarDownload(0, totalTiles);
    updateProgressBarModel(0, totalTiles);


    var newStyle = new Style({
        stroke: new Stroke({
            color: contourColorSelect.value,
            width: 2
        }),
        fill: new Fill({
            color: 'rgba(0, 0, 0, 0)'
        })
    });


    var pattern = encodeURIComponent(mapProviderDownloadSelect.value);
    var model = encodeURIComponent(modelSelect.value);
    eventSource = new EventSource(`/stream?xMin=${xMin}&yMin=${yMin}&xMax=${xMax}&yMax=${yMax}&z=${z}&pattern=${pattern}&model=${model}`);
    var i = 0;
    var j = 0;

    eventSource.addEventListener('message', event => {
        //console.log('recieved:', event.data);

        //const pattern = /i:(\d+)/g;
        //const matches = event.data.matchAll(pattern);
        //const numbers = Array.from(matches, (match) => parseInt(match[1]));
        //const sum = numbers.reduce((acc, curr) => acc + curr, 0);
        if (event.data[0] == 'i')
        {
            i += parseInt(event.data.slice(2));
            updateProgressBarDownload(i, totalTiles);
        }
        if (event.data[0] == 'x')
        {
            //console.log('j:' + parseInt(event.data.slice(2)));
            const regex_x = /x:(\d+)/;
            const regex_y = /y:(\d+)/;

            const match_x = event.data.match(regex_x);
            const match_y = event.data.match(regex_y);

            const x = parseInt(match_x[1]);
            const y = parseInt(match_y[1]);
            //console.log('x:', match_x[1])
            //console.log('y:', match_y[1])

            let startIndex = event.data.indexOf("points:") + "points:".length;
            let contoursString = event.data.substring(startIndex, event.data.length - 1);

            let contoursArray = contoursString.split(";");
             
            let res = []
            contoursArray.forEach(contour => {
                let pointsString = contour.split(',');
                let points = []
                for (let i = 0; i < pointsString.length - 1; i += 2) {
                    let x = parseInt(pointsString[i]);
                    let y = parseInt(pointsString[i + 1]);
                    points.push([ x, y ]);
                  }
                res.push(points)
            });

            //console.log(res)


            drawGridRectContours(x, y, z, res, newStyle);
            //console.log("draw: ", x, y, z);

            j += 1;
            updateProgressBarModel(j, totalTiles);
        }
        else
        {
            //console.log(event.data)
        }
        

        //const pattern2 = /j:(\d+)/g;
        //const matches2 = event.data.matchAll(pattern2);
        //const numbers2 = Array.from(matches2, (match) => parseInt(match[1]));
        //const sum2 = numbers2.reduce((acc, curr) => acc + curr, 0);

        

        // if (data[0] == 'i')
        // {   
        //     console.log(data.slice(2));
        //     i += parseInt(data.slice(2));
        //     updateProgressBar(i, totalTiles);
        // }
        // else
        // {
        //     console.log('data j');
        // }
        
       
      });
    
      eventSource.addEventListener('error', error => {
        //console.error('Error:', error);
        eventSource.close();
        CancelDownload();
      });
  
    //console.log('done');
  }

  function updateProgressBarDownload(i, totalTiles) {
    var progress = i / totalTiles * 100;
    progressBarFillDownload.style.width = `${progress}%`;
    progressTextDownload.textContent = `Downloaded: ${i}/${totalTiles}`;
  }

  function updateProgressBarModel(j, totalTiles) {
    var progress = j / totalTiles * 100;
    progressBarFillModel.style.width = `${progress}%`;
    progressTextModel.textContent = `Processed: ${j}/${totalTiles}`;
    
  }

function CancelDownload()
{
    if (eventSource)
    {
        eventSource.close();
    }

    settingsSidebar.style.display  = '';
    downloadSidebar.style.display = 'none';

    ModelProgressPolygon = null;
    ModelProgressLayer.getSource().clear();
    highlightLayer.getSource().clear();

    cancelLocalDownload = true;
}

/// xxxxxxxx    DOWNLOAD xxxxxxxx ///////

function hideGrid()
{
    GridLayer.getSource().clear();
    gridLabel.innerHTML = "";
    gridErrorLabel.innerHTML = "";
}

function toggleModelProcessLayer()
{
    
    if (ModelProgressLayer.isVisible())
    {
        ModelProgressLayer.setVisible(false);
        toggleModelProgress.checked = false;
    }
    else
    {
        ModelProgressLayer.setVisible(true);
        toggleModelProgress.checked = true;
    }
}

function lonLatSearchFunction()
{
    var text = lonLatInput.value;
    var parts = text.split(",");

    var lat = parseFloat(parts[0])
    var lon = parseFloat(parts[1])

    var view = map2.getView();
    view.setCenter([lon, lat])
}

function geoSearchFunction()
{
 

  const baseUrl = 'https://nominatim.openstreetmap.org/search';
  const params = new URLSearchParams({
    q: geoInput.value,
    format: 'json',
  });

  const url = `${baseUrl}?${params.toString()}`;

  fetch(url)
    .then(response => response.json())
    .then(data => {
      if (data && data.length > 0) {
        const { lat, lon } = data[0];
        lonLatInput.value = lat + ', ' + lon;
        lonLatSearchFunction();
        
      } else {
        lonLatInput.value = 'ERROR'
      }
    })
    .catch(error => {
      //console.error('Geocoding failed:', error);
      callback(null);
    });
}

function clearContoursFunction()
{
    ContourLayer.getSource().clear();
}

function changeContourColor()
{
    //var color = contourColorSelect.value;
    var newStyle = new Style({
        stroke: new Stroke({
            color: contourColorSelect.value,
            width: 1
        }),
        fill: new Fill({
            color: 'rgba(0, 0, 0, 0)'
        })
    });

    ContourLayer.setStyle(newStyle);
}



downloadButton.addEventListener('click', SetupDownload);
cancelDownloadButton.addEventListener('click', CancelDownload);
showGridButton.addEventListener('click', showGrid);
hideGridButton.addEventListener('click', hideGrid);
toggleModelProgress.addEventListener('click', toggleModelProcessLayer)
lonLatSearch.addEventListener('click', lonLatSearchFunction)
geoSearch.addEventListener('click', geoSearchFunction)
clearContoursButton.addEventListener('click', clearContoursFunction)
downloadToLocalDeviceButton.addEventListener('click', downloadToLocalDevice)
//contourColorSelect.addEventListener('change', changeContourColor)