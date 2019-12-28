var config = {
	'baseUrl': 'http://www.simonvoelcker.de/panoramaviewer/images/',
	'albums': [
		{
			'name': 'Atelier',
			'prefix': 'atelier',
			'images': [
				// runtime type check settles this
				{
					'color': 'atelier_hdr_dreieck.jpg',
					'oid': 'atelier_hdr_dreieck.oids.png'
				},
				'atelier_light.jpg',
				'fxcenter.jpg',
				'atelier_hdr.jpg',
				'pano4_equi.png'
			],
			'objects_by_id': {
				0x00ff0000:	{
					'name': 'Hag Capisco Drehstuhl',
					'center': new THREE.Vector3(-0.6307973986209384, 0.5027212303113293, -0.5910719131267281),
					'fov': 110.0
				},
				0x000000ff:	{
					'name': 'Tinkturenpresse',
					'center': new THREE.Vector3(0.8934373356868359, 0.4409230578582554, -0.08577053252561155),
					'fov': 80.0
				},
				0x00ff00ff: {
					'name': 'Bildhauerschürze',
					'center': new THREE.Vector3(0.7601213597881036, 0.15663490848625633, 0.6306195555462684),
					'fov': 90.0
				},
				0x0000ff00: {
					'name': 'Weinspalier',
					'center': new THREE.Vector3(0.7123378720041629, -0.026278970686410278, 0.7013445457178816),
					'fov': 90.0
				}
			}
		},{
			'name': 'Office',
			'prefix': 'office',
			'images': [
				'PANO_20151118_125436.jpg']
		},{
			'name': 'Other',
			'prefix': 'other',
			'images': [
				'zimmer4.jpg'
			]
		},{
			'name': 'Schweden1',
			'prefix': 'sweden1',
			'images': [
				'PANO_20150801_091258.jpg',
				'PANO_20150731_211945.jpg',
				'PANO_20150801_120207.jpg',
				'PANO_20150731_182532.jpg',
				'PANO_20150801_152308.jpg',
				'PANO_20150731_211500.jpg',
				'PANO_20150801_091829.jpg',
				'PANO_20150730_210333.jpg']
		},{
			'name': 'Schweden2',
			'prefix': 'sweden2',
			'images': [
				'PANO_20150907_151629.jpg',
				'PANO_20150911_155252.jpg',
				'PANO_20150912_153928.jpg',
				'PANO_20150907_155233.jpg',
				'PANO_20150912_103813.jpg',
				'PANO_20150912_154211.jpg',
				'PANO_20150907_185049.jpg',
				'PANO_20150912_141129.jpg',
				'PANO_20150910_160712.jpg',
				'PANO_20150912_144608.jpg']
		},{
			'name': 'Potsdam',
			'prefix': 'potsdam',
			'images': [
				'PANO_20150420_193349.jpg',
				'PANO_20150511_182242.jpg',
				'PANO_20150904_193306.jpg',
				'PANO_20150422_183904.jpg',
				'PANO_20150519_144833.jpg',
				'PANO_20150506_185338.jpg',
				'PANO_20150603_104607.jpg']
		}
	]
}

var settings = {
	// defaults
	'high-quality': false,
	'fish-eye-mode': false,
	'selected-album': config['albums'][0]
}

var objectFromId = function(oid) {
    if (oid == null) return null;
    var objectMap = settings['selected-album']['objects_by_id'];
    if (objectMap === undefined) return null;
    var object = objectMap[oid]
    if (object === undefined) return null;
    return object;
}

var handleUrlParams = function(params) {
	for (var i=0; i<params.length; i++) {
		var kvp = params[i].split('=');
		if (kvp.length == 2 && kvp[0] == 'album') {
			selectAlbumByName(kvp[1]);			
		}
	}
}

var selectAlbumByName = function(name) {
	for (var i=0; i<config['albums'].length; i++) {
		if (config['albums'][i]['name'] == name) {
			settings['selected-album'] = config['albums'][i];
			break;
		}
	}
}
