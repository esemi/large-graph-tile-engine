ymaps.ready(function () {

    var LAYER_NAME = 'user#layer',
        MAP_TYPE_NAME = 'user#customMap',
        TILES_PATH = '%TILES_PATH%',
        MAX_ZOOM = %ZOOM_MAX%;
        MIN_ZOOM = %ZOOM_MIN%;

    /**
     * Конструктор, создающий собственный слой.
     */
    var Layer = function () {
        var layer = new ymaps.Layer(TILES_PATH + '/%z/tile-%x-%y.png');
        // Указываем доступный диапазон масштабов для данного слоя.
        layer.getZoomRange = function () {
            return ymaps.vow.resolve([MIN_ZOOM, MAX_ZOOM]);
        };
        // Добавляем свои копирайты.
        layer.getCopyrights = function () {
            return ymaps.vow.resolve('© esemi');
        };
        return layer;
    };
    ymaps.layer.storage.add(LAYER_NAME, Layer);

    var mapType = new ymaps.MapType(MAP_TYPE_NAME, [LAYER_NAME]);
    ymaps.mapType.storage.add(MAP_TYPE_NAME, mapType);

    // Вычисляем размер всех тайлов на максимальном зуме.
    var worldSize = Math.pow(2, MAX_ZOOM) * %TILE_SIZE%,
        map = new ymaps.Map('map', {
            center: [worldSize / 2,  worldSize / 2],
            zoom: MIN_ZOOM,
            nativeFullscreen: true,
            controls: ['zoomControl'],
            type: MAP_TYPE_NAME
        }, {
             projection: new ymaps.projection.Cartesian([[0, 0], [worldSize, worldSize]], [false, false]),
             restrictMapArea: [[0, 0], [worldSize, worldSize]]
        });
});