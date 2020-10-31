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

    $backend.getStars().then(response => {
        let stars = response.data

        let indices = []
        let vertices = []
        let uvs = []

        for (var i=0; i<stars.length; i++) {
            // carefully handcrafted coordinate mapping
            let ra = (270.0 + stars[i].ra) / 180.0 * Math.PI
            let dec = - stars[i].dec / 180.0 * Math.PI
            let distance = 30.0 * stars[i].mag

            const spriteVertices = this.getStarSpriteVertices(ra, dec, -distance, 0.5)
            for (let vertex of spriteVertices) {
                vertices = vertices.concat([vertex.x, vertex.y, vertex.z])
            }
            indices = indices.concat([4*i, 4*i+1, 4*i+2, 4*i+1, 4*i+3, 4*i+2])
            uvs = uvs.concat([0, 0, 0, 1, 1, 0, 1, 1])
        }

        const geometry = new THREE.BufferGeometry()
		geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3))
		geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2))
        geometry.setIndex(indices)
        const spriteMap = new THREE.TextureLoader().load(starImage);
        const material = new THREE.MeshBasicMaterial({ map: spriteMap });
        this.scene.add(new THREE.Mesh(geometry, material))
    })

    this.start()
  }

  getStarSpriteVertices (ra, dec, distance, size) {

    let scale = new THREE.Matrix4().makeScale(size, size, 0)
    let translate = new THREE.Matrix4().makeTranslation(0, 0, -distance)
    let rotateX = new THREE.Matrix4().makeRotationX(dec)
    let rotateY = new THREE.Matrix4().makeRotationY(ra)

    let transform = scale.premultiply(translate).premultiply(rotateX).premultiply(rotateY)

    let vertices = [
        new THREE.Vector3(-1, -1, 0),
        new THREE.Vector3(-1, +1, 0),
        new THREE.Vector3(+1, -1, 0),
        new THREE.Vector3(+1, +1, 0),
    ]
    return vertices.map((v) => v.applyMatrix4(transform))
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
