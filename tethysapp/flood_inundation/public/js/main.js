//Here we are declaring the projection object for Web Mercator
var projection = ol.proj.get('EPSG:3857');

//Define Basemap
//Here we are declaring the raster layer as a separate object to put in the map later
var baseLayer = new ol.layer.Tile({
    source: new ol.source.BingMaps({
        key: 'bQu3Ep7QlBGnycbtYHkm~YC02-zt2ntZ-TPL4RotREg~AjlcnqkJmHSlQXzLXs1EV18Ccd5421OxrRFu9V-QJ0BQypTA_Q7NdK654t8FPUtQ',
        imagerySet: 'AerialWithLabels'  // Options 'Aerial', 'AerialWithLabels', 'Road'
        })
});

//Define all WMS Sources:
var subbasin =  new ol.source.TileWMS({
        url:'http://geoserver.byu.edu/arcgis/services/Tuscaloosa/Catchment/MapServer/WmsServer?',
        params:{
           LAYERS:"0",
//            FORMAT:"image/png", //Not a necessary line, but maybe useful if needed later
        },
        crossOrigin: 'Anonymous' //This is necessary for CORS security in the browser
        });

var river =  new ol.source.TileWMS({
        url:'http://geoserver.byu.edu/arcgis/services/Tuscaloosa/Streamlines/MapServer/WmsServer?',
        params:{
           LAYERS:"0",
//            FORMAT:"image/png", //Not a necessary line, but maybe useful if needed later
        },
        crossOrigin: 'Anonymous' //This is necessary for CORS security in the browser
        });

var basin =  new ol.source.TileWMS({
        url:'http://geoserver.byu.edu/arcgis/services/Tuscaloosa/HUC12/MapServer/WmsServer?',
        params:{
           LAYERS:"0",
//            FORMAT:"image/png", //Not a necessary line, but maybe useful if needed later
        },
        crossOrigin: 'Anonymous' //This is necessary for CORS security in the browser
        });

//console.log(FolderName);

var depthmap = new ol.layer.Image({
        source: new ol.source.ImageStatic({
        projection: ol.proj.get('EPSG:4326'),
        imageExtent: [-87.461413, 33.201141, -87.444098, 33.209104],
        url: '/static/flood_inundation/data/InundationLibrary/18228791/12.3m.tif'
//        url: '/static/flood_inundation/data/results/Floodplain_' + FolderName + range_input + '.tif'
        }),
        });


//Define all WMS layers
//The gauge layers can be changed to layer.Image instead of layer.Tile (and .ImageWMS instead of .TileWMS) for a single tile
var catchment = new ol.layer.Tile({
    source:subbasin
    }); //Thanks to http://jsfiddle.net/GFarkas/tr0s6uno/ for getting the layer working

var flowlines = new ol.layer.Tile({
    source:river
    });

var polygon = new ol.layer.Tile({
    source:basin
    });
//Set opacity of layers
catchment.setOpacity(0.8);
polygon.setOpacity(0.6);


sources = [subbasin, river, basin];
layers = [baseLayer, catchment, flowlines, polygon];  //add depthmap back for flood maps

//Establish the view area. Note the reprojection from lat long (EPSG:4326) to Web Mercator (EPSG:3857)
var view = new ol.View({
        center: [-9735000, 3917000],
        projection: projection,
        zoom: 12,
    })

//Declare the map object itself.
var map = new ol.Map({
    target: document.getElementById("map"),
    layers: layers,
    view: view,
});

map.addControl(new ol.control.ZoomSlider());

//This function is ran to set a listener to update the map size when the navigation pane is opened or closed
(function () {
    var target, observer, config;
    // select the target node
    target = $('#app-content-wrapper')[0];

    observer = new MutationObserver(function () {
        window.setTimeout(function () {
            map.updateSize();
        }, 350);
    });

    config = {attributes: true};

    observer.observe(target, config);
}());