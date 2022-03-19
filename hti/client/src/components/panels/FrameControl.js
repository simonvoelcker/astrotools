import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../appstate'
import { Input, Label } from 'reactstrap'
import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';
import $backend from '../../backend'

export default class FrameControl extends Component {

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
