import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../appstate'
import $backend from '../../backend'

import SequenceControl from '../panels/SequenceControl'
import FrameControl from '../panels/FrameControl'

export default class AnalyzeTab extends Component {

  constructor (props) {
    super(props)
    this.state = {
      selectedSequence: null,
      selectedFrame: null,
    }
  }

  render () {
    const store = this.context.store
    return (
      <AppConsumer>
        {({ store }) => (
          <div className='analyze-tab'>
            <SequenceControl tabState={this.state} setTabState={this.setState.bind(this)} />
            <FrameControl tabState={this.state} setTabState={this.setState.bind(this)} />
          </div>
        )}
      </AppConsumer>
    )
  }
}

AnalyzeTab.contextType = AppContext
