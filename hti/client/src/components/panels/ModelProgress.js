import React, { Component } from 'react'
import BabylonScene from './BabylonScene'
import ReflectivityTexture from '../../assets/textures/sg.png'
import EnvTexture from '../../assets/textures/environment.dds'
import { AppContext, AppConsumer } from '../../context/AppContext'
import * as BABYLON from 'babylonjs'
// eslint-disable-next-line
import * as LOADER from 'babylonjs-loaders' // do NOT remove the loader, it´s used internally as BABYLON.Sceneloader

export default class ModelProgress extends Component {
  constructor (props) {
    super(props)

    this.bBox = null
    this.camera = null
    this.material = null
    this.directionLight = null
    this.scene = null
    this.canvas = null
    this.engine = null
    this.isWebGlSupported = this.checkWebGlSupport()
  }

  componentWillUpdate () {
    if (this.engine !== null) {
      this.engine.resize()
    }
  }

  componentWillUnmount () {
    if (this.engine !== null) {
      this.engine.stopRenderLoop()
      this.engine.unbindAllTextures()
    }
  }

  onSceneMount = (babylonjsElements) => {
    const { canvas, scene, engine } = babylonjsElements
    this.canvas = canvas
    this.scene = scene
    this.engine = engine
    this.initScene(engine)
  }

  onObjectsLoaded = (objects) => {
    let object = objects[0]
    // STLs exported from Blade have invalid vertex normals, must be recomputed (yes.)
    object.createNormals()

    this.bBox = object.getBoundingInfo().boundingBox

    object.translate(BABYLON.Axis.X, -this.bBox.center.x, BABYLON.Space.LOCAL)
    object.translate(BABYLON.Axis.Y, -this.bBox.center.y, BABYLON.Space.LOCAL)
    object.translate(BABYLON.Axis.Z, -this.bBox.center.z, BABYLON.Space.LOCAL)

    let diagBbox = this.bBox.maximum.subtract(this.bBox.minimum).length()
    this.camera.setPosition(new BABYLON.Vector3(0, diagBbox * 0.5, diagBbox * 1.4))
    this.camera.target = object
    this.camera.setTarget(BABYLON.Vector3.Zero())

    object.material = this.material

    this.directionLight.includedOnlyMeshes.push(object)
  }

  cameraArcAnimation (toAlpha) {
    var animCamAlpha = new BABYLON.Animation('animCam', 'alpha', 60,
      BABYLON.Animation.ANIMATIONTYPE_FLOAT,
      BABYLON.Animation.ANIMATIONLOOPMODE_CYCLE)

    var keysAlpha = []
    keysAlpha.push({ frame: 0, value: this.camera.alpha })
    keysAlpha.push({ frame: 2400, value: toAlpha })
    animCamAlpha.setKeys(keysAlpha)

    this.camera.animations.push(animCamAlpha)
    this.scene.beginAnimation(this.camera, 0, 2400, true, 1, function () { })
  }

  checkWebGlSupport = () => {
    try {
      var tempcanvas = document.createElement('canvas')
      var gl = tempcanvas.getContext('webgl') || tempcanvas.getContext('experimental-webgl')
      return gl != null && !!window.WebGLRenderingContext
    } catch (e) {
      return false
    }
  }

  createMaterial = () => {
    let material = new BABYLON.PBRMaterial('pbr', this.scene)
    material.albedoColor = new BABYLON.Color3(0.015, 0.187, 0.1882)
    material.reflectivityColor = new BABYLON.Color3(1.0, 1.0, 1.0)
    material.microSurface = 1.0 // Let the texture controls the value
    material.reflectionTexture = BABYLON.CubeTexture.CreateFromPrefilteredData(EnvTexture, this.scene)
    material.baseColor = new BABYLON.Color3(1.0, 1.0, 1.0)
    material.metallic = 0.55
    material.roughness = 0.44
    material.alpha = 1.0
    material.reflectivityTexture = new BABYLON.Texture(ReflectivityTexture, this.scene)
    material.useMicroSurfaceFromReflectivityMapAlpha = true
    material.environmentIntensity = 0.9
    material.directIntensity = 0.0
    material.indexOfRefraction = 0.52
    // STL does not guarantee any fixed facet orientation, we should support both to be safe.
    material.backFaceCulling = false
    material.sideOrientation = BABYLON.Mesh.DOUBLESIDE
    material.twoSidedLighting = true
    return material
  }

  initScene = (engine) => {
    if (!this.props.stlFileName || !this.scene || !this.canvas) return

    this.scene.clearColor = new BABYLON.Color4(0, 0, 0, 0.0000000000000001)

    this.camera = new BABYLON.ArcRotateCamera('Camera', 0, 1.0, 1, BABYLON.Vector3.Zero(), this.scene)
    this.camera.attachControl(this.canvas, false)

    BABYLON.SceneLoader.ImportMesh(
      null,
      this.context.store.fileServerPath,
      this.props.stlFileName,
      this.scene,
      this.onObjectsLoaded
    )

    let pipeline = new BABYLON.DefaultRenderingPipeline('default', true, this.scene, [this.camera])
    pipeline.fxaaEnabled = true
    pipeline.samples = 4
    pipeline.imageProcessing.contrast = 3.0
    pipeline.imageProcessing.exposure = 1.5

    this.directionLight = new BABYLON.DirectionalLight('*dirLight', new BABYLON.Vector3(0, -0.6, 0.3), this.scene)
    this.directionLight.position = new BABYLON.Vector3(0, 200, 0)

    this.material = this.createMaterial()
    this.cameraArcAnimation(2 * Math.PI)

    engine.runRenderLoop(() => {
      if (this.scene) {
        this.scene.render()
      }
    })
  }

  render () {

    let message = ''
    if (!this.isWebGlSupported) {
      message = 'WebGL is not supported. Preview unavailable.'
    } else {
      if (!this.context.store.jobQueue[0]) {
        message = 'No job in queue.'
      } else if (!this.props.stlFileName) {
        message = 'No preview available.'
      }
    }
    if (this.canvas) {
      this.canvas.style.visibility = message === '' ? 'visible' : 'hidden'
    }

    return (
      <AppConsumer>
        {() => (
          <div className='panel-modelprogress' data-cy='ModelProgress'>
            <div className='centered'>
              {message ?
                <div className='centered-floating spitzmarke'>
                  <h2>{message}</h2>
                </div> :
                <BabylonScene onSceneMount={this.onSceneMount} adaptToDeviceRatio={false} />
              }
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

ModelProgress.contextType = AppContext
