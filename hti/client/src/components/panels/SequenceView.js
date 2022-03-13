import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../appstate'
import { Input, Label } from 'reactstrap'
import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';
import $backend from '../../backend'

export default class SequenceView extends Component {
  constructor(props) {
    super(props)
    this.state = {
      sequence: null
    }
  }

  sequenceStr (sequence) {
    if (sequence === null) {
      return '-'
    }
    return '#' + sequence.id + ': ' + sequence.created
  }

  deleteSequence () {
    $backend.deleteSequence(this.state.sequence.id).then(() => {
      let sequences = this.context.store.sequences
      this.setState({sequence: sequences.length > 0 ? sequences[0] : null})
    })
  }

  analyzeSequence () {
  }

  render () {
    const store = this.context.store
    return (
      <AppConsumer>
        {({ store }) => (
          <div className={'panel sequence-view-panel'}>

            <div className='settings-row'>
              <Label className='spaced-text'>Sequence</Label>
              <UncontrolledDropdown>
                <DropdownToggle caret>{this.sequenceStr(this.state.sequence)}</DropdownToggle>
                <DropdownMenu>
                  {store.sequences.map(sequence => {
                    return <DropdownItem key={sequence.id} onClick={() => {this.setState({sequence: sequence})}}>
                      {this.sequenceStr(sequence)}
                    </DropdownItem>
                  })}
                </DropdownMenu>
              </UncontrolledDropdown>
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Name</Label>
              <span className='spaced-text'>{this.state.sequence !== null ? this.state.sequence.name : '-'}</span>
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Camera</Label>
              <span className='spaced-text'>{this.state.sequence !== null ? this.state.sequence.cameraName : '-'}</span>
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Exposure</Label>
              <span className='spaced-text'>{this.state.sequence !== null ? this.state.sequence.exposure : '-'}</span>
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Gain</Label>
              <span className='spaced-text'>{this.state.sequence !== null ? this.state.sequence.gain : '-'}</span>
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Created</Label>
              <span className='spaced-text'>{this.state.sequence !== null ? this.state.sequence.created : '-'}</span>
            </div>

            <div className='settings-row'>
              <button
                className='btn'
                disabled={true}
                onClick={this.analyzeSequence.bind(this)}>Analyze
              </button>
              <button
                className='btn'
                disabled={this.state.sequence === null}
                onClick={this.deleteSequence.bind(this)}>Delete
              </button>
            </div>

          </div>
        )}
      </AppConsumer>
    )
  }
}

SequenceView.contextType = AppContext
