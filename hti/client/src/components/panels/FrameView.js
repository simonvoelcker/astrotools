import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../appstate'
import { Input } from 'reactstrap'
import $backend from '../../backend'

export default class FrameView extends Component {

  constructor (props) {
    super(props)
    this.state = {
      frameId: null,
      framePath: null
    }
  }

  render () {
    // worst practice ever: detect prop changes ourselves and run a request in render()
    let newFrameId = null
    if (this.props.frame) {
      newFrameId = this.props.frame.id
    }
    if (newFrameId !== this.state.frameId) {
      if (newFrameId !== null) {
        $backend.getFramePath(newFrameId).then((response) => {
          this.setState({
            frameId: newFrameId,
            framePath: response.data,
          })
        })
      } else {
        this.setState({
          frameId: null,
          framePath: null,
        })
      }
    }

    let imageSource = ""
    if (this.state.framePath !== null) {
      const pathArg = encodeURIComponent(this.state.framePath)
      imageSource = "http://localhost:5000/api/camera/frames?framePath=" + pathArg
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

FrameView.contextType = AppContext
