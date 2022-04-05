import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../appstate'
import $backend from '../../backend'
import StackControl from '../panels/StackControl'
import StackedImageView from '../panels/StackedImageView'

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
              <StackedImageView stackedImageHash={store.stackedImageHash} />
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
