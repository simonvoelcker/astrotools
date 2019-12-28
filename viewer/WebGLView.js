function WebGLView() {

    this.camera = null;
    this.controls = null;
    this.scene = null;
    this.renderer = null;
}

WebGLView.prototype.initialize = function(container, width, height) {

    var webGLView = this;
    this.camera = new THREE.PerspectiveCamera(75.0, width / height, 1, 10000);
    this.controls = new THREE.OrbitControls(this.camera, container);
    this.greaterFov = 100.0;
    this.updateFov();

    this.scene = new THREE.Scene();

    this.panoramaView = new PanoramaView();
    this.scene.add( this.panoramaView.mesh );

    // renderer
    this.renderer = new THREE.WebGLRenderer( { antialias: true } );
    this.renderer.setClearColor( 0x000000, 1 );
    this.renderer.setPixelRatio( window.devicePixelRatio );
    this.renderer.setSize( width, height );  

    this.container = container;

    return this.renderer.getContext();
}

WebGLView.prototype.onResize = function(width, height) {

    this.camera.aspect = width / height;
    this.updateFov();
    this.renderer.setSize(width, height);
}

WebGLView.prototype.updateFov = function() {

    this.camera.fov = this.camera.aspect > 1.0 ?
                        this.greaterFov / this.camera.aspect :
                        this.greaterFov;
    this.camera.updateProjectionMatrix();

    // fov * aspect = fovX, rotatespeed = 1 means width = 360°, minus because inside.
    this.controls.rotateSpeed = this.camera.aspect > 1.0 ?
                    - this.camera.fov * this.camera.aspect / 360.0 :
                    - this.camera.fov / 360.0;
}

WebGLView.prototype.animateCameraTo = function(position, target, fov, delay) {

    var webGLView = this;

    if (position != null) {
        new TWEEN.Tween( this.camera.position )
            .to({ x: position.x, y: position.y, z: position.z }, delay)
            .easing(TWEEN.Easing.Sinusoidal.Out)
            .start();
    }

    if (target != null) {
        new TWEEN.Tween( this.controls.target )
            .to({ x: target.x, y: target.y, z: target.z}, delay)
            .onUpdate(function(){
                webGLView.controls.update();
            })
            .onComplete(function(){
                webGLView.controls.update();
            })
            .easing(TWEEN.Easing.Sinusoidal.Out)
            .start();
    }

    if (fov != null) {
        var t0 = { fov: this.greaterFov };
        var t1 = { fov: this.camera.aspect > 1.0 ? fov : fov / this.camera.aspect };
        new TWEEN.Tween(t0)
            .to(t1, delay)
            .onUpdate(function(){
                webGLView.greaterFov = t0.fov;
                webGLView.updateFov();
            })
            .easing(TWEEN.Easing.Sinusoidal.Out)
            .start();
    }
}

WebGLView.prototype.setFishEyeMode = function(enabled) {

    var webGLView = this;

    this.animateCameraTo(
        new THREE.Vector3().copy(this.camera.position).setLength(enabled ? 500 : 1),
        new THREE.Vector3(0,0,0),
        enabled ? 120.0 : 100.0,
        1000
    );
}

WebGLView.prototype.focusObjectById = function(oid) {

    var object = objectFromId(oid);
    if (object != null) {
        if (object['center'] !== undefined && object['fov'] !== undefined) {
            this.animateCameraTo(
                new THREE.Vector3().copy(object['center']),
                new THREE.Vector3(0,0,0),
                object['fov'],
                1000
            );
        }
    } else {
        this.animateCameraTo(null, null, 100.0, 1000);
    }
}

WebGLView.prototype.update = function() {

    if (this.firstFrame === undefined) {
        this.firstFrame = false;
        this.camera.position.set(1,0,0);
        this.controls.target.set(0,0,0);
        this.controls.update();
    }

    TWEEN.update();
}

WebGLView.prototype.render = function() {

    this.renderer.render(this.scene, this.camera);
}

WebGLView.prototype.getIntersectionFromEvent = function(event) {

    var rect = this.container.getBoundingClientRect();
    var vector = new THREE.Vector3();
    vector.set( + ( (event.clientX-rect.left) / rect.width ) * 2 - 1,
                - ( (event.clientY-rect.top) / rect.height ) * 2 + 1,
                0.5 );

    return this.getIntersection(vector);
}

WebGLView.prototype.getIntersection = function(vector) {

    if (Math.abs(vector.x) > 1.0 || Math.abs(vector.y) > 1.0) return;

    vector.unproject(this.camera);

    var raycaster = new THREE.Raycaster();
    raycaster.ray.set(this.camera.position, vector.sub(this.camera.position).normalize());
    var intersects = raycaster.intersectObjects( [this.panoramaView.mesh] );

    if (intersects.length > 0) {
        return intersects[0];
    } else {
        return null;
    }
}