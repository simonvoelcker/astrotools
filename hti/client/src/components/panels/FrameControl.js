import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../appstate'
import { Input, Label } from 'reactstrap'
import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';
import $backend from '../../backend'

export default class FrameControl extends Component {

  componentDidMount () {
    document.onkeydown = this.onKeyDown.bind(this)
  }

  componentWillUnmount () {
    document.onkeydown = null
  }

  onKeyDown (event) {
    switch (event.key) {
        case 'ArrowLeft':
            this.previousFrame()
            break;
        case 'ArrowRight':
            this.nextFrame()
            break;
        case 'Delete':
            this.deleteFrame()
            break;
        default:
            break;
    }
  }


  formatFrame (frame) {
    if (this.props.selectedFrame === null) {
      return '-'
    }

    const index = this.props.frames.indexOf(this.props.selectedFrame)
    const count = this.props.frames.length
    return '' + (index+1) + '/' + count
  }

  previousFrame () {
    if (this.props.frames.length > 0) {
      const index = this.props.frames.indexOf(this.props.selectedFrame)
      // wrap around from first to last
      const newIndex = (index+this.props.frames.length-1) % this.props.frames.length
      this.props.selectFrame(this.props.frames[newIndex])
    }
  }

  nextFrame () {
    if (this.props.frames.length > 0) {
      const index = this.props.frames.indexOf(this.props.selectedFrame)
      // wrap around from last to first
      const newIndex = (index+1) % this.props.frames.length
      this.props.selectFrame(this.props.frames[newIndex])
    }
  }

  deleteFrame () {
    $backend.deleteFrame(this.props.selectedFrame.id).then(() => {
      this.props.refresh()
    })
  }

  render () {
    const store = this.context.store
    return (
      <AppConsumer>
        {({ store }) => (
          <div className={'panel frame-control-panel'}>

            <div className='settings-row'>
              <Label className='spaced-text'>Frame</Label>
              <span className='spaced-text'>{this.formatFrame()}</span>
            </div>

            <div className='settings-row'>
              <button
                className='btn'
                disabled={this.props.frames.length === 0}
                onClick={this.previousFrame.bind(this)}>Previous
              </button>
              <button
                className='btn'
                disabled={this.props.frames.length === 0}
                onClick={this.nextFrame.bind(this)}>Next
              </button>
            </div>

            <div className='settings-row'>
              <button
                className='btn'
                disabled={this.props.frames.length === 0}
                onClick={this.deleteFrame.bind(this)}>Delete
              </button>
            </div>

          </div>
        )}
      </AppConsumer>
    )
  }
}

FrameControl.contextType = AppContext
