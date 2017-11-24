ymaps.ready(function () {

    var LAYER_NAME = 'user#layer',
        MAP_TYPE_NAME = 'user#customMap',
        TILES_PATH = '%TILES_PATH%',
        MAX_ZOOM = %ZOOM_MAX%;

    /**
     * Конструктор, создающий собственный слой.
     */
    var Layer = function () {
        var layer = new ymaps.Layer(TILES_PATH + '/%z/tile-%x-%y.png');
        // Указываем доступный диапазон масштабов для данного слоя.
        layer.getZoomRange = function () {
            return ymaps.vow.resolve([3, 3]);
        };
        // Добавляем свои копирайты.
        layer.getCopyrights = function () {
            return ymaps.vow.resolve('© esemi');
        };
        return layer;
    };
    // Добавляем в хранилище слоев свой конструктор.
    ymaps.layer.storage.add(LAYER_NAME, Layer);

    /**
     * Создадим новый тип карты.
     * MAP_TYPE_NAME - имя нового типа.
     * LAYER_NAME - ключ в хранилище слоев или функция конструктор.
     */
    var mapType = new ymaps.MapType(MAP_TYPE_NAME, [LAYER_NAME]);
    // Сохраняем тип в хранилище типов.
    ymaps.mapType.storage.add(MAP_TYPE_NAME, mapType);

    // Вычисляем размер всех тайлов на максимальном зуме.
    var worldSize = Math.pow(2, MAX_ZOOM) * 256,
        /**
         * Создаем карту, указав свой новый тип карты.
         */
        map = new ymaps.Map('map', {
            center: [worldSize / 2,  worldSize / 2],
            zoom: MAX_ZOOM,
            nativeFullscreen: true,
            controls: ['zoomControl'],
            type: MAP_TYPE_NAME
        }, {
            // Задаем в качестве проекции Декартову.
             projection: new ymaps.projection.Cartesian([[0, 0], [worldSize, worldSize]], [false, false]),
             restrictMapArea: [[0, 0], [worldSize, worldSize]]
        });
});