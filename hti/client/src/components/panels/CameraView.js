import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'

export default class CameraView extends Component {
  constructor (props) {
    super(props)
    this.state = {
    }
  }

  render () {
    return (
      <AppConsumer>
        {({ store }) => (
          <div>
            <img id="camera-image" className='camera-image' alt='' />
          </div>
        )}
      </AppConsumer>
    )
  }
}

CameraView.contextType = AppContext
