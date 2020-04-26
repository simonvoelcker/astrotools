import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'

export default class CameraView extends Component {
  render () {
    return (
      <AppConsumer>
        {({ store }) => (
          <div>
            <img id="camera-image" className='camera-image' alt='' src={store.imageUrl} />
          </div>
        )}
      </AppConsumer>
    )
  }
}

CameraView.contextType = AppContext
