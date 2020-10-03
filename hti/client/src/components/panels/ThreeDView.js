import React, { Component } from 'react';
import * as THREE from 'three';
import { OrbitControls } from '../../utils/OrbitControls';
import backgroundImage from '../../assets/img/skymap.jpg';

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
    const gridGeometry = new THREE.SphereGeometry(500, 36, 18)
    const gridMaterial = new THREE.MeshBasicMaterial({ color: '#ffffff', wireframe: true })
    this.scene.add(new THREE.Mesh(gridGeometry, gridMaterial))

    var texture = new THREE.TextureLoader().load(backgroundImage)
    var backgroundGeometry = new THREE.BoxBufferGeometry(200, 200, 200)
    var backgroundMaterial = new THREE.MeshBasicMaterial({ map: texture })
    this.scene.add(new THREE.Mesh(backgroundGeometry, backgroundMaterial))

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
