//Here we are declaring the projection object for Web Mercator
var projection = ol.proj.get('EPSG:3857');

//Define Basemap
//Here we are declaring the raster layer as a separate object to put in the map later
var baseLayer = new ol.layer.Tile({
    source: new ol.source.MapQuest({layer: 'osm'})
});

//Define all WMS Sources:
var river =  new ol.source.TileWMS({
        url:'http://geoserver.byu.edu/arcgis/services/Tuscaloosa/Catchment/MapServer/WmsServer?',

        params:{
            LAYERS:"0",
//            FORMAT:"image/png", //Not a necessary line, but maybe useful if needed later
        },
        crossOrigin: 'Anonymous' //This is necessary for CORS security in the browser
        });

//Define all WMS layers
//The gauge layers can be changed to layer.Image instead of layer.Tile (and .ImageWMS instead of .TileWMS) for a single tile
var flood = new ol.layer.Tile({
    source:river
    }); //Thanks to http://jsfiddle.net/GFarkas/tr0s6uno/ for getting the layer working

//Set opacity of layers
flood.setOpacity(0.8);


sources = [river];
layers = [baseLayer, flood];

//Establish the view area. Note the reprojection from lat long (EPSG:4326) to Web Mercator (EPSG:3857)
var view = new ol.View({
        center: [-9730000, 3920000],
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