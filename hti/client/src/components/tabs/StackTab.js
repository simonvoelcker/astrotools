import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../appstate'
import $backend from '../../backend'
import StackControl from '../panels/StackControl'

export default class StackTab extends Component {

  constructor (props) {
    super(props)
    this.state = {
    }
  }

  render () {
    const store = this.context.store
    return (
      <AppConsumer>
        {({ store }) => (
          <div className='stack-tab'>
            <div className='left-column'>
              <div className='panel frame-view-panel'>
                <img id="image" alt='' src='' />
              </div>
            </div>
            <div className='right-column'>
                <StackControl />
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

StackTab.contextType = AppContext
