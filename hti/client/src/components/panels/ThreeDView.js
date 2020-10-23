import React, { Component } from 'react';
import * as THREE from 'three';
import { OrbitControls } from '../../utils/OrbitControls';
import skymapImage from '../../assets/img/skymap.jpg';
import gridImage from '../../assets/img/grid.png';
import starImage from '../../assets/img/star.png';

import $backend from '../../backend'

export default class ThreeDView extends Component {
  componentDidMount() {
    const width = this.mount.clientWidth
    const height = this.mount.clientHeight


    this.scene = new THREE.Scene()

    // ad camera
    this.camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000)
    this.camera.position.z = 0.1

    // add renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true })
    this.renderer.setClearColor('#000000')
    this.renderer.setSize(width, height)
    this.mount.appendChild(this.renderer.domElement)

    this.controls = new OrbitControls( this.camera, this.renderer.domElement );
    this.controls.domElement = this.renderer.domElement;
    this.controls.enablePan = false;
    this.controls.enableZoom = true;
    this.controls.zoomSpeed = 0.5;
    this.controls.rotateSpeed = -0.2;

    // grid

    this.scene.add( this.getBackground() )
    this.scene.add( this.getGrid() )

    // stars (todo: use one vertex buffer, not list of sprites)

    $backend.getStars().then(response => {
        let stars = response.data

        var spriteMap = new THREE.TextureLoader().load(starImage);
        var spriteMaterial = new THREE.SpriteMaterial({ map: spriteMap });

        for (var i=0; i<stars.length; i++) {
            // carefully handcrafted coordinate mapping
            let ra = (180.0 - stars[i].ra) / 180.0 * Math.PI
            let dec = stars[i].dec / 180.0 * Math.PI

            var sprite = new THREE.Sprite(spriteMaterial);
            let distance = 30.0 * stars[i].mag
            sprite.position.x = distance * Math.cos(ra) * Math.cos(dec)
            sprite.position.y = distance * Math.sin(dec)
            sprite.position.z = distance * Math.sin(ra) * Math.cos(dec)
            this.scene.add(sprite);
        }
    })

    this.start()
  }

  getTexturedSphere (size, material) {
    let geometry = new THREE.SphereGeometry(size, 90, 45)
    geometry.applyMatrix(new THREE.Matrix4().makeScale( -1, 1, 1 ))
    return new THREE.Mesh(geometry, material)
  }

  getBackground () {
    let texture = new THREE.TextureLoader().load(skymapImage)

    let material = new THREE.MeshBasicMaterial({
      map: texture,
      transparent: false,
      depthTest: true,
      depthWrite: true,
    })
    return this.getTexturedSphere(600, material)
  }

  getGrid (degPerLine = 10) {
    let texture = new THREE.TextureLoader().load(gridImage)
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.RepeatWrapping;
    texture.repeat.set(360 / degPerLine, 180 / degPerLine)

    let material = new THREE.MeshBasicMaterial({
      map: texture,
      transparent: true,
      depthTest: true,
      depthWrite: false,
    })
    return this.getTexturedSphere(500, material)
  }

  componentWillUnmount() {
    this.stop()
    this.mount.removeChild(this.renderer.domElement)
  }

  start = () => {
    if (!this.frameId) {
      this.frameId = requestAnimationFrame(this.animate)
    }
  }

  stop = () => {
    cancelAnimationFrame(this.frameId)
  }

  animate = () => {
   // this.controls.update(0.001)
   this.renderScene()
   this.frameId = window.requestAnimationFrame(this.animate)
 }

  renderScene = () => {
    this.renderer.render(this.scene, this.camera)
  }

  render () {
    return (
      <div
        style={{ width: '100%', height: '100%' }}
        ref={(mount) => { this.mount = mount }}
      />
    )
  }
}
