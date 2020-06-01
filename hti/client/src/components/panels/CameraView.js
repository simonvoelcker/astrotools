import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'

export default class CameraView extends Component {
  render () {
    return (
      <AppConsumer>
        {({ store, mutations, utils }) => (
          <div className='camera-view-panel'>
            <img id="camera-image" alt='' src={utils.imageUrl()} />
          </div>
        )}
      </AppConsumer>
    )
  }
}

CameraView.contextType = AppContext
