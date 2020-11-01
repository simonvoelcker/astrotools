import React, { Component } from 'react';
import * as THREE from 'three';
import { OrbitControls } from '../../utils/OrbitControls';
import skymapImage from '../../assets/img/skymap.jpg';
import gridImage from '../../assets/img/grid.png';
import starImage from '../../assets/img/star.png';
import stackedImage from '../../assets/img/13_M101_Galaxy.png';

import $backend from '../../backend'

export default class ThreeDView extends Component {
  componentDidMount() {
    const width = this.mount.clientWidth
    const height = this.mount.clientHeight

    this.scene = new THREE.Scene()

    this.camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000)
    this.camera.position.z = 0.1

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

    // grid and background

    this.scene.add( this.getBackground() )
    this.scene.add( this.getGrid() )

    // stars

    $backend.getStars().then(response => {
        let stars = response.data
        const geometry = this.getStarsGeometry(stars)
        const spriteMap = new THREE.TextureLoader().load(starImage)
        const material = new THREE.MeshBasicMaterial({ map: spriteMap })
        this.scene.add( new THREE.Mesh(geometry, material) )
    })

    // image

    const corners = [
        { ra: 211.1585478725, dec: 54.2492060608 }, // 0,0
        { ra: 211.1606458588, dec: 54.4829486252 }, // 0,930
        { ra: 210.3881586528, dec: 54.2490715344 }, // 1790,0
        { ra: 210.3863435910, dec: 54.4826463763 }, // 1790,930
    ]

    const geometry = this.getImageGeometry(corners, 300)
    const imageTexture = new THREE.TextureLoader().load(stackedImage)
    const material = new THREE.MeshBasicMaterial({ map: imageTexture, side: THREE.DoubleSide })
    this.scene.add( new THREE.Mesh(geometry, material) )

    this.start()
  }

  getImageGeometry (corners, distance) {
    // corners: array of 4 objects with ra, dec
    let vertices = new Array(12)
    let indices = [0, 1, 2, 1, 3, 2]
    let uvs = [0, 0, 0, 1, 1, 0, 1, 1]

    for (let i=0; i<corners.length; i++) {
        // carefully handcrafted coordinate mapping
        const ra = (270.0 + corners[i].ra) / 180.0 * Math.PI
        const dec = - corners[i].dec / 180.0 * Math.PI

        const vertex = this.getVertexFromRaDec(ra, dec, -distance)
        vertices[3*i+0] = vertex.x
        vertices[3*i+1] = vertex.y
        vertices[3*i+2] = vertex.z
    }

    const geometry = new THREE.BufferGeometry()
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3))
    geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2))
    geometry.setIndex(indices)
    return geometry
  }

  getStarsGeometry (stars, distanceMultiplier = 30) {
    let vertices = new Array(12*stars.length)
    let indices = new Array(6*stars.length)
    let uvs = new Array(8*stars.length)

    for (let i=0; i<stars.length; i++) {
        // carefully handcrafted coordinate mapping
        const alpha = (270.0 + stars[i].ra) / 180.0 * Math.PI
        const beta = - stars[i].dec / 180.0 * Math.PI
        const distance = distanceMultiplier * stars[i].mag

        const spriteVertices = this.getStarSpriteVertices(alpha, beta, -distance, 0.5)

        vertices[12*i+0] = spriteVertices[0].x
        vertices[12*i+1] = spriteVertices[0].y
        vertices[12*i+2] = spriteVertices[0].z
        vertices[12*i+3] = spriteVertices[1].x
        vertices[12*i+4] = spriteVertices[1].y
        vertices[12*i+5] = spriteVertices[1].z
        vertices[12*i+6] = spriteVertices[2].x
        vertices[12*i+7] = spriteVertices[2].y
        vertices[12*i+8] = spriteVertices[2].z
        vertices[12*i+9] = spriteVertices[3].x
        vertices[12*i+10] = spriteVertices[3].y
        vertices[12*i+11] = spriteVertices[3].z

        indices[6*i+0] = 4*i
        indices[6*i+1] = 4*i+1
        indices[6*i+2] = 4*i+2
        indices[6*i+3] = 4*i+1
        indices[6*i+4] = 4*i+3
        indices[6*i+5] = 4*i+2

        uvs[8*i+0] = 0
        uvs[8*i+1] = 0
        uvs[8*i+2] = 0
        uvs[8*i+3] = 1
        uvs[8*i+4] = 1
        uvs[8*i+5] = 0
        uvs[8*i+6] = 1
        uvs[8*i+7] = 1
    }

    const geometry = new THREE.BufferGeometry()
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3))
    geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2))
    geometry.setIndex(indices)
    return geometry
  }

  getVertexFromRaDec (ra, dec, distance) {
    let rotateX = new THREE.Matrix4().makeRotationX(dec)
    let rotateY = new THREE.Matrix4().makeRotationY(ra)
    return new THREE.Vector3(0, 0, -distance).applyMatrix4(rotateX).applyMatrix4(rotateY)
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
    let geometry = new THREE.SphereGeometry(size, 36, 18)
    geometry.applyMatrix4(new THREE.Matrix4().makeScale( -1, 1, 1 ))
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

  getShaderGrid () {
    let geometry = new THREE.BoxGeometry(2, 2, 2);
    let material = new THREE.ShaderMaterial({
        side: THREE.DoubleSide,
        vertexShader: document.getElementById('gridVertexShader').textContent,
        fragmentShader: document.getElementById('gridFragmentShader').textContent,
    })
    return new THREE.Mesh(geometry, material)
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
