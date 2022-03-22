import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../appstate'
import $backend from '../../backend'

import SequenceControl from '../panels/SequenceControl'
import FrameControl from '../panels/FrameControl'
import FrameView from '../panels/FrameView'

export default class AnalyzeTab extends Component {

  constructor (props) {
    super(props)
    this.state = {
      sequences: [],
      selectedSequence: null,
      frames: [],
      selectedFrame: null,
    }
  }

  componentDidMount () {
    $backend.listSequences().then((response) => {
      this.setState({sequences: response.data})
      this.selectSequence(response.data[0])
    })
  }

  selectSequence (sequence) {
    this.setState({selectedSequence: sequence})
    $backend.listFrames(sequence.id).then((response) => {
      this.setState({frames: response.data})
      this.selectFrame(response.data[0])
    })
  }

  selectFrame (frame) {
    this.setState({selectedFrame: frame})
  }

  render () {
    const store = this.context.store
    return (
      <AppConsumer>
        {({ store }) => (
          <div className='analyze-tab'>
            <div className='left-column'>
              <FrameView frame={this.state.selectedFrame} />
            </div>
            <div className='right-column'>
              <SequenceControl
                sequences={this.state.sequences}
                selectedSequence={this.state.selectedSequence}
                selectSequence={this.selectSequence.bind(this)} />
              <FrameControl
                frames={this.state.frames}
                selectedFrame={this.state.selectedFrame}
                selectFrame={this.selectFrame.bind(this)} />
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

AnalyzeTab.contextType = AppContext
