import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../appstate'
import { Input } from 'reactstrap'
import $backend from '../../backend'

export default class StackedImageView extends Component {

  render () {
    let imageSource = ""

    if (this.props.stackedImageHash !== null) {
      imageSource = "http://localhost:5000/api/stacking/preview/" + this.props.stackedImageHash
    }

    return (
      <AppConsumer>
        {({ store }) => (
          <div className='panel frame-view-panel'>
            <img id="image" alt='' src={imageSource} />
          </div>
        )}
      </AppConsumer>
    )
  }
}

StackedImageView.contextType = AppContext
