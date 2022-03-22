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
    this.refreshSequences()
  }

  refreshSequences () {
    $backend.listSequences().then((response) => {
      this.setState({sequences: response.data})
      this.selectSequence(response.data[0])
    })
  }

  refreshFrames () {
    // Get selection index before refreshing frames list
    const lastFrameIndex = this.state.frames.indexOf(this.state.selectedFrame)
    $backend.listFrames(this.state.selectedSequence.id).then((response) => {
      this.setState({frames: response.data})
      if (response.data.length > 0) {
        // If the old index is still valid, keep it. Else clamp to last.
        const index = Math.min(lastFrameIndex, response.data.length-1)
        this.selectFrame(response.data[index])
      } else {
        this.selectFrame(null)
      }
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
                selectSequence={this.selectSequence.bind(this)}
                refresh={this.refreshSequences.bind(this)} />
              <FrameControl
                frames={this.state.frames}
                selectedFrame={this.state.selectedFrame}
                selectFrame={this.selectFrame.bind(this)}
                refresh={this.refreshFrames.bind(this)} />
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

AnalyzeTab.contextType = AppContext
