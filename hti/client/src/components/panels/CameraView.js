import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'

export default class CameraView extends Component {
  render () {
    const endpoint = "http://localhost:5000/api/camera/frames?imagePath="
    return (
      <AppConsumer>
        {({ store }) => (
          <div className='panel camera-view-panel'>
            <img id="camera-image" alt='' src={endpoint + encodeURIComponent(store.framePath)} />
          </div>
        )}
      </AppConsumer>
    )
  }
}

CameraView.contextType = AppContext
