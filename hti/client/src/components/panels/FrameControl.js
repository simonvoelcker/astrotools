import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../appstate'
import { Input, Label } from 'reactstrap'
import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';
import $backend from '../../backend'

let formatFrame = (frame) => {
  if (frame === null) {
    return '-'
  }
  return '#' + frame.id
}

export default class FrameControl extends Component {

  previousFrame () {
    const index = this.props.frames.indexOf(this.props.selectedFrame)
    this.props.selectFrame(this.props.frames[index-1])
  }

  nextFrame () {
    const index = this.props.frames.indexOf(this.props.selectedFrame)
    this.props.selectFrame(this.props.frames[index+1])
  }

  analyzeFrame () {
  }

  deleteFrame () {
  }

  render () {
    const store = this.context.store
    return (
      <AppConsumer>
        {({ store }) => (
          <div className={'panel frame-control-panel'}>

            <div className='settings-row'>
              <Label className='spaced-text'>Frame</Label>
              <span className='spaced-text'>{formatFrame(this.props.selectedFrame)}</span>
            </div>

            <div className='settings-row'>
              <button
                className='btn'
                disabled={this.props.selectedFrame === this.props.frames[0]}
                onClick={this.previousFrame.bind(this)}>Previous
              </button>
              <button
                className='btn'
                disabled={this.props.selectedFrame === this.props.frames[this.props.frames.length-1]}
                onClick={this.nextFrame.bind(this)}>Next
              </button>
            </div>

            <div className='settings-row'>
              <button
                className='btn'
                disabled={true}
                onClick={this.analyzeFrame.bind(this)}>Analyze
              </button>
              <button
                className='btn'
                disabled={true}
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
