function PanoramaView(textureUrl) {

	this.geometry = new THREE.SphereGeometry( 500, 60, 40 );
	this.geometry.applyMatrix(new THREE.Matrix4().makeScale( -1, 1, 1 ));
	this.mesh = new THREE.Mesh( this.geometry, null );
    this.selectedObjectId = null;
}

PanoramaView.prototype.loadTextures = function(url, oidUrl, onAllLoaded) {

    if (oidUrl == null) {
        this.texture = THREE.ImageUtils.loadTexture(url, THREE.UVMapping, onAllLoaded);
        this.oidTexture = null;
        this.useMaterial( this.createSimpleTextureMaterial() );
    } else {
        var numToLoad = 2;
        var onOneLoaded = function() {
            numToLoad--;
            if (numToLoad == 0) {
                onAllLoaded();
            }
        }
        this.texture = THREE.ImageUtils.loadTexture(url, THREE.UVMapping, onOneLoaded);
        this.oidTexture = THREE.ImageUtils.loadTexture(oidUrl, THREE.UVMapping, onOneLoaded);
        this.useMaterial( this.createSimpleTextureMaterial() );
    }
}

PanoramaView.prototype.useMaterial = function(material) {

	this.mesh.material = material;
}

PanoramaView.prototype.createSimpleTextureMaterial = function() {

	return new THREE.MeshBasicMaterial( { map: this.texture	} );
}

PanoramaView.prototype.createHighlightObjectMaterial = function(objectId) {
    
    var highlightColor = new THREE.Vector3(0.3, 0.3, 1.0);
    var highlightIntensity = 0.6;

    return new THREE.ShaderMaterial( {
        uniforms: {
            texture: { type: "t", value: this.texture },
            oidTexture: { type: "t", value: this.oidTexture },
            objectId: { type: "v3", value: objectId },
            highlight: { type: "v3", value: highlightColor },
            intensity: { type: "f", value: highlightIntensity }
        },
        attributes: {},
        vertexShader: document.getElementById('vertexShader').text,
        fragmentShader: document.getElementById('fragmentShader').text
    } );
}

PanoramaView.prototype.selectObject = function(objectId) {

    if (this.selectedObjectId == objectId) return;

    if (objectId != null) {
        this.useMaterial(this.createHighlightObjectMaterial(objectId));
    } else {
        this.useMaterial(this.createSimpleTextureMaterial());
    }
    this.selectedObjectId = objectId;
}

PanoramaView.prototype.selectPoint = function(point) {

    if (this.oidTexture == null) return;

    // let d be a non-normalized direction vector pointing at point
    var d = new THREE.Vector3().copy(point).sub(this.mesh.position);
    // calculate angles
    var angles = this.calculateAnglesFromDirection(d);

    var u = angles["azimuth"] / (2.0*Math.PI);
    var v = 0.5 - angles["altitude"] / Math.PI;
    var c = this.getColorFromTexture(u, v, this.oidTexture);

    var oidVector = (c[3] == 255) ? new THREE.Vector3(c[0]/255.0, c[1]/255.0, c[2]/255.0) : null;
    this.selectObject(oidVector);

    var oid = (c[3] == 255) ? c[0] << 16 | c[1] << 8 | c[2] : null;
    return oid;
}

// TODO cachedContext vs texture parameter. either remove parameter or cache using a dict
// TODO also, time caching behavior
PanoramaView.prototype.getColorFromTexture = function(u, v, texture) {

    if (texture.image === undefined) return null;

    if (this.cachedContext === undefined) {
        var canvas = document.createElement( 'canvas' );
        canvas.width = texture.image.width;
        canvas.height = texture.image.height;

        this.cachedContext = canvas.getContext( '2d' );
        this.cachedContext.drawImage( texture.image, 0, 0 );
    }

    var x = Math.round(texture.image.width * u);
    var y = Math.round(texture.image.height * v);
    var color = this.cachedContext.getImageData( x, y, 1, 1 ).data;

    return color;
}

PanoramaView.prototype.calculateAnglesFromDirection = function(d) {
    // catch altitude special cases
    if (d.x == 0.0 && d.z == 0.0) {
    	if (d.y == 0.0) {
    		// null vector case: safe fallback
    		return { altitude: 0.0, azimuth: 0.0 };
    	} else if (d.y < 0.0) {
    		// again save fallback for azimuth
    		return { altitude: -Math.PI/2.0, azimuth: 0.0 };
    	} else {
    		// again save fallback for azimuth
    		return { altitude: +Math.PI/2.0, azimuth: 0.0 };
    	}
    }

    var altitude = Math.atan2(d.y, Math.sqrt(d.x*d.x + d.z*d.z));

    // catch azimuth special cases
    if (d.x == 0.0) {
    	if (d.z < 0.0) {
    		return { altitude: altitude, azimuth: -Math.PI/2.0 };
    	} else {
    		return { altitude: altitude, azimuth: +Math.PI/2.0 };
    	}
    }

    var azimuth = Math.atan2(d.z, d.x);			// outputs [-pi;pi]
    if (azimuth < 0.0) azimuth += 2*Math.PI;	// map to [0;2pi]

	return { altitude: altitude, azimuth: azimuth };
}
