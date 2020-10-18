import React, { Component } from 'react';
import * as THREE from 'three';
import { OrbitControls } from '../../utils/OrbitControls';
import backgroundImage from '../../assets/img/skymap.jpg';
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
    this.controls.enableZoom = false;
    this.controls.rotateSpeed = -0.2;

    // add grid
    // const gridGeometry = new THREE.SphereGeometry(500, 36, 18)
    // const gridMaterial = new THREE.MeshBasicMaterial({ color: '#aaaaaa', wireframe: true })
    // this.scene.add(new THREE.Mesh(gridGeometry, gridMaterial))

    let texture = new THREE.TextureLoader().load(backgroundImage)
    let backgroundGeometry = new THREE.SphereGeometry(600, 36, 18)
    backgroundGeometry.applyMatrix(new THREE.Matrix4().makeScale( -1, 1, 1 ))
    let backgroundMaterial = new THREE.MeshBasicMaterial({ map: texture })
    this.scene.add(new THREE.Mesh(backgroundGeometry, backgroundMaterial))

    $backend.getStars().then(response => {
        let stars = response.data

        var spriteMap = new THREE.TextureLoader().load(starImage);
        var spriteMaterial = new THREE.SpriteMaterial({ map: spriteMap });

        for (var i=0; i<stars.length; i++) {
            // carefully handcrafted coordinate mapping
            let ra = (180.0 - stars[i].ra) / 180.0 * Math.PI
            let dec = stars[i].dec / 180.0 * Math.PI

            var sprite = new THREE.Sprite(spriteMaterial);
            let distance = 20.0 * stars[i].mag
            sprite.position.x = distance * Math.cos(ra) * Math.cos(dec)
            sprite.position.y = distance * Math.sin(dec)
            sprite.position.z = distance * Math.sin(ra) * Math.cos(dec)
            this.scene.add(sprite);
        }
    })

    this.start()
  }

  componentWillUnmount(){
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
        style={{ width: '1180px', height: '600px' }}
        ref={(mount) => { this.mount = mount }}
      />
    )
  }
}
